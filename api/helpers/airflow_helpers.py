import base64
import os
import uuid
import requests

# Get Airflow DAG IDs and API URL from environment variables
AIRFLOW_REGISTRATION_DAG_ID = os.environ.get("AIRFLOW_REGISTRATION_DAG_ID")
AIRFLOW_AUTHENTICATION_DAG_ID = os.environ.get("AIRFLOW_AUTHENTICATION_DAG_ID")
AIRFLOW_API_URL = os.environ.get("AIRFLOW_API_URL")

# Get API Executor username and password from environment variables
API_EXECUTOR_USERNAME = os.environ.get("API_EXECUTOR_USERNAME")
API_EXECUTOR_PASSWORD = os.environ.get("API_EXECUTOR_PASSWORD")

def _trigger_airflow_dag(dag_id, voice_file_id, logical_date, result_webhook):
    """
    Triggers the execution of an Airflow DAG.

    Args:
    - dag_id (str): The ID of the Airflow DAG to be executed.
    - voice_file_id (str): The ID of the voice file associated with the DAG execution.
    - logical_date (datetime): The logical date for the DAG execution.
    - result_webhook (str): The webhook URL to notify the result of the DAG execution.

    Returns:
    - requests.Response: The response object from the API request.

    Raises:
    - Exception: If there's an error during the API request or response handling.
    """
    # Generate a unique DAG run ID
    dag_run_id = str(uuid.uuid4())
    logical_date_str = logical_date.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

    dag_run_conf = {
        "conf": {
            "voice_file_id": str(voice_file_id),
            "result_webhook": result_webhook
        },
        "dag_run_id": dag_run_id,  
        "logical_date": logical_date_str,
        "note": f"DAG run ID: {dag_run_id}"
    }

    # Encode API executor's username and password in Base64
    credentials = f"{API_EXECUTOR_USERNAME}:{API_EXECUTOR_PASSWORD}"
    credentials_base64 = base64.b64encode(credentials.encode()).decode()

    # Create headers for the request
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Basic {credentials_base64}"
    }

    # Build the URL to trigger the Airflow DAG execution
    airflow_dag_url = f"{AIRFLOW_API_URL}/dags/{dag_id}/dagRuns"

    # Trigger the Airflow DAG execution by sending a POST request
    response = requests.post(
        url=airflow_dag_url,
        json=dag_run_conf,
        headers=headers
    )
    return response

# Use the trigger_airflow_dag function to trigger the desired DAG
def trigger_voice_registration_dag(voice_file_id, logical_date, result_webhook):
    return _trigger_airflow_dag(AIRFLOW_REGISTRATION_DAG_ID, voice_file_id, logical_date, result_webhook)

def trigger_voice_authentication_dag(voice_file_id, logical_date, result_webhook):
    return _trigger_airflow_dag(AIRFLOW_AUTHENTICATION_DAG_ID, voice_file_id, logical_date, result_webhook)