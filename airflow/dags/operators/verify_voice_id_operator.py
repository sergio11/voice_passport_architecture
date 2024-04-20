import json
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from web3.middleware import geth_poa_middleware
from web3 import Web3
import hashlib

class VerifyVoiceIdOperator(BaseOperator):
    """
    Operator to verify the voice ID of a user by interacting with a smart contract on the blockchain.

    This operator connects to a Web3 provider, loads the contract ABI from MinIO,
    and then interacts with the smart contract to verify the association between
    the user ID and the voice ID.

    Args:
    - http_provider (str): The HTTP provider URL for the Web3 connection.
    - caller_address (str): The address of the caller account for interacting with the smart contract.
    - caller_private_key (str): The private key of the caller account for signing transactions.
    - contract_address (str): The address of the smart contract on the blockchain.
    - contract_abi (str): The name of the ABI file containing the smart contract's interface.

    Attributes:
    - http_provider (str): The HTTP provider URL for the Web3 connection.
    - caller_address (str): The address of the caller account for interacting with the smart contract.
    - caller_private_key (str): The private key of the caller account for signing transactions.
    - contract_address (str): The address of the smart contract on the blockchain.
    - contract_abi (str): The name of the ABI file containing the smart contract's interface.

    Methods:
    - _sha256(data): Generates the SHA256 hash of the input data.
    - _connect_to_web3(): Connects to the Web3 provider using the specified HTTP provider URL.
    - _check_connection(web3, context): Checks if the connection to the Web3 provider is successful.
    - _load_contract_abi(context): Loads the ABI of the smart contract from MinIO.
    - _get_contract_instance(web3, contract_abi): Returns an instance of the smart contract.
    - execute(context): Executes the operator logic to verify the voice ID of the user.

    Raises:
    - Exception: If there's an error during the ABI retrieval process or connecting to the Web3 provider.

    Returns:
    - dict: A dictionary containing information about the executed operation, including the user ID
      and the verification result.
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
        hash_object = hashlib.sha256(data.encode())
        return hash_object.hexdigest()

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
    
    def _load_contract_abi(self, context):
        """
        Loads the ABI (Application Binary Interface) of the smart contract from MinIO.

        Args:
        - context (dict): The context containing MinIO connection details.

        Returns:
        - bytes: The binary data of the contract ABI file.

        Raises:
        - Exception: If there's an error during the ABI retrieval process.
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
        Get contract instance.
        """
        return web3.eth.contract(address=self.contract_address, abi=contract_abi)

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

        
