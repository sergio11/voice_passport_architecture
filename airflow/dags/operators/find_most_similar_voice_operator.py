from operators.base_custom_operator import BaseCustomOperator
from airflow.utils.decorators import apply_defaults
from qdrant_client import QdrantClient

class FindMostSimilarVoiceOperator(BaseCustomOperator):
    """
    Custom Airflow operator to find the most similar voice based on audio embeddings.

    This operator searches for the most similar voice in a given collection using audio embeddings 
    generated from an input audio file. It connects to a QDrant server to perform the search.

    Args:
    - qdrant_uri (str): The URI of the QDrant server.
    - qdrant_api_key (str): The API key for accessing the QDrant server.
    - qdrant_collection (str): The name of the collection in QDrant to search for similar voices.

    Inherits:
    - BaseOperator: The base class for all operators in Airflow.

    Methods:
    - _initialize_qdrant_client(): Initialize the QDrant client with the provided URI and API key.
    - execute(context): Execute the operator, performing the search for the most similar voice.

    Attributes:
    - qdrant_uri (str): The URI of the QDrant server.
    - qdrant_api_key (str): The API key for accessing the QDrant server.
    - qdrant_collection (str): The name of the collection in QDrant to search for similar voices.
    """

    @apply_defaults
    def __init__(
        self,
        qdrant_uri,
        qdrant_api_key,
        qdrant_collection,
        *args, **kwargs
    ):
        """
        Initialize the operator with the required parameters.

        Args:
        - qdrant_uri (str): The URI of the QDrant server.
        - qdrant_api_key (str): The API key for accessing the QDrant server.
        - qdrant_collection (str): The name of the collection in QDrant to search for similar voices.

        Inherits:
        - *args: Additional arguments.
        - **kwargs: Additional keyword arguments.
        """
        super().__init__(*args, **kwargs)
        self.qdrant_uri = qdrant_uri
        self.qdrant_api_key = qdrant_api_key
        self.qdrant_collection = qdrant_collection

    def _initialize_qdrant_client(self):
        """
        Initialize the QDrant client with the provided URI and API key.

        Returns:
        - QdrantClient: An instance of the QDrant client.
        """
        # Initialize QDrant client
        return QdrantClient(url=self.qdrant_uri, api_key=self.qdrant_api_key)

    def execute(self, context):
        """
        Execute the operator, performing the search for the most similar voice.

        Args:
        - context (dict): The context dictionary passed by Airflow.

        Returns:
        - dict: A dictionary containing information about the most similar voice.
        """
        # Log the start of the execution
        self._log_to_mongodb(f"Starting execution of FindMostSimilarVoiceOperator", context, "INFO")
        # Get the configuration passed to the DAG from the execution context
        args = context['task_instance'].xcom_pull(task_ids='generate_voice_embedding_task')
        # Get the user_id and embeddings from the configuration
        voice_file_id = args['voice_file_id']
        embeddings = args['embeddings']

        if voice_file_id is None:
            self._log_to_mongodb("voice_file_id is not defined", context, "ERROR")
            raise ValueError("voice_file_id is not defined")

        if embeddings is None:
            self._log_to_mongodb("embeddings is not defined", context, "ERROR")
            raise ValueError("embeddings is not defined")

        qdrant_client = self._initialize_qdrant_client()
        # Search related embeddings
        results = qdrant_client.search(self.qdrant_collection, embeddings)

        # Get the most similar audio based on the highest score
        most_similar_audio = max(results, key=lambda result: result.score)

        # Log the end of the execution
        self._log_to_mongodb(f"Execution of FindMostSimilarVoiceOperator completed with voice matched id {str(most_similar_audio.id)} and score {most_similar_audio.score}", context, "INFO")

        # Return information about the executed operation
        return {"voice_matched_id": str(most_similar_audio.id)}

       
       
        
        
