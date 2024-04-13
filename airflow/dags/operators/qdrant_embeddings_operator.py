from airflow.utils.decorators import apply_defaults
from operators.base_custom_operator import BaseCustomOperator
import qdrant_client

class QDrantEmbeddingsOperator(BaseCustomOperator):

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
        # Initialize QDrant client
        return qdrant_client.QdrantClient(url=self.qdrant_uri, api_key=self.qdrant_api_key)

    def _create_or_verify_collection(self, client):
        # Check if the collection already exists
        collections = client.list_collections()
        if self.qdrant_collection not in collections:
            # Create a collection with specified parameters
            vectors_config = qdrant_client.http.models.VectorParams(
                size=256,  # Size required for embeddings from resemblyzer
                distance=qdrant_client.http.models.Distance.COSINE
            )
            client.create_collection(self.qdrant_collection, vectors_config)

    def _upsert_embeddings(self, client, embeddings):
        # Upsert embeddings into the collection
        client.upsert(self.qdrant_collection, embeddings)

    def execute(self, context):
       # Log the start of the execution
       self._log_to_mongodb(f"Starting execution of QDrantOperator", context, "INFO")
       # Get the configuration passed to the DAG from the execution context
       dag_run_conf = context['dag_run'].conf
       # Get the user_id and embeddings from the configuration
       user_id = dag_run_conf['user_id']
       self._log_to_mongodb(f"Received user_id: {user_id}", context, "INFO")
       embeddings = dag_run_conf['embeddings']
       try:
            # Initialize QDrant client
            client = self._initialize_qdrant_client()

            # Create or verify the existence of the collection
            self._create_or_verify_collection(client)

            # Upsert embeddings into the collection
            self._upsert_embeddings(client, embeddings)

            # Log success
            self._log_to_mongodb(f"Embeddings successfully upserted into QDrant", context, "INFO")
       except Exception as e:
            # Log error if any
            error_message = f"Error while upserting embeddings into QDrant: {str(e)}"
            self._log_to_mongodb(error_message, context, "ERROR")
            raise e
       # Log the end of the execution
       self._log_to_mongodb(f"Execution of QDrantOperator completed", context, "INFO")
       return {"user_id": str(user_id)}
