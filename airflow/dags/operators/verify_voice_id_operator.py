from airflow.utils.decorators import apply_defaults
import jwt
from operators.base_web3_custom_operator import BaseWeb3CustomOperator
from datetime import datetime, timedelta, timezone

class VerifyVoiceIdOperator(BaseWeb3CustomOperator):
    """
    An operator to verify a user's voice ID using a Smart Contract on the Ethereum blockchain.

    Inherits:
    - BaseWeb3CustomOperator: Base class for Ethereum blockchain interaction operators.

    Parameters:
    - jwt_secret (str): The secret key used for JWT token generation.
    - jwt_duration_hours (int): The duration, in hours, for which the JWT token will be valid.
    - *args: Additional arguments.
    - **kwargs: Additional keyword arguments.
    """
    

    @apply_defaults
    def __init__(
        self,
        jwt_secret,
        jwt_duration_hours,
        *args, **kwargs
    ):
        """
        Initialize the operator.

        Parameters:
        - jwt_secret (str): The secret key used for JWT token generation.
        - jwt_duration_hours (int): The duration, in hours, for which the JWT token will be valid.
        - *args: Additional arguments.
        - **kwargs: Additional keyword arguments.
        """
        super().__init__(*args, **kwargs)
        self.jwt_secret = jwt_secret
        self.jwt_duration_hours = jwt_duration_hours

    def generate_jwt(self, user_id):
        """
        Generate a JWT token with user ID as claim.

        Parameters:
        - user_id (str): The ID of the current authenticated user.

        Returns:
        - str: The generated JWT token.
        """
        token_expiry = datetime.now(timezone.utc) + timedelta(hours=self.jwt_duration_hours)
        token_payload = {'user_id': user_id, 'exp': token_expiry}
        jwt_token = jwt.encode(token_payload, self.jwt_secret, algorithm='HS256')
        return jwt_token

    def execute(self, context):
        """
        Execute the operator.

        Parameters:
        - context (dict): The execution context.

        Returns:
        - dict: The result of the operator execution.
        """
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

        if result:
            # Generate session token
            session_token = self.generate_jwt(user_id)
            result = {"result": {
                "type": "authentication",
                "isSuccess": True, 
                "session_token": session_token,
                "user_id": user_id
            }}
        else:
            result = {
                "type": "authentication",
                "isSuccess": False
            }

        # Log completion of operator execution
        self._log_to_mongodb(f"Execution of VerifyVoiceIdOperator completed", context, "INFO")
        # Return information about the executed operation
        return {"result": result}

        
