import os
import tempfile
from flask import jsonify

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

# Function to save the uploaded file locally
def save_file_locally(file):
    # Create a temporary file to store the uploaded video
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file_path = temp_file.name
    # Save the uploaded video to the temporary file
    file.save(temp_file_path)
    return temp_file_path

# Function to clean up the temporary file
def cleanup_temp_file(temp_file_path):
    # Delete the temporary file
    os.unlink(temp_file_path)