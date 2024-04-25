import hashlib
import json
from airflow.utils.decorators import apply_defaults
from operators.base_custom_operator import BaseCustomOperator
from web3.middleware import geth_poa_middleware
from web3 import Web3

class BaseWeb3CustomOperator(BaseCustomOperator):
    """
    Base class for custom operators interacting with Web3 blockchain networks.

    Attributes:
    - http_provider (str): HTTP provider URL for the Web3 connection.
    - caller_address (str): Ethereum address of the caller.
    - caller_private_key (str): Private key of the caller.
    - contract_address (str): Address of the smart contract to interact with.
    - contract_abi (str): Filename of the contract's Application Binary Interface (ABI) stored in MinIO.
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
        """
        Initialize the BaseWeb3CustomOperator.

        Args:
        - http_provider (str): HTTP provider URL for the Web3 connection.
        - caller_address (str): Ethereum address of the caller.
        - caller_private_key (str): Private key of the caller.
        - contract_address (str): Address of the smart contract to interact with.
        - contract_abi (str): Filename of the contract's Application Binary Interface (ABI) stored in MinIO.
        - mongo_uri (str): MongoDB URI.
        - mongo_db (str): MongoDB database name.
        - mongo_db_collection (str): MongoDB collection name.
        - minio_endpoint (str): MinIO endpoint URL.
        - minio_access_key (str): MinIO access key.
        - minio_secret_key (str): MinIO secret key.
        - minio_bucket_name (str): Name of the MinIO bucket where the contract ABI file is stored.
        """
        super().__init__(*args, **kwargs)
        self.http_provider = http_provider
        self.caller_address = caller_address
        self.caller_private_key = caller_private_key
        self.contract_address = contract_address
        self.contract_abi = contract_abi

    def _sha256(self, data):
        hash_object = hashlib.sha256(str(data).encode())
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
            self._log_to_mongodb("web3 connection opened successfully", context, "INFO")
        else:
            self._log_to_mongodb("web3 connection Failed", context, "ERROR")
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