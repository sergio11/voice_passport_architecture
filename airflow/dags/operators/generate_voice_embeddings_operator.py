from resemblyzer import preprocess_wav, VoiceEncoder
from airflow.utils.decorators import apply_defaults
from operators.base_custom_operator import BaseCustomOperator

class GenerateVoiceEmbeddingsOperator(BaseCustomOperator):
    """
    Custom Airflow operator to generate voice embeddings from audio files.

    This operator preprocesses an audio file, generates embeddings from the audio data, 
    and logs the execution details to MongoDB.

    Inherits:
    - BaseCustomOperator: The base class for custom operators in Airflow.

    Methods:
    - _process_audio(file_path): Preprocess the audio file and generate embeddings.
    - execute(context): Execute the operator, generating embeddings for the provided audio file.

    """
    @apply_defaults
    def __init__(
        self,
        *args, **kwargs
    ):
        """
        Initialize the operator.

        Inherits:
        - *args: Additional arguments.
        - **kwargs: Additional keyword arguments.
        """
        super().__init__(*args, **kwargs)

    def _process_audio(self, file_path):
        """
        Preprocess the audio file and generate embeddings.

        Args:
        - file_path (str): Path to the audio file.

        Returns:
        - np.ndarray: Array of embeddings generated from the audio file.
        """
        # Preprocess the audio file
        wav = preprocess_wav(file_path)

        # Generate embeddings
        encoder = VoiceEncoder()
        embedding = encoder.embed_utterance(wav)
        return embedding

    def execute(self, context):
        """
        Execute the operator, generating embeddings for the provided audio file.

        Args:
        - context (dict): The context dictionary passed by Airflow.

        Returns:
        - dict: A dictionary containing user_id and embeddings.
        """
        # Log the start of the execution
        self._log_to_mongodb(f"Starting execution of GenerateVoiceEmbeddingsOperator", context, "INFO")
        # Get the configuration passed to the DAG from the execution context
        dag_run_conf = context['dag_run'].conf

        # Get the user_id from the configuration
        voice_file_id = dag_run_conf['voice_file_id']
        self._log_to_mongodb(f"Received voice_file_id: {voice_file_id}", context, "INFO")
        self._log_to_mongodb(f"Attempting to download file '{voice_file_id}' from MinIO...", context, "INFO")
        # Download the file from MinIO and get the file path
        file_path = self._download_file_from_minio(context, voice_file_id)

        # Preprocess the audio file and generate embeddings
        embeddings = self._process_audio(file_path)

        # Log the end of the execution
        self._log_to_mongodb(f"Execution of GenerateVoiceEmbeddingsOperator completed", context, "INFO")

        return {"voice_file_id": str(voice_file_id), "embeddings": embeddings}
