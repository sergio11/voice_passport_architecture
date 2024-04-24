from airflow.utils.decorators import apply_defaults
from operators.base_custom_operator import BaseCustomOperator
import requests

class ProcessResultWebhookOperator(BaseCustomOperator):
    """
    Executes a task to process and send result data to a specified webhook.

    :param result_webhook: The URL of the webhook to send the result data to.
    :type result_webhook: str
    :param tasks: A list of task IDs to pull result data from.
    :type tasks: list[str]
    """

    @apply_defaults
    def __init__(
        self,
        result_webhook: str,
        tasks: list[str],
        *args, **kwargs
    ):
        """
        Initialize the operator.

        Inherits:
        - *args: Additional arguments.
        - **kwargs: Additional keyword arguments.
        """
        super().__init__(*args, **kwargs)
        self.result_webhook = result_webhook
        self.tasks = tasks

    def execute(self, context):
        """
        Execute the operator.

        This method pulls result data from the specified tasks,
        combines the data, and sends it to the specified webhook.

        :param context: The context object, containing metadata related to the execution.
        :type context: dict
        :return: A dictionary containing the user ID extracted from the result data.
        :rtype: dict
        :raises ValueError: If the result webhook, user ID, or result data is not provided.
        """

        # Log the start of the execution
        self._log_to_mongodb(f"Starting execution of ProcessResultWebhookOperator", context, "INFO")
        
        # Retrieve the result webhook from the DAG run configuration
        dag_run_conf = context['dag_run'].conf
        result_webhook = dag_run_conf.get('result_webhook')

        # Retrieve and combine result data from specified tasks
        combined_args = {}
        for task_id in self.tasks:
            args = context['task_instance'].xcom_pull(task_ids=task_id)
            if args:
                combined_args.update(args[0])

        # Extract user ID and result data
        user_id = combined_args.get('user_id')
        result_data = combined_args.get('result')

        # Validate if result_webhook is present
        if not result_webhook:
            self._log_to_mongodb("No result webhook provided", context, "ERROR")
            raise ValueError("No result webhook provided")

        # Validate if user_id is present
        if not user_id:
            self._log_to_mongodb("No user ID provided", context, "ERROR")
            raise ValueError("No user ID provided")

        # Validate if result_data is present
        if not result_data:
            self._log_to_mongodb("No result data provided", context, "ERROR")
            raise ValueError("No result data provided")

        # Log the result_data before making the POST request
        self._log_to_mongodb(f"Result data to be sent: {result_data}", context, "INFO")
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

        return {"user_id": user_id}