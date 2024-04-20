import json
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from web3.middleware import geth_poa_middleware
from web3 import Web3
import hashlib

class ChangeVoiceIdVerificationStateOperator(BaseOperator):
    """
    Operator for changing the verification state of a user's voice ID 
    in a smart contract on the Ethereum blockchain.

    :param http_provider: HTTP provider URL for the Ethereum node.
    :type http_provider: str
    :param caller_address: Ethereum address of the caller.
    :type caller_address: str
    :param caller_private_key: Private key of the caller for signing transactions.
    :type caller_private_key: str
    :param contract_address: Ethereum address of the smart contract.
    :type contract_address: str
    :param contract_abi: Name of the file containing the contract ABI stored in MinIO.
    :type contract_abi: str
    """

    @apply_defaults
    def __init__(
        self,
        http_provider,
        caller_address,
        caller_private_key,
        contract_address,
        contract_abi,
        *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.http_provider = http_provider
        self.caller_address = caller_address
        self.caller_private_key = caller_private_key
        self.contract_address = contract_address
        self.contract_abi = contract_abi

    def _sha256(self, data):
        """
        Calculate the SHA256 hash of the input data.

        :param data: Input data to be hashed.
        :type data: str
        :return: Hexadecimal representation of the SHA256 hash.
        :rtype: str
        """
        hash_object = hashlib.sha256(data.encode())
        return hash_object.hexdigest()

    def _connect_to_web3(self):
        """
        Connect to the Web3 provider.

        :return: Web3 instance connected to the specified provider.
        :rtype: Web3
        """
        web3 = Web3(Web3.HTTPProvider(self.http_provider))
        web3.middleware_onion.inject(geth_poa_middleware, layer=0)  # Inject the middleware
        return web3

    def _check_connection(self, web3, context):
        """
        Check if connection to the Web3 provider is successful.

        :param web3: Web3 instance connected to the provider.
        :type web3: Web3
        :param context: Context dictionary containing additional information.
        :type context: dict
        :raises Exception: If connection to the Web3 provider fails.
        """
        if web3.is_connected():
            self._log_to_mongodb("Connection Successful", context, "INFO")
        else:
            self._log_to_mongodb("Connection Failed", context, "ERROR")
            raise Exception("Failed to connect to Web3 provider")
    
    def _load_contract_abi(self, context):
        """
        Loads the ABI (Application Binary Interface) of the smart contract from MinIO.

        :param context: Context containing MinIO connection details.
        :type context: dict
        :return: Contract ABI loaded from MinIO.
        :rtype: dict
        :raises Exception: If there's an error during the ABI retrieval process.
        """
        try:
            minio_client = self._get_minio_client(context)
            response = minio_client.get_object(self.minio_bucket_name, self.contract_abi)
            contract_abi_json = response.read()
            contract_abi = json.loads(contract_abi_json)
            return contract_abi
        except Exception as e:
            error_message = f"Error retrieving file '{self.contract_abi}' from MinIO: {e}"
            raise Exception(error_message)

    def _get_contract_instance(self, web3, contract_abi):
        """
        Get an instance of the smart contract.

        :param web3: Web3 instance connected to the provider.
        :type web3: Web3
        :param contract_abi: ABI of the smart contract.
        :type contract_abi: dict
        :return: Instance of the smart contract.
        :rtype: Contract
        """
        return web3.eth.contract(address=self.contract_address, abi=contract_abi)
    
    def _get_chain_id(self, web3):
        """
        Get the chain ID of the Ethereum network.

        :param web3: Web3 instance connected to the provider.
        :type web3: Web3
        :return: Chain ID of the Ethereum network.
        :rtype: int
        """
        return web3.eth.chain_id

    def _get_nonce(self, web3):
        """
        Get the nonce (transaction count) for the caller's address.

        :param web3: Web3 instance connected to the provider.
        :type web3: Web3
        :return: Nonce for the caller's address.
        :rtype: int
        """
        return web3.eth.get_transaction_count(self.caller_address)
    
    def _log_transaction_details(self, tx_receipt, context):
        """
        Log details of the transaction.

        :param tx_receipt: Receipt of the transaction.
        :type tx_receipt: dict
        :param context: Context dictionary containing additional information.
        :type context: dict
        """
        self._log_to_mongodb(f"Transaction hash: {tx_receipt.transactionHash}", context, "INFO")
        self._log_to_mongodb(f"Gas used: {tx_receipt.gasUsed}", context, "INFO")
        status = 'Success' if tx_receipt.status == 1 else 'Failed'
        self._log_to_mongodb(f"Status: {status}", context, "INFO")

    def execute(self, context):
        """
        Execute the operator.

        :param context: Context dictionary containing additional information.
        :type context: dict
        :return: Dictionary containing information about the executed operation.
        :rtype: dict
        """
        # Log the start of the execution
        self._log_to_mongodb(f"Starting execution of ChangeVoiceIdVerificationState", context, "INFO")
        # Get the user ID from the DAG run configuration
        dag_run = context['dag_run']
        user_id = dag_run.conf['user_id']
        if not user_id:
            raise ValueError("The 'user_id' parameter cannot be empty or None.")
        
        is_enabled = dag_run.conf['is_enabled']
        if not isinstance(is_enabled, bool):
            raise ValueError("The 'is_enabled' parameter must be a boolean.")
        # Connect to Web3 provider
        web3 = self._connect_to_web3()
        # Check if the connection to the Web3 provider is successful
        self._check_connection(web3, context)
         # Load the contract ABI from clearthe specified file
        contract_abi = self._load_contract_abi(context)
        # Get an instance of the Smart Contract using the Web3 provider and contract ABI
        contract = self._get_contract_instance(web3, contract_abi)
        # Generate the SHA256 hash of the user ID
        user_id_hash = self._sha256(user_id)
        
        # Get chain ID and nonce
        chain_id = self._get_chain_id(web3)
        nonce = self._get_nonce(web3)

        # Build contract function call
        if is_enabled:
            contract_call = contract.functions.enableVoiceIDVerification(user_id_hash)
        else:
            contract_call = contract.functions.disableVoiceIDVerification(user_id_hash)

        # Build and send transaction
        tx_data = contract_call.build_transaction({
            "chainId": chain_id, 
            "from": self.caller_address, 
            "nonce": nonce
        })
        signed_tx = web3.eth.account.sign_transaction(tx_data, private_key=self.caller_private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

        # Log transaction details
        self._log_transaction_details(tx_receipt, context)

        # Log completion of operator execution
        self._log_to_mongodb(f"Execution of ChangeVoiceIdVerificationState completed", context, "INFO")
        result = tx_receipt['status'] == 1
        # Return information about the executed operation
        return {"user_id": str(user_id), "result": result}
