import json
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from web3.middleware import geth_poa_middleware
from web3 import Web3
import hashlib

class RegisterVoiceIDOperator(BaseOperator):
    """
    Operator to register a VoiceID by interacting with a Smart Contract on the blockchain.
    """
    @apply_defaults
    def __init__(
        self,
        http_provider,
        caller_address,
        caller_private_key,
        contract_address,
        *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.http_provider = http_provider
        self.caller_address = caller_address
        self.caller_private_key = caller_private_key
        self.contract_address = contract_address

    def _sha256(data):
        hash_object = hashlib.sha256(data.encode())
        return hash_object.hexdigest()

    def _log_transaction_details(self, tx_receipt, context):
        """
        Log transaction details.
        """
        self._log_to_mongodb(f"Transaction hash: {tx_receipt.transactionHash}", context, "INFO")
        self._log_to_mongodb(f"Gas used: {tx_receipt.gasUsed}", context, "INFO")
        status = 'Success' if tx_receipt.status == 1 else 'Failed'
        self._log_to_mongodb(f"Status: {status}", context, "INFO")

    def _connect_to_web3(self):
        """
        Connect to Web3 provider.
        """
        web3 = Web3(Web3.HTTPProvider(self.http_provider))
        web3.middleware_onion.inject(geth_poa_middleware, layer=0)  # Inject the middleware
        return web3

    def _check_connection(self, web3, context):
        """
        Check if connection to Web3 provider is successful.
        """
        if web3.is_connected():
            self._log_to_mongodb("Connection Successful", context, "INFO")
        else:
            self._log_to_mongodb("Connection Failed", context, "ERROR")
            raise Exception("Failed to connect to Web3 provider")

    def _get_chain_id(self, web3):
        """
        Get chain ID.
        """
        return web3.eth.chain_id

    def _get_nonce(self, web3):
        """
        Get address nonce.
        """
        return web3.eth.get_transaction_count(self.caller_address)

    def _load_contract_abi(self):
        """
        Load contract ABI from file.
        """
        with open(self.contract_abi) as f:
            return json.load(f)

    def _get_contract_instance(self, web3, contract_abi):
        """
        Get contract instance.
        """
        return web3.eth.contract(address=self.contract_address, abi=contract_abi)

    def _register_voice_id(self, web3, contract, user_id_hash, voice_file_id_hash, chain_id, nonce):
        """
        Register VoiceID with contract.
        """
        tx_data = contract.functions.registerVoiceIDVerification(user_id_hash, voice_file_id_hash).build_transaction({
            "chainId": chain_id, 
            "from": self.caller_address, 
            "nonce": nonce
        })
        signed_tx = web3.eth.account.sign_transaction(tx_data, private_key=self.caller_private_key)
        return web3.eth.send_raw_transaction(signed_tx.rawTransaction)

    def execute(self, context):
        """
        Execute operator logic.
        
        Parameters:
        - context (dict): Execution context containing information about the DAG run.
        
        Returns:
        - dict: A dictionary containing information about the executed operation.
        """
        # Log the start of the execution
        self._log_to_mongodb(f"Starting execution of RegisterVoiceIDOperator", context, "INFO")
        
        # Connect to Web3 provider
        web3 = self._connect_to_web3()
        
        # Check if the connection to the Web3 provider is successful
        self._check_connection(web3, context)
        
        # Get the chain ID from the connected Web3 provider
        chain_id = self._get_chain_id(web3)
        
        # Get the transaction nonce for the caller address
        nonce = self._get_nonce(web3)
        
        # Load the contract ABI from the specified file
        contract_abi = self._load_contract_abi()
        
        # Get an instance of the Smart Contract using the Web3 provider and contract ABI
        contract = self._get_contract_instance(web3, contract_abi)
        
        # Get the user ID from the DAG run configuration
        user_id = context['dag_run'].conf['user_id']
        
        # Generate the SHA256 hash of the user ID
        user_id_hash = self._sha256(user_id)
        
        # Retrieve user information based on the user ID from MongoDB
        user_info = self._get_user_info(context, user_id)
        
        # Extract the voice file ID from the user information
        voice_file_id = self._get_voice_id_from_user_info(context, user_info)
        
        # Generate the SHA256 hash of the voice file ID
        voice_file_id_hash = self._sha256(voice_file_id)
        
        try:
            # Register the voice ID on the Smart Contract and get the transaction hash
            tx_hash = self._register_voice_id(web3, contract, user_id_hash, voice_file_id_hash, chain_id, nonce)
            
            # Wait for the transaction receipt
            tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
            
            # Log transaction details
            self._log_transaction_details(tx_receipt, context)
            
            # Log completion of operator execution
            self._log_to_mongodb(f"Execution of RegisterVoiceIDOperator completed", context, "INFO")
            
            # Return information about the executed operation
            return {"user_id": str(user_id)}
        
        except Exception as e:
            # Log any errors that occur during execution
            self._log_to_mongodb(f"Error: {str(e)}", context, "ERROR")
            # Raise the exception to be handled by Airflow
            raise

        
