import tempfile
from bson import ObjectId
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from pymongo import MongoClient
from minio import Minio
from datetime import datetime

class BaseCustomOperator(BaseOperator):
    
    @apply_defaults
    def __init__(
        self,
        mongo_uri,
        mongo_db,
        mongo_db_collection,
        minio_endpoint,
        minio_access_key,
        minio_secret_key,
        minio_bucket_name,
        *args, **kwargs
    ):
        """
        Initialize a custom base operator for common functionality.

        :param mongo_uri: The URI for the MongoDB connection.
        :param mongo_db: The name of the MongoDB database.
        :param mongo_db_collection: The name of the MongoDB collection.
        :param minio_endpoint: The MinIO server endpoint.
        :param minio_access_key: The access key for MinIO.
        :param minio_secret_key: The secret key for MinIO.
        :param minio_bucket_name: The name of the MinIO bucket.
        """
        super().__init__(*args, **kwargs)
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.mongo_db_collection = mongo_db_collection
        self.minio_endpoint = minio_endpoint
        self.minio_access_key = minio_access_key
        self.minio_secret_key = minio_secret_key
        self.minio_bucket_name = minio_bucket_name

    def _get_mongodb_collection(self, collection_name=None):
        """
        Private method to securely obtain a reference to the MongoDB collection.

        Args:
            collection_name (str, optional): The name of the MongoDB collection to retrieve. If not provided, the default collection is used.

        Returns:
            pymongo.collection.Collection: A reference to the desired MongoDB collection.
        """
        client = MongoClient(self.mongo_uri)
        db = client[self.mongo_db]
        
        if collection_name:
            return db[collection_name]
        else:
            return db[self.mongo_db_collection]

    def _log_to_mongodb(self, message, context, log_level):
        """
        Log a message to a MongoDB collection.

        :param message: The message to be logged.
        :param context: The execution context.
        :param log_level: The log level (e.g., INFO, ERROR).
        """
        task_instance = context['task_instance']
        task_instance_id = f"{task_instance.dag_id}.{task_instance.task_id}"
        current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_document = {
            "task_instance_id": task_instance_id,
            "log_level": log_level,
            "timestamp": current_timestamp,
            "log_message": message
        }
        client = MongoClient(self.mongo_uri)
        db = client[self.mongo_db]
        try:
            db.dags_execution_logs.insert_one(log_document)
            print("Log message registered in MongoDB")
        except Exception as e:
            print(f"Error writing log message to MongoDB: {e}")

    def _get_minio_client(self, context):
        """
        Get a MinIO client for interacting with MinIO.

        :param context: The execution context.

        :return: A MinIO client instance.
        """
        try:
            self._log_to_mongodb(f"MinIO Endpoint: {self.minio_endpoint}  Bucket Name: {self.minio_bucket_name}", context, "INFO")
            self._log_to_mongodb(f"Access Key: {self.minio_access_key}", context, "INFO")
            self._log_to_mongodb("Connecting to MinIO...", context, "INFO")
            minio_client = Minio(
                self.minio_endpoint,
                access_key=self.minio_access_key,
                secret_key=self.minio_secret_key,
                secure=False
            )
            bucket_exists = minio_client.bucket_exists(self.minio_bucket_name)
            if not bucket_exists:
                self._log_to_mongodb(f"Bucket '{self.minio_bucket_name}' does not exist; creating...", context, "INFO")
                minio_client.make_bucket(self.minio_bucket_name)
            self._log_to_mongodb(f"Connected to MinIO and bucket '{self.minio_bucket_name}' exists", context, "INFO")
            return minio_client

        except Exception as e:
            error_message = f"Error connecting to MinIO: {e}"
            self._log_to_mongodb(error_message, context, "ERROR")
            raise Exception(error_message)
        
    def _get_user_info(self, context, user_id):
        # Get a reference to the MongoDB collection
        collection = self._get_mongodb_collection()

        # Retrieve meeting information from MongoDB based on user_id
        user_info = collection.find_one({"_id": ObjectId(user_id)})
        if user_info is None:
            error_message = f"User with ID {user_id} not found in MongoDB"
            self._log_to_mongodb(error_message, context, "ERROR")
            raise Exception(error_message)

        self._log_to_mongodb(f"Retrieved user from MongoDB: {user_id}", context, "INFO")
        return user_info
    
    def _get_voice_id_from_user_info(self, context, user_info):
        """
        Retrieves the user information and extracts the voice_file_id.

        Args:
        - context: The execution context.
        - user_info: The user information

        Returns:
        The voice_file_id from the user information.
        """
        file_id = user_info.get('voice_file_id')
        if not file_id:
            error_message = f"No 'file_id' found in the user information."
            self._log_to_mongodb(error_message, context, "ERROR")
            raise Exception(error_message)
        return file_id
    
    def _find_user_by_voice_id(self, voice_id):
        """
        Find user details by voice ID.

        Parameters:
        - voice_id (str): The voice ID of the user to search for.

        Returns:
        - dict or None: A dictionary containing the user details if found, or None if not found.
        """
        # Get a reference to the MongoDB collection
        collection = self._get_mongodb_collection()
        user_info = collection.find_one({"voice_id": voice_id})  # Find user details by voice ID
        return user_info
    
    def _download_file_from_minio(self, context, file_path):
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
            # Get MinIO client
            minio_client = self._get_minio_client(context)
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