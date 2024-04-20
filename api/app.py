import datetime
from flask import Flask, request
import logging
from api.helpers.jwt_helpers import validate_jwt, generate_jwt
from api.helpers.mongodb_helpers import delete_user_details, find_user_details, save_user_metadata, update_user_register_planned_date, find_user_by_voice_id
from helpers.api_helpers import process_voice_file, create_response, validate_webhook_url
from helpers.airflow_helpers import trigger_voice_registration_dag, trigger_voice_authentication_dag
from helpers.voice_id_verifier_helpers import verify_voice_id, change_voice_id_verification_state


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Base prefix for application routes
BASE_URL_PREFIX = "/api/voice-passport"

# Create a Flask application
app = Flask(__name__)

@app.route(f"{BASE_URL_PREFIX}/schedule_user_registration", methods=['POST'])
def schedule_user_registration():
    fullname = request.form.get('fullname')
    email = request.form.get('email')
    result_webhook = request.form.get('result_webhook')

    # Validate received data
    if not all([fullname, email, result_webhook]):
        logger.error("Missing parameters")
        return create_response("Error", 400, "Missing parameters: fullname, email, or result_webhook")

    # Validate the format of the webhook URL
    if not validate_webhook_url(result_webhook, logger):
        return create_response("Error", 400, "Invalid webhook URL format")

    # Process the voice file
    voice_file_id = process_voice_file(request, logger)

    # Save metadata about the user in MongoDB
    user_id = save_user_metadata(fullname, email, voice_file_id)

    # Schedule the user registration DAG
    return _schedule_user_registration(user_id, voice_file_id, result_webhook)

@app.route(f"{BASE_URL_PREFIX}/schedule_user_authentication", methods=['POST'])
def schedule_user_authentication():
    result_webhook = request.form.get('result_webhook')

    # Validate the format of the webhook URL
    if not validate_webhook_url(result_webhook, logger):
        return create_response("Error", 400, "Invalid webhook URL format")
    
    # Process the voice file
    voice_file_id = process_voice_file(request, logger)

    # Schedule the user authentication DAG
    return _schedule_user_authentication(voice_file_id, result_webhook)

def _schedule_user_registration(user_id, voice_file_id, result_webhook):
    try:
        # Calculate the logical date 2 minutes from now
        logical_date = datetime.utcnow() + datetime.timedelta(minutes=2)
        # Trigger the registration DAG execution
        response = trigger_voice_registration_dag(voice_file_id, logical_date, result_webhook)
        if response.status_code == 200:
            return create_response("Success", 200, "User registration scheduled successfully.", data={"user_id": user_id})
        else:
            logger.error(f"Error triggering registration DAG execution: {response.text}")
            return create_response("Error", response.status_code, "Error triggering user registration scheduling.")
    except Exception as e:
        logger.error(f"An error occurred during file processing: {str(e)}")
        return create_response("Error", 500, "An error occurred during user registration scheduling.")

def _schedule_user_authentication(voice_file_id, result_webhook):
    try:
        # Calculate the logical date 2 minutes from now
        logical_date = datetime.utcnow() + datetime.timedelta(minutes=2)
        # Trigger the authentication DAG execution
        response = trigger_voice_authentication_dag(voice_file_id, logical_date, result_webhook)
        if response.status_code == 200:
            return create_response("Success", 200, "User authentication scheduled successfully.")
        else:
            logger.error(f"Error triggering authentication DAG execution: {response.text}")
            return create_response("Error", response.status_code, "Error triggering user authentication scheduling.")
    except Exception as e:
        logger.error(f"An error occurred during file processing: {str(e)}")
        return create_response("Error", 500, "An error occurred during user authentication scheduling.")


@app.route(f"{BASE_URL_PREFIX}/accounts/<string:user_id>/enable", methods=['PUT'])
@validate_jwt
def enable_user(decoded_token, user_id):
    """
    Enable a user identified by user_id.

    This endpoint enables a user by setting their status to 'enabled' in the system.

    Parameters:
    - user_id (str): The ID of the user to enable.

    Returns:
    - dict: A dictionary containing the result of the operation.
    """
    # Check if user ID in JWT matches the user ID provided in the URL
    if decoded_token.get('user_id') == user_id:
        change_voice_id_verification_state(user_id=user_id, is_enabled=True)
        return create_response("Success", 200, f"User with ID {user_id} enabled successfully.")
    else:
        return create_response("Forbidden", 403, "Unauthorized access.")

@app.route(f"{BASE_URL_PREFIX}/accounts/<string:user_id>/disable", methods=['PUT'])
@validate_jwt
def disable_user(decoded_token, user_id):
    """
    Disable a user identified by user_id.

    This endpoint disables a user by setting their status to 'disabled' in the system.

    Parameters:
    - user_id (str): The ID of the user to disable.

    Returns:
    - dict: A dictionary containing the result of the operation.
    """
    # Check if user ID in JWT matches the user ID provided in the URL
    if decoded_token.get('user_id') == user_id:
        change_voice_id_verification_state(user_id=user_id, is_enabled=False)
        return create_response("Success", 200, f"User with ID {user_id} disabled successfully.")
    else:
        return create_response("Forbidden", 403, "Unauthorized access.")
    

@app.route(f"{BASE_URL_PREFIX}/accounts/current", methods=['GET'])
@validate_jwt
def get_current_user(decoded_token):
    """
    Get information about the currently authenticated user.

    This endpoint retrieves information about the user whose JWT token is provided in the request headers.

    Returns:
    - dict: A dictionary containing information about the currently authenticated user.
    """
    # Extract user ID from decoded token
    user_id = decoded_token.get('user_id')
    if user_id:
        user_info = find_user_details(user_id)
        user_info = {
            "user_id": user_id,
            "fullname": user_info["fullname"],
            "email": user_info["email"],
        }
        return create_response("Success", 200, "Information about the currently authenticated user retrieved successfully.", data=user_info)
    else:
        return create_response("Forbidden", 403, "Unauthorized access.")

@app.errorhandler(Exception)
def handle_error(e):
    logger.error(f"An error occurred: {str(e)}")
    return create_response("Error", 500, "An internal server error occurred")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)