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
with DAG('voice_authentication_dag', default_args=default_args, default_view="graph", schedule_interval=None, catchup=False) as dag:
    # Import the necessary operators from external modules
    operators_module = importlib.import_module('operators.generate_voice_embeddings_operator')
    GenerateVoiceEmbeddingsOperator = operators_module.GenerateVoiceEmbeddingsOperator
    operators_module = importlib.import_module('operators.find_most_similar_voice_operator')
    FindMostSimilarVoiceOperator = operators_module.FindMostSimilarVoiceOperator
    operators_module = importlib.import_module('operators.verify_voice_id_operator')
    VerifyVoiceIdOperator = operators_module.VerifyVoiceIdOperator
    operators_module = importlib.import_module('operators.process_result_webhook_operator')
    ProcessResultWebhookOperator = operators_module.ProcessResultWebhookOperator

    # Define the task instances for each operator

    # Task to extract voice embeddings from audio file
    generate_voice_embedding_task = GenerateVoiceEmbeddingsOperator(
        task_id='generate_voice_embedding_task',
        mongo_uri=os.environ.get("MONGO_URI"),
        mongo_db=os.environ.get("MONGO_DB"),
        mongo_db_collection=os.environ.get("MONGO_DB_COLLECTION"),
        minio_endpoint=os.environ.get("MINIO_ENDPOINT"),
        minio_access_key=os.environ.get("MINIO_ACCESS_KEY"),
        minio_secret_key=os.environ.get("MINIO_SECRET_KEY"),
        minio_bucket_name=os.environ.get("MINIO_BUCKET_NAME")
    )

    # Task to find the most similar voice embeddings
    find_most_similar_voice_task = FindMostSimilarVoiceOperator(
        task_id='find_most_similar_voice_task',
        mongo_uri=os.environ.get("MONGO_URI"),
        mongo_db=os.environ.get("MONGO_DB"),
        mongo_db_collection=os.environ.get("MONGO_DB_COLLECTION"),
        minio_endpoint=os.environ.get("MINIO_ENDPOINT"),
        minio_access_key=os.environ.get("MINIO_ACCESS_KEY"),
        minio_secret_key=os.environ.get("MINIO_SECRET_KEY"),
        minio_bucket_name=os.environ.get("MINIO_BUCKET_NAME"),
        qdrant_uri=os.environ.get("QDRANT_URI"),
        qdrant_api_key=os.environ.get("QDRANT_API_KEY"),
        qdrant_collection=os.environ.get("QDRANT_COLLECTION"),
    )

    # Task to verify the identity using voice authentication
    verify_voice_id_task = VerifyVoiceIdOperator(
        task_id='verify_voice_id_task',
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
        contract_abi=os.environ.get("VOICE_ID_VERIFIER_CONTRACT_ABI_NAME"),
        jwt_secret=os.environ.get("JWT_SECRET_KEY"),
        jwt_duration_hours=os.environ.get("JWT_DURATION_HOURS_KEY")
    )
    
    # Task to process the result and send it to a webhook
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
    generate_voice_embedding_task >> find_most_similar_voice_task >> verify_voice_id_task >> process_result_webhook_task
