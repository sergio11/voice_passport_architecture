from airflow.utils.decorators import apply_defaults
from operators.base_web3_custom_operator import BaseWeb3CustomOperator

class VerifyVoiceIdOperator(BaseWeb3CustomOperator):
  
    @apply_defaults
    def __init__(
        self,
        *args, **kwargs
    ):
        super().__init__(*args, **kwargs)


    def execute(self, context):
        """
        Executes the operator logic to verify the voice ID of the user.

        This method performs the following steps:
        1. Logs the start of the execution.
        2. Retrieves the voice ID from the DAG run configuration.
        3. Finds the user information based on the voice ID.
        4. Connects to the Web3 provider.
        5. Checks if the connection to the Web3 provider is successful.
        6. Loads the contract ABI from MinIO.
        7. Gets an instance of the smart contract using the Web3 provider and contract ABI.
        8. Generates the SHA256 hash of the user ID and voice ID.
        9. Calls the `verifyVoiceID` function of the smart contract to verify the association
        between the user ID and voice ID.
        10. Logs the completion of the operator execution.
        11. Returns information about the executed operation, including the user ID
            and the verification result.

        Args:
        - context (dict): The execution context containing information about the DAG run.

        Returns:
        - dict: A dictionary containing information about the executed operation,
        including the user ID and the verification result.
        """
        # Log the start of the execution
        self._log_to_mongodb(f"Starting execution of VerifyVoiceIdOperator", context, "INFO")
        # Get the user ID from the DAG run configuration
        voice_id = context['dag_run'].conf['voice_matched_id']
        user_info = self._find_user_by_voice_id(voice_id)
        user_id = user_info["_id"]
        # Connect to Web3 provider
        web3 = self._connect_to_web3()
        # Check if the connection to the Web3 provider is successful
        self._check_connection(web3, context)
         # Load the contract ABI from clearthe specified file
        contract_abi = self._load_contract_abi(context)
        # Get an instance of the Smart Contract using the Web3 provider and contract ABI
        contract = self._get_contract_instance(web3, contract_abi)
         # Generate the SHA256 hash of the user ID
        user_id_hash = self._sha256(user_info["_id"])
         # Generate the SHA256 hash of the voice ID
        voice_file_id_hash = self._sha256(voice_id)
        result = contract.functions.verifyVoiceID(user_id_hash, voice_file_id_hash).call() 
        # Log completion of operator execution
        self._log_to_mongodb(f"Execution of VerifyVoiceIdOperator completed", context, "INFO")
        # Return information about the executed operation
        return {"user_id": str(user_id), "verification_result": result}

        
