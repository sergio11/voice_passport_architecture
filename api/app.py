from datetime import datetime, timezone
from flask import Flask, request
import logging
from helpers.jwt_helpers import validate_jwt
from helpers.mongodb_helpers import delete_user_details, find_user_details, save_user_metadata, find_user_by_email_or_fullname
from helpers.api_helpers import process_voice_file, create_response, validate_webhook_url
from helpers.airflow_helpers import trigger_voice_id_change_state_dag, trigger_voice_registration_dag, trigger_voice_authentication_dag

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Base prefix for application routes
BASE_URL_PREFIX = "/api/voice-passport"

# Create a Flask application
app = Flask(__name__)

@app.route(f"{BASE_URL_PREFIX}/schedule_user_registration", methods=['POST'])
def schedule_user_registration():
    data = request.form
    fullname = data.get('fullname')
    email = data.get('email')
    result_webhook = data.get('result_webhook')

    # Validate received data
    if not all([fullname, email, result_webhook]):
        logger.error("Missing parameters")
        return create_response("Error", 400, "Missing parameters: fullname, email, or result_webhook")

    # Validate the format of the webhook URL
    if not validate_webhook_url(result_webhook, logger):
        return create_response("Error", 400, "Invalid webhook URL format")
    
    # Check if the user already exists
    existing_user = find_user_by_email_or_fullname(email=email, fullname=fullname)
    if existing_user:
        logger.error("User already exists")
        return create_response("Error", 400, "User already exists")

    # Process the voice file
    voice_file_id = process_voice_file(request, logger)

    # Save metadata about the user in MongoDB
    user_id = save_user_metadata(fullname, email, voice_file_id)

    # Trigger the registration DAG execution
    response = trigger_voice_registration_dag(datetime.now(timezone.utc), voice_file_id, result_webhook)
    if response.status_code == 200:
        return create_response("Success", 200, "User registration scheduled successfully.", data={"user_id": user_id})
    else:
        delete_user_details(user_id)
        logger.error(f"Error triggering registration DAG execution: {response.text}")
        return create_response("Error", response.status_code, "Error triggering user registration scheduling.")

@app.route(f"{BASE_URL_PREFIX}/schedule_user_authentication", methods=['POST'])
def schedule_user_authentication():
    result_webhook = request.form.get('result_webhook')

    # Validate the format of the webhook URL
    if not validate_webhook_url(result_webhook, logger):
        return create_response("Error", 400, "Invalid webhook URL format")
    
    # Process the voice file
    voice_file_id = process_voice_file(request, logger)

    # Trigger the authentication DAG execution
    response = trigger_voice_authentication_dag(datetime.now(timezone.utc), voice_file_id, result_webhook)
    if response.status_code == 200:
        return create_response("Success", 200, "User authentication scheduled successfully.")
    else:
        logger.error(f"Error triggering authentication DAG execution: {response.text}")
        return create_response("Error", response.status_code, "Error triggering user authentication scheduling.")


@app.route(f"{BASE_URL_PREFIX}/accounts/<string:user_id>/enable", methods=['PUT'])
@validate_jwt
def enable_user(decoded_token, user_id):
    result_webhook = request.json.get('result_webhook')
    return _change_user_state(decoded_token, user_id, True, result_webhook)

@app.route(f"{BASE_URL_PREFIX}/accounts/<string:user_id>/disable", methods=['PUT'])
@validate_jwt
def disable_user(decoded_token, user_id):
    result_webhook = request.json.get('result_webhook')
    return _change_user_state(decoded_token, user_id, False, result_webhook)
    
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


def _change_user_state(decoded_token, user_id, enable, result_webhook):
    # Validate the format of the webhook URL
    if not validate_webhook_url(result_webhook, logger):
        return create_response("Error", 400, "Invalid webhook URL format")
    # Check if user ID in JWT matches the user ID provided in the URL
    if decoded_token.get('user_id') != user_id:
        return create_response("Forbidden", 403, "Unauthorized access.")

    # Trigger DAG execution
    response = trigger_voice_id_change_state_dag(datetime.now(timezone.utc), user_id, enable, result_webhook)
    if response.status_code == 200:
        return create_response("Success", 200, "User state change scheduled successfully.")
    else:
        logger.error(f"Error triggering voice id change state DAG execution: {response.text}")
        return create_response("Error", response.status_code, "Error triggering user state change scheduling.")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)