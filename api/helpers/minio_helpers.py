import os
import uuid
from minio import Minio

# MinIO configuration
MINIO_ENDPOINT = os.environ.get("MINIO_ENDPOINT")
MINIO_ACCESS_KEY = os.environ.get("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.environ.get("MINIO_SECRET_KEY")
MINIO_BUCKET_NAME = os.environ.get("MINIO_BUCKET_NAME")

# Function to handle MinIO storage for the file
def handle_minio_storage(temp_file_path):
    # Generate a unique name for the file in MinIO using UUID
    unique_filename = str(uuid.uuid4())
    # Store the video file in MinIO
    _store_file_in_minio(
        minio_endpoint=MINIO_ENDPOINT,
        minio_access_key=MINIO_ACCESS_KEY,
        minio_secret_key=MINIO_SECRET_KEY,
        minio_bucket_name=MINIO_BUCKET_NAME,
        local_file_path=temp_file_path,
        minio_object_name=unique_filename
    )
    return unique_filename

def get_file_from_minio(minio_object_name):
    """
    Retrieves a file from MinIO based on its object name.

    Args:
    - minio_object_name (str): The name of the object in MinIO.

    Returns:
    - bytes: The binary data of the file if it exists in MinIO.

    Raises:
    - Exception: If there's an error during the MinIO file retrieval process.
    """
    try:
        # Get MinIO client
        minio_client = _get_minio_client(
            minio_endpoint=MINIO_ENDPOINT,
            minio_access_key=MINIO_ACCESS_KEY,
            minio_secret_key=MINIO_SECRET_KEY,
            minio_bucket_name=MINIO_BUCKET_NAME
        )
        # Retrieve the file from MinIO
        response = minio_client.get_object(MINIO_BUCKET_NAME, minio_object_name)
        # Read and return the file data
        file_data = response.read()
        return file_data
    except Exception as e:
        error_message = f"Error retrieving file '{minio_object_name}' from MinIO: {e}"
        raise Exception(error_message)

def _get_minio_client(minio_endpoint, minio_access_key, minio_secret_key, minio_bucket_name):
    """
    Establishes a connection with MinIO and returns a MinIO client.

    Args:
    - minio_endpoint (str): The endpoint URL of the MinIO server.
    - minio_access_key (str): The access key for MinIO.
    - minio_secret_key (str): The secret key for MinIO.
    - minio_bucket_name (str): The name of the MinIO bucket.

    Returns:
    - Minio: A MinIO client instance.

    Raises:
    - Exception: If there's an error while connecting to MinIO.
    """
    try:
        minio_client = Minio(
            endpoint=minio_endpoint,
            access_key=minio_access_key,
            secret_key=minio_secret_key,
            secure=False
        )
        bucket_exists = minio_client.bucket_exists(minio_bucket_name)
        if not bucket_exists:
            minio_client.make_bucket(minio_bucket_name)
        return minio_client
    except Exception as e:
        error_message = f"Error connecting to MinIO: {e}"
        raise Exception(error_message)
        
def _store_file_in_minio(minio_endpoint, minio_access_key, minio_secret_key, minio_bucket_name, local_file_path, minio_object_name, content_type=None):
    """
    Stores a file in MinIO.

    Args:
    - minio_endpoint (str): The endpoint URL of the MinIO server.
    - minio_access_key (str): The access key for MinIO.
    - minio_secret_key (str): The secret key for MinIO.
    - minio_bucket_name (str): The name of the MinIO bucket.
    - local_file_path (str): The local path to the file to be stored in MinIO.
    - minio_object_name (str): The name to be used for the object in MinIO.
    - content_type (str, optional): The content type of the object to be stored in MinIO.

    Raises:
    - Exception: If there's an error during the MinIO file storage process.
    """
    try:
        with open(local_file_path, 'rb') as file_data:
            file_data.seek(0, 2)
            file_size_bytes = file_data.tell()
            file_data.seek(0)
            if file_size_bytes == 0:
                error_message = f"File '{local_file_path}' is empty"
                raise Exception(error_message)
            # Get MinIO client
            minio_client = _get_minio_client(minio_endpoint, minio_access_key, minio_secret_key, minio_bucket_name)
            minio_client.put_object(
                bucket_name=minio_bucket_name,
                object_name=minio_object_name,
                data=file_data,
                length=file_size_bytes,
                content_type=content_type
            )
    except Exception as e:
        error_message = f"Error storing file '{local_file_path}' - {minio_object_name} in MinIO: {e}"
        raise Exception(error_message)