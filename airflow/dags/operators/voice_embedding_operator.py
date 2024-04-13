import tempfile
from resemblyzer import preprocess_wav, VoiceEncoder
from airflow.utils.decorators import apply_defaults
from operators.base_custom_operator import BaseCustomOperator

class VoiceEmbeddingOperator(BaseCustomOperator):

    @apply_defaults
    def __init__(
        self,
        *args, **kwargs
    ):
        super().__init__(*args, **kwargs)

    def _process_audio(self, file_path):
        """
        Preprocesses the audio file and generates embeddings.

        Args:
        - file_path (str): Path to the downloaded audio file.

        Returns:
        - np.ndarray: Array of embeddings generated from the audio file.
        """
        # Preprocess the audio file
        wav = preprocess_wav(file_path)

        # Generate embeddings
        encoder = VoiceEncoder()
        embedding = encoder.embed_utterance(wav)
        return embedding

    def _download_file_from_minio(self, context, minio_client, file_path):
        """
        Downloads a file from MinIO to a temporary file.

        Args:
        - context (dict): The execution context.
        - minio_client: MinIO client instance.
        - file_path (str): Path to the file in MinIO.

        Returns:
        - str: Path to the downloaded temporary file.
        """
        try:
            file_data = minio_client.get_object(self.minio_bucket_name, file_path)
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_file_path = temp_file.name
                temp_file.write(file_data.read())
            self._log_to_mongodb(f"Downloaded file '{file_path}' from MinIO to temporary file", context, "INFO")
            return temp_file_path
        except Exception as e:
            error_message = f"Error downloading file '{file_path}' from MinIO: {str(e)}"
            self._log_to_mongodb(error_message, context, "ERROR")
            raise e

    def execute(self, context):
        # Log the start of the execution
        self._log_to_mongodb(f"Starting execution of TranscriptionOperator", context, "INFO")
        # Get the configuration passed to the DAG from the execution context
        dag_run_conf = context['dag_run'].conf

        # Get the user_id from the configuration
        user_id = dag_run_conf['user_id']
        self._log_to_mongodb(f"Received user_id: {user_id}", context, "INFO")

        user_info = self._get_user_info(context, user_id)
        self._log_to_mongodb(f"Retrieved user from MongoDB: {user_id}", context, "INFO")

        # Extract voice_file_id from user information
        voice_file_id = self._get_voice_id_from_user_info(context, user_info)
        self._log_to_mongodb(f"Received voice_file_id: {voice_file_id}", context, "INFO")

        # Get MinIO client
        minio_client = self._get_minio_client(context)
        self._log_to_mongodb(f"Attempting to download file '{voice_file_id}' from MinIO...", context, "INFO")

        # Download the file from MinIO and get the file path
        file_path = self._download_file_from_minio(context, minio_client, voice_file_id)

        # Preprocess the audio file and generate embeddings
        embeddings = self._process_audio(file_path)

        # Log the end of the execution
        self._log_to_mongodb(f"Execution of VoiceEmbeddingOperator completed", context, "INFO")

        return {"user_id": str(user_id), "embeddings": embeddings}
