from airflow.utils.decorators import apply_defaults
from operators.base_web3_custom_operator import BaseWeb3CustomOperator

class RegisterVoiceIDOperator(BaseWeb3CustomOperator):
    """
    Operator for registering a voice ID in a blockchain smart contract.

    Inherits from BaseWeb3CustomOperator.

    Args:
    - *args: Variable length argument list.
    - **kwargs: Arbitrary keyword arguments.

    Raises:
    - Exception: If there's an error during the transaction building or execution.

    Returns:
    - dict: Information about the executed operation, including user ID.
    """

    @apply_defaults
    def __init__(
        self,
        *args, **kwargs
    ):
        """
        Initializes the RegisterVoiceIDOperator.

        Args:
        - *args: Variable length argument list.
        - **kwargs: Arbitrary keyword arguments.
        """
        super().__init__(*args, **kwargs)

    def _register_voice_id(self, web3, contract, user_id_hash, voice_file_id_hash, chain_id, nonce):
        """
        Register VoiceID with contract.

        Args:
        - web3 (Web3): The Web3 provider.
        - contract (Contract): The instance of the Smart Contract.
        - user_id_hash (str): The SHA256 hash of the user ID.
        - voice_file_id_hash (str): The SHA256 hash of the voice file ID.
        - chain_id (int): The chain ID.
        - nonce (int): The transaction nonce.

        Returns:
        - str: The transaction hash.
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
        
        # Load the contract ABI from clearthe specified file
        contract_abi = self._load_contract_abi(context)
        
        # Get an instance of the Smart Contract using the Web3 provider and contract ABI
        contract = self._get_contract_instance(web3, contract_abi)
        
        # Get the voice file ID from the DAG run configuration
        voice_file_id = context['dag_run'].conf['voice_file_id']
        # Generate the SHA256 hash of the voice file ID
        voice_file_id_hash = self._sha256(voice_file_id)
        # Generate the SHA256 hash of the user ID
        user_info = self._find_user_by_voice_id(voice_file_id)
        user_id = user_info["_id"]
        user_id_hash = self._sha256(user_id)

        # Register the voice ID on the Smart Contract and get the transaction hash
        tx_hash = self._register_voice_id(web3, contract, user_id_hash, voice_file_id_hash, chain_id, nonce)
            
        # Wait for the transaction receipt
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
            
        # Log transaction details
        self._log_transaction_details(tx_receipt, context)
            
        # Log completion of operator execution
        self._log_to_mongodb(f"Execution of RegisterVoiceIDOperator completed", context, "INFO")
            
        # Return information about the executed operation
        return {"user_id": user_id, "result": {
            "type": "identity_registration",
            "result": True, 
            "user_id": str(user_id)
        }}

        
