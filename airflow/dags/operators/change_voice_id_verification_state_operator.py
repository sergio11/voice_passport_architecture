from operators.base_web3_custom_operator import BaseWeb3CustomOperator
from airflow.utils.decorators import apply_defaults

class ChangeVoiceIdVerificationStateOperator(BaseWeb3CustomOperator):
    """
    Operator for changing the verification state of a voice ID in a blockchain smart contract.

    Inherits from BaseWeb3CustomOperator.

    Args:
    - *args: Variable length argument list.
    - **kwargs: Arbitrary keyword arguments.

    Raises:
    - ValueError: If 'user_id' parameter is empty or None, or if 'is_enabled' parameter is not a boolean.
    - Exception: If there's an error during the ABI retrieval process, transaction building, or transaction execution.

    Returns:
    - dict: Information about the executed operation, including user ID and result.
    """
    @apply_defaults
    def __init__(
        self,
        *args, **kwargs
    ):
        """
        Initializes the ChangeVoiceIdVerificationStateOperator.

        Args:
        - *args: Variable length argument list.
        - **kwargs: Arbitrary keyword arguments.
        """
        super().__init__(*args, **kwargs)

    def execute(self, context):
        """
        Executes the operator to change the verification state of a voice ID in the blockchain smart contract.

        Args:
        - context (dict): The context containing information about the DAG run.

        Returns:
        - dict: Information about the executed operation, including user ID and result.

        Raises:
        - ValueError: If 'user_id' parameter is empty or None, or if 'is_enabled' parameter is not a boolean.
        - Exception: If there's an error during the ABI retrieval process, transaction building, or transaction execution.
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
        return {"user_id": str(user_id), "result": {
            "type": "change_state",
            "result": result, 
            "user_id": str(user_id)
        }}
