import base64
import os
import uuid
import requests

# Get Airflow DAG ID and API URL from environment variables
AIRFLOW_DAG_ID = os.environ.get("AIRFLOW_DAG_ID")
AIRFLOW_API_URL = os.environ.get("AIRFLOW_API_URL")

# Get API Executor username and password from environment variables
API_EXECUTOR_USERNAME = os.environ.get("API_EXECUTOR_USERNAME")
API_EXECUTOR_PASSWORD = os.environ.get("API_EXECUTOR_PASSWORD")

# Function to trigger an Airflow DAG execution
def trigger_airflow_dag(user_id, logical_date):
    # Generate a unique DAG run ID
    dag_run_id = str(uuid.uuid4())
    logical_date_str = logical_date.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

    dag_run_conf = {
        "conf": {
            "user_id": str(user_id),
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
    airflow_dag_url = f"{AIRFLOW_API_URL}/dags/{AIRFLOW_DAG_ID}/dagRuns"

    # Trigger the Airflow DAG execution by sending a POST request
    response = requests.post(
        url=airflow_dag_url,
        json=dag_run_conf,
        headers=headers
    )
    return response
