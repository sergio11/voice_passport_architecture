import os
import re
import tempfile
from flask import jsonify
from minio_helpers import handle_minio_storage

ALLOWED_EXTENSIONS = {'wav', 'mp3'}

def process_voice_file(request, logger):
    voice_file = _extract_voice_file_from_request(request, logger)
    # Save the file locally
    temp_file_path = _save_file_locally(voice_file)
    # Store the file in MinIO
    voice_file_id = handle_minio_storage(temp_file_path)
    # Clean up the temporary voice file
    _cleanup_temp_file(temp_file_path)
    return voice_file_id

def validate_webhook_url(result_webhook, logger):
    if not re.match(r'^https?://(?:www\.)?\w+\.\w{2,3}(?:/\w*)?$', result_webhook):
        logger.error("Invalid webhook URL format")
        return False
    return True

def create_response(status, code, message, data=None):
    """
    Creates a JSON response to send to the client.

    Parameters:
    status (str): The status of the response, e.g., 'success' or 'error'.
    code (int): The HTTP code to be included in the response.
    message (str): A descriptive message accompanying the response.
    data (any, optional): Additional data to be included in the response, defaults to None.

    Returns:
    tuple: A tuple containing the JSON response and the HTTP code.
    """
    response_data = {
        "status": status,
        "code": code,
        "message": message,
        "data": data
    }
    return jsonify(response_data), code


def _extract_voice_file_from_request(request, logger):
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
        logger.error("Invalid audio file format. Only WAV or MP3 files are allowed.")
        return create_response("Error", 400, "Invalid audio file format. Only WAV files are allowed.")
    
    logger.info(f"Received file: {voice_file.filename}")

    return voice_file

# Function to save the uploaded file locally
def _save_file_locally(file):
    # Create a temporary file to store the uploaded video
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file_path = temp_file.name
    # Save the uploaded video to the temporary file
    file.save(temp_file_path)
    return temp_file_path

# Function to clean up the temporary file
def _cleanup_temp_file(temp_file_path):
    # Delete the temporary file
    os.unlink(temp_file_path)

# Check if the filename has a valid extension present in the ALLOWED_EXTENSIONS set
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS