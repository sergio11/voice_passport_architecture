from airflow.utils.decorators import apply_defaults
import jwt
from operators.base_web3_custom_operator import BaseWeb3CustomOperator
from datetime import datetime, timedelta, timezone

class VerifyVoiceIdOperator(BaseWeb3CustomOperator):
  
    @apply_defaults
    def __init__(
        self,
        jwt_secret,
        *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.jwt_secret = jwt_secret

    def generate_jwt(self, user_id):
        """
        Generate a JWT token with user ID as claim.

        Parameters:
        - user_id (str): The ID of the current authenticated user.

        Returns:
        - str: The generated JWT token.
        """
        token_expiry = datetime.now(timezone.utc) + timedelta(hours=1)  # Token expires in 1 hour
        token_payload = {'user_id': user_id, 'exp': token_expiry}
        jwt_token = jwt.encode(token_payload, self.jwt_secret, algorithm='HS256')
        return jwt_token.decode('utf-8') 

    def execute(self, context):
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
        session_token = self.generate_jwt(user_id)
        # Log completion of operator execution
        self._log_to_mongodb(f"Execution of VerifyVoiceIdOperator completed", context, "INFO")
        # Return information about the executed operation
        return {"user_id": user_id, "result": {
            "verification_result": result, 
            "session_token": session_token,
            "user_id": user_id
        }}

        
