from airflow.utils.decorators import apply_defaults
from operators.base_custom_operator import BaseCustomOperator
from qdrant_client import QdrantClient, http

class QDrantEmbeddingsOperator(BaseCustomOperator):
    """
    Custom Apache Airflow operator for upserting voice embeddings into the QDrant vector database.
    
    :param qdrant_uri: The URI of the QDrant service.
    :type qdrant_uri: str
    :param qdrant_api_key: The API key for authentication with the QDrant service.
    :type qdrant_api_key: str
    :param qdrant_collection: The name of the collection in which the embeddings will be upserted.
    :type qdrant_collection: str
    """

    @apply_defaults
    def __init__(
        self,
        qdrant_uri,
        qdrant_api_key,
        qdrant_collection,
        *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.qdrant_uri = qdrant_uri
        self.qdrant_api_key = qdrant_api_key
        self.qdrant_collection = qdrant_collection

    def _initialize_qdrant_client(self):
        """
        Initialize the QDrant client with the provided URI and API key.
        
        :return: Initialized QDrant client.
        """
        # Initialize QDrant client
        return QdrantClient(url=self.qdrant_uri, api_key=self.qdrant_api_key)

    def _create_or_verify_collection(self, client):
        """
        Create or verify the existence of the specified collection in QDrant.
        
        :param client: Initialized QDrant client.
        """
        # Get collections response
        collections_response = client.get_collections()
        # Extract collection names
        collection_names = [collection.name for collection in collections_response.collections]
        print(collection_names)
        if self.qdrant_collection not in collection_names:
            # Create a collection with specified parameters
            vectors_config = http.models.VectorParams(
                size=256,  # Size required for embeddings from resemblyzer
                distance=http.models.Distance.COSINE
            )
            client.create_collection(self.qdrant_collection, vectors_config)
            
    def _upsert_embeddings(self, client, id, embeddings):
        """
        Upsert the provided embeddings into the specified collection in QDrant.
        
        :param client: Initialized QDrant client.
        :param id: Unique identifier for the embeddings.
        :param embeddings: List of voice embeddings.
        """
        # Upsert embeddings into the collection
        client.upsert(self.qdrant_collection, [{"id": id, "vector": embeddings.tolist()}])

    def execute(self, context):
       """
        Execute the QDrant operator.
        
        :param context: Task execution context.
        :return: Dictionary containing the voice file ID.
       """
       # Log the start of the execution
       self._log_to_mongodb(f"Starting execution of QDrantOperator", context, "INFO")
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

       self._log_to_mongodb(f"Received voice_file_id: {voice_file_id}", context, "INFO")
       try:
            # Initialize QDrant client
            client = self._initialize_qdrant_client()

            # Create or verify the existence of the collection
            self._create_or_verify_collection(client)

            # Upsert embeddings into the collection
            self._upsert_embeddings(client, voice_file_id, embeddings)
            # Log success
            self._log_to_mongodb(f"Embeddings successfully upserted into QDrant", context, "INFO")
       except Exception as e:
            # Log error if any
            error_message = f"Error while upserting embeddings into QDrant: {str(e)}"
            self._log_to_mongodb(error_message, context, "ERROR")
            raise e
       # Log the end of the execution
       self._log_to_mongodb(f"Execution of QDrantOperator completed", context, "INFO")
       return {"voice_file_id": str(voice_file_id)}
