from datetime import datetime
from airflow import DAG
import importlib
import os

# Define default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
    'logging_level': 'INFO'
}

# Create the DAG with the specified default arguments
with DAG('voice_id_change_state_dag', default_args=default_args, default_view="graph", schedule_interval=None, catchup=False) as dag:
    # Import the necessary operators from external modules
    operators_module = importlib.import_module('operators.change_voice_id_verification_state_operator')
    ChangeVoiceIdVerificationStateOperator = operators_module.ChangeVoiceIdVerificationStateOperator
    operators_module = importlib.import_module('operators.process_result_webhook_operator')
    ProcessResultWebhookOperator = operators_module.ProcessResultWebhookOperator

    # Define the task instances for each operator

    # Task to change the verification state of a voice ID
    change_voice_id_verification_state_task = ChangeVoiceIdVerificationStateOperator(
        task_id='change_voice_id_verification_state_task',
        mongo_uri=os.environ.get("MONGO_URI"),
        mongo_db=os.environ.get("MONGO_DB"),
        mongo_db_collection=os.environ.get("MONGO_DB_COLLECTION"),
        minio_endpoint=os.environ.get("MINIO_ENDPOINT"),
        minio_access_key=os.environ.get("MINIO_ACCESS_KEY"),
        minio_secret_key=os.environ.get("MINIO_SECRET_KEY"),
        minio_bucket_name=os.environ.get("MINIO_BUCKET_NAME"),
        http_provider=os.environ.get("VOICE_ID_VERIFIER_HTTP_PROVIDER"),
        caller_address=os.environ.get("VOICE_ID_VERIFIER_CALLER_ADDRESS"),
        caller_private_key=os.environ.get("VOICE_ID_VERIFIER_CALLER_PRIVATE_KEY"),
        contract_address=os.environ.get("VOICE_ID_VERIFIER_CONTRACT_ADDRESS"),
        contract_abi=os.environ.get("VOICE_ID_VERIFIER_CONTRACT_ABI_NAME")
    )

    # Task to process the result of changing the verification state and send it to a webhook
    process_result_webhook_task = ProcessResultWebhookOperator(
        task_id='process_result_webhook_task',
        mongo_uri=os.environ.get("MONGO_URI"),
        mongo_db=os.environ.get("MONGO_DB"),
        mongo_db_collection=os.environ.get("MONGO_DB_COLLECTION"),
        minio_endpoint=os.environ.get("MINIO_ENDPOINT"),
        minio_access_key=os.environ.get("MINIO_ACCESS_KEY"),
        minio_secret_key=os.environ.get("MINIO_SECRET_KEY"),
        minio_bucket_name=os.environ.get("MINIO_BUCKET_NAME")
    )

    # Define task dependencies by chaining the tasks in sequence
    change_voice_id_verification_state_task >> process_result_webhook_task