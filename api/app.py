import datetime
from flask import Flask, request
import logging
from api.helpers.mongodb_helpers import delete_user_details, find_user_details, save_user_metadata, update_user_register_planned_date, find_user_by_voice_id
from helpers.minio_helpers import handle_minio_storage
from helpers.api_helpers import cleanup_temp_file, create_response, extract_voice_file_from_request, save_file_locally 
from helpers.airflow_helpers import trigger_airflow_dag
from helpers.qdrant_helpers import search_most_similar_audio
from helpers.voice_id_verifier_helpers import verifyVoiceID

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Base prefix for application routes
BASE_URL_PREFIX = "/api/voice-passport"

# Create a Flask application
app = Flask(__name__)

app.route(f"{BASE_URL_PREFIX}/signup", methods=['POST'])
def signup_user():
    voice_file = extract_voice_file_from_request(request, logger)
    # Save the file locally
    temp_file_path = save_file_locally(voice_file)
    # Store the file in MinIO
    minio_object_name = handle_minio_storage(temp_file_path)
    fullname = request.form.get('fullname')
    email = request.form.get('email')
    if not all([fullname, email]):
        logger.error("Missing parameters")
        return create_response("Error", 400, "Missing parameters: fullname or email")

    # Save metadata about the user in MongoDB
    user_id = save_user_metadata(fullname, email, minio_object_name)

    # Clean up the temporary file
    cleanup_temp_file(temp_file_path)

    try:
        # Calculate the logical date 2 minutes from now
        logical_date = datetime.utcnow() + datetime.timedelta(minutes=2)
        # Trigger the Airflow DAG execution
        response = trigger_airflow_dag(logical_date)
        if response.status_code == 200:
            # Update the MongoDB document with "planned" flag and date
            update_user_register_planned_date(user_id, logical_date)
            logger.info("DAG execution triggered successfully")
            # Get user details
            user_info = find_user_details(user_id)
            response_data = create_response("Success", 200, "User generated and scheduled successfully.", data= {
                "user_id": str(user_info["_id"]),
                "fullname": user_info["title"],
                "email": user_info["email"],
                "planned_date": user_info["planned_date"]
            })
            return response_data
        else:
            # If DAG execution fails, remove the document from MongoDB
            delete_user_details(user_id)
            logger.error(f"Error triggering DAG execution: {response.text}")
            response_data = create_response("Error", response.status_code, "Error triggering DAG execution.")
            return response_data
    except Exception as e:
        logger.error(f"An error occurred during file proccessing : {str(e)}")
        delete_user_details(user_id)
        return create_response("Error", 500, "An error occurred during file proccessing")
    

@app.route(f"{BASE_URL_PREFIX}/signin", methods=['POST'])
def signin_user():
    """
    Sign in a user by verifying their voice ID against stored voice ID hashes.

    This endpoint receives a voice file from the request, searches for the most similar
    voice ID in the system, retrieves the corresponding user, and verifies their voice ID.

    Returns:
    - dict: A dictionary containing the result of the verification process.
            Example: {'success': True, 'message': 'User signed in successfully.',
                      'user_info': {'user_id': '12345', 'fullname': 'John Doe', 'email': 'john@example.com'}}
    """
    # Extract voice file from the request
    voice_file = extract_voice_file_from_request(request, logger)
    
    # Save the voice file locally
    temp_file_path = save_file_locally(voice_file)
    
    # Search for the most similar audio in the system and retrieve the associated voice ID
    voice_id = search_most_similar_audio(temp_file_path)

    # Find the user associated with the retrieved voice ID
    user_info = find_user_by_voice_id(voice_id)

    # Verify the user's voice ID
    verification_result = verifyVoiceID(user_info["_id"], voice_id)

    # Clean up the temporary voice file
    cleanup_temp_file(temp_file_path)

    # Return a formatted response based on the verification result
    if verification_result:
        response_data = {
            "user_id": str(user_info["_id"]),
            "fullname": user_info["fullname"],
            "email": user_info["email"]
        }
        return create_response("Success", 200, "User signed in successfully.", user_info=response_data)
    else:
        return create_response("Forbidden", 403, "Access denied.")

@app.errorhandler(Exception)
def handle_error(e):
    logger.error(f"An error occurred: {str(e)}")
    return create_response("Error", 500, "An internal server error occurred")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)