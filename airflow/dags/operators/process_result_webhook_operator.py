from airflow.utils.decorators import apply_defaults
from operators.base_custom_operator import BaseCustomOperator
import requests

class ProcessResultWebhookOperator(BaseCustomOperator):

    @apply_defaults
    def __init__(
        self,
        *args, **kwargs
    ):
        """
        Initialize the operator.

        Inherits:
        - *args: Additional arguments.
        - **kwargs: Additional keyword arguments.
        """
        super().__init__(*args, **kwargs)

    def execute(self, context):
        # Log the start of the execution
        self._log_to_mongodb(f"Starting execution of ProcessResultWebhookOperator", context, "INFO")
        # Get the configuration passed to the DAG from the execution context
        dag_run_conf = context['dag_run'].conf
        user_id = dag_run_conf['user_id']

        # Extract necessary data from the DAG run configuration
        result_webhook = dag_run_conf.get('result_webhook')
        result_data = dag_run_conf.get('result')

        # Validate if result_webhook is present
        if not result_webhook:
            self._log_to_mongodb("No result webhook provided", context, "ERROR")
            raise ValueError("No result webhook provided")

        # Validate if result_data is present
        if not result_data:
            self._log_to_mongodb("No result data provided", context, "ERROR")
            raise ValueError("No result data provided")

        try:
            # Make a POST request to the result webhook
            response = requests.post(result_webhook, json=result_data)
            response.raise_for_status()  # Raise an error for non-2xx responses
            self._log_to_mongodb(f"POST request to {result_webhook} successful", context, "INFO")
        except Exception as e:
            # Log any exceptions that occur during the POST request
            self._log_to_mongodb(f"Error making POST request to {result_webhook}: {str(e)}", context, "ERROR")
            raise

        # Log the end of the execution
        self._log_to_mongodb(f"Execution of ProcessResultWebhookOperator completed", context, "INFO")

        return { "user_id": user_id}