import base64
import os
import uuid
import requests

# Get Airflow DAG IDs and API URL from environment variables
AIRFLOW_REGISTRATION_DAG_ID = os.environ.get("AIRFLOW_REGISTRATION_DAG_ID")
AIRFLOW_AUTHENTICATION_DAG_ID = os.environ.get("AIRFLOW_AUTHENTICATION_DAG_ID")
AIRFLOW_CHANGE_STATE_DAG_ID = os.environ.get("AIRFLOW_CHANGE_STATE_DAG_ID")
AIRFLOW_API_URL = os.environ.get("AIRFLOW_API_URL")

# Get API Executor username and password from environment variables
API_EXECUTOR_USERNAME = os.environ.get("API_EXECUTOR_USERNAME")
API_EXECUTOR_PASSWORD = os.environ.get("API_EXECUTOR_PASSWORD")

def _trigger_airflow_dag(dag_id, logical_date, data):
    # Generate a unique DAG run ID
    dag_run_id = str(uuid.uuid4())
    logical_date_str = logical_date.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

    dag_run_conf = {
        "conf": data,
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
def trigger_voice_registration_dag(logical_date, voice_file_id, result_webhook):
    return _trigger_airflow_dag(AIRFLOW_REGISTRATION_DAG_ID, logical_date, data={
        "voice_file_id": voice_file_id,
        "result_webhook": result_webhook
    })

def trigger_voice_authentication_dag(logical_date, voice_file_id, result_webhook):
    return _trigger_airflow_dag(AIRFLOW_AUTHENTICATION_DAG_ID, logical_date, data={
        "voice_file_id": voice_file_id,
        "result_webhook": result_webhook
    })

def trigger_voice_id_change_state_dag(logical_date, user_id, enable, result_webhook):
    return _trigger_airflow_dag(AIRFLOW_CHANGE_STATE_DAG_ID, logical_date, data={
        "user_id": user_id,
        "result_webhook": result_webhook,
        "is_enabled": enable
    })