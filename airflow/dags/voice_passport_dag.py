from datetime import datetime
from airflow import DAG
import importlib
import os

# Define default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
    'logging_level': 'INFO'
}

# Create the DAG with the specified default arguments
with DAG('voice_passport_dag', default_args=default_args, default_view="graph", schedule_interval=None, catchup=False) as dag:
    # Define task dependencies by chaining the tasks in sequence
    pass
