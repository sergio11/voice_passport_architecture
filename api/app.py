from flask import Flask, request, jsonify
import logging
import os
from minio_helpers import get_minio_client, store_file_in_minio
from api_helpers import create_response, allowed_file

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get Airflow DAG ID and API URL from environment variables
AIRFLOW_DAG_ID = os.environ.get("AIRFLOW_DAG_ID")
AIRFLOW_API_URL = os.environ.get("AIRFLOW_API_URL")

# Get API Executor username and password from environment variables
API_EXECUTOR_USERNAME = os.environ.get("API_EXECUTOR_USERNAME")
API_EXECUTOR_PASSWORD = os.environ.get("API_EXECUTOR_PASSWORD")

# MinIO configuration
MINIO_ENDPOINT = os.environ.get("MINIO_ENDPOINT")
MINIO_ACCESS_KEY = os.environ.get("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.environ.get("MINIO_SECRET_KEY")
MINIO_BUCKET_NAME = os.environ.get("MINIO_BUCKET_NAME")

# Base prefix for application routes
BASE_URL_PREFIX = "/api/voice-passport"

# Create a Flask application
app = Flask(__name__)

app.route(f"{BASE_URL_PREFIX}/signup", methods=['POST'])
def register_user():
    # Check if the voice_file part is in the request
    if 'voice_file' not in request.files:
        # If not, log an error and return a response indicating the error
        logger.error("No voice file part received")
        return create_response("Error", 400, "No voice file part")
    
    # Retrieve the voice file from the request
    voice_file = request.files['voice_file']

    # Check if a file was selected
    if voice_file.filename == '':
        # If not, log an error and return a response indicating the error
        logger.error("No audio file selected")
        return create_response("Error", 400, "No audio file file")
        
    # Check if the file format is allowed (in this case, only WAV files are allowed)
    if not allowed_file(voice_file.filename):
        # If not, log an error and return a response indicating the error
        logger.error("Invalid audio file format. Only WAV files are allowed.")
        return create_response("Error", 400, "Invalid audio file format. Only WAV files are allowed.")


@app.errorhandler(Exception)
def handle_error(e):
    logger.error(f"An error occurred: {str(e)}")
    return create_response("Error", 500, "An internal server error occurred")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)