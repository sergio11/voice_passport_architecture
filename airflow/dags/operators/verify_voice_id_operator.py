from airflow.utils.decorators import apply_defaults
import jwt
from operators.base_web3_custom_operator import BaseWeb3CustomOperator
from datetime import datetime, timedelta, timezone

class VerifyVoiceIdOperator(BaseWeb3CustomOperator):
    """
    VerifyVoiceIdOperator is responsible for verifying the authenticity of a voice ID using a Smart Contract on the Ethereum blockchain.

    Attributes:
    - jwt_secret (str): The secret key used for JWT token generation.

    Methods:
    - generate_jwt(user_id): Generate a JWT token with user ID as claim.
    - execute(context): Execute the operator to verify the voice ID authenticity.
    """

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
        return jwt_token

    def execute(self, context):
        # Log the start of the execution
        self._log_to_mongodb(f"Starting execution of VerifyVoiceIdOperator", context, "INFO")
        # Get task arguments
        args = context['task_instance'].xcom_pull(task_ids='find_most_similar_voice_task')
        voice_id = args['voice_matched_id']
        
        if voice_id is None:
           self._log_to_mongodb("voice_id is not defined - authentication failed", context, "ERROR")
           return {"result": { "type": "authentication", "result": False}}
        
        user_info = self._find_user_by_voice_id(voice_id)
        user_id = str(user_info["_id"])
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
         # Generate the SHA256 hash of the voice ID
        voice_file_id_hash = self._sha256(voice_id)
        result = contract.functions.verifyVoiceID(user_id_hash, voice_file_id_hash).call() 
        session_token = self.generate_jwt(user_id)
        # Log completion of operator execution
        self._log_to_mongodb(f"Execution of VerifyVoiceIdOperator completed", context, "INFO")
        # Return information about the executed operation
        return {"result": {
            "type": "authentication",
            "result": result, 
            "session_token": session_token,
            "user_id": user_id
        }}

        
