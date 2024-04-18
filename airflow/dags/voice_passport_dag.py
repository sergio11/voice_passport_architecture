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
with DAG('voice_passport_dag', default_args=default_args, default_view="graph", schedule_interval=None, catchup=False) as dag:
    # Import the necessary operators from external modules
    operators_module = importlib.import_module('operators.voice_embedding_operator')
    VoiceEmbeddingOperator = operators_module.VoiceEmbeddingOperator
    operators_module = importlib.import_module('operators.qdrant_embeddings_operator')
    QDrantEmbeddingsOperator = operators_module.QDrantEmbeddingsOperator
    operators_module = importlib.import_module('operators.register_voice_id_operator')
    RegisterVoiceIDOperator = operators_module.RegisterVoiceIDOperator

    # Define the task instances for each operator

    # Define the task to extract voice embeddings from audio file
    voice_embedding_task = VoiceEmbeddingOperator(
        task_id='voice_embedding_task',
        qdrant_uri=os.environ.get("MONGO_URI"),
        qdrant_api_key=os.environ.get("MONGO_URI"),
        qdrant_collection=os.environ.get("MONGO_URI"),
        mongo_uri=os.environ.get("MONGO_URI"),
        mongo_db=os.environ.get("MONGO_DB"),
        mongo_db_collection=os.environ.get("MONGO_DB_COLLECTION"),
        minio_endpoint=os.environ.get("MINIO_ENDPOINT"),
        minio_access_key=os.environ.get("MINIO_ACCESS_KEY"),
        minio_secret_key=os.environ.get("MINIO_SECRET_KEY"),
        minio_bucket_name=os.environ.get("MINIO_BUCKET_NAME")
    )

    # Define the task to upsert the extracted voice embeddings into QDrant for similarity search
    qdrant_embeddings_task = QDrantEmbeddingsOperator(
        task_id='qdrant_embeddings_task',
        mongo_uri=os.environ.get("MONGO_URI"),
        mongo_db=os.environ.get("MONGO_DB"),
        mongo_db_collection=os.environ.get("MONGO_DB_COLLECTION"),
        minio_endpoint=os.environ.get("MINIO_ENDPOINT"),
        minio_access_key=os.environ.get("MINIO_ACCESS_KEY"),
        minio_secret_key=os.environ.get("MINIO_SECRET_KEY"),
        minio_bucket_name=os.environ.get("MINIO_BUCKET_NAME")
    )

    # Define a task to register a VoiceID using a Smart Contract.
    register_voice_task = RegisterVoiceIDOperator(
        task_id='register_voice_task',
        http_provider=os.environ.get("VOICE_ID_VERIFIER_HTTP_PROVIDER"),
        caller_address=os.environ.get("VOICE_ID_VERIFIER_CALLER_ADDRESS"),
        caller_private_key=os.environ.get("VOICE_ID_VERIFIER_CALLER_PRIVATE_KEY"),
        contract_address=os.environ.get("VOICE_ID_VERIFIER_CONTRACT_ADDRESS"),
        contract_abi=os.environ.get("VOICE_ID_VERIFIER_CONTRACT_ABI_NAME"),
        mongo_uri=os.environ.get("MONGO_URI"),
        mongo_db=os.environ.get("MONGO_DB"),
        mongo_db_collection=os.environ.get("MONGO_DB_COLLECTION"),
        minio_endpoint=os.environ.get("MINIO_ENDPOINT"),
        minio_access_key=os.environ.get("MINIO_ACCESS_KEY"),
        minio_secret_key=os.environ.get("MINIO_SECRET_KEY"),
        minio_bucket_name=os.environ.get("MINIO_BUCKET_NAME")
    )

    # Define task dependencies by chaining the tasks in sequence
    voice_embedding_task >> qdrant_embeddings_task >> register_voice_task
