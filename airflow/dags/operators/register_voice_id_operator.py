import json
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from web3 import Web3
import hashlib

class RegisterVoiceIDOperator(BaseOperator):
    """
    Operator to register VoiceID using a Smart Contract.
    """

    @apply_defaults
    def __init__(
        self,
        contract_address,
        contract_abi,
        http_provider,
        *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.contract_address = contract_address
        self.contract_abi = contract_abi
        self.http_provider = http_provider

    def _sha256(data):
        hash_object = hashlib.sha256(data.encode())
        return hash_object.hexdigest()
    
    def _register_voice_id(self, contract, user_id_hash, voice_file_id_hash):
        tx_hash = contract.functions.registerVoiceID(user_id_hash, voice_file_id_hash).transact()
        return tx_hash

    def _log_transaction_details(self, tx_receipt, context):
        self._log_to_mongodb(f"Transaction hash: {tx_receipt.transactionHash}", context, "INFO")
        self._log_to_mongodb(f"Gas used: {tx_receipt.gasUsed}", context, "INFO")
        status = 'Success' if tx_receipt.status == 1 else 'Failed'
        self._log_to_mongodb(f"Status: {status}", context, "INFO")

    def execute(self, context):
        # Log the start of the execution
        self._log_to_mongodb(f"Starting execution of RegisterVoiceIDOperator", context, "INFO")
        # Get the configuration passed to the DAG from the execution context
        dag_run_conf = context['dag_run'].conf
        # Get the user_id and embeddings from the configuration
        user_id = dag_run_conf['user_id']
        self._log_to_mongodb(f"Received user_id: {user_id}", context, "INFO")

        user_info = self._get_user_info(context, user_id)
        self._log_to_mongodb(f"Retrieved user from MongoDB: {user_id}", context, "INFO")

        # Extract voice_file_id from user information
        voice_file_id = self._get_voice_id_from_user_info(context, user_info)
        self._log_to_mongodb(f"Received voice_file_id: {voice_file_id}", context, "INFO")

        web3 = Web3(Web3.HTTPProvider(self.http_provider))
        with open(self.contract_abi) as f:
            contract_abi = json.load(f)
        contract = web3.eth.contract(address=self.contract_address, abi=contract_abi)

        user_id_hash = self._sha256(user_id)
        voice_file_id_hash = self._sha256(voice_file_id)

        tx_hash = self._register_voice_id(contract, user_id_hash, voice_file_id_hash)
        tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)

        self._log_transaction_details(tx_receipt, context)
        self._log_to_mongodb(f"Execution of RegisterVoiceIDOperator completed", context, "INFO")
        return {"user_id": str(user_id)}

        
