# Standard library imports
import logging
import json
import openai
from openai import OpenAI

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = OpenAI(
    api_key="",
    organization="",
)


def create_jsonl_for_finetuning(training_data, file_path):
    """
    Writes training data to a JSONL file for fine-tuning purposes.

    Args:
        training_data (list): A list of tuples containing user and assistant messages.
        file_path (str): Path to save the JSONL file.

    Returns:
        None: Logs the completion of file writing.
    """
    with open(file_path, "w") as jsonl_file:
        for user, assistant in training_data:
            message = {
                "messages": [
                    {"role": "user", "content": user},
                    {"role": "assistant", "content": assistant},
                ]
            }
            example = json.dumps(message)
            jsonl_file.write(example + "\n")
    logger.info(f"|training_data| saved to {file_path} as jsonl")
    return None


def upload_oai_file(file_path):
    """
    Uploads a file to OpenAI API for fine-tuning.

    Args:
        file_path (str): Path of the file to be uploaded.

    Returns:
        object: Returns a file object as a response from OpenAI API.
    """
    with open(file_path, "rb") as file_data:
        file_obj = client.files.create(file=file_data, purpose="fine-tune")

    logging.info(f"Uploaded dataset {file_path} to OpenAI API.")
    return file_obj


def create_oai_finetuning_job(model_name, train_file_id, model_suffix):
    """
    Creates a fine-tuning job with OpenAI.

    Args:
        model_name (str): Name of the base model to fine-tune.
        train_file_id (str): ID of the training file uploaded to OpenAI.
        model_suffix (str): Suffix to be added to the fine-tuned model.

    Returns:
        object: Returns a fine-tuning job object.
    """
    model = client.fine_tuning.jobs.create(
        model=model_name,
        training_file=train_file_id,
        suffix=model_suffix,
    )
    return model


def check_on_finetuning_job(ft_id):
    """
    Checks the status of a fine-tuning job.

    Args:
        ft_id (str): ID of the fine-tuning job.

    Returns:
        None: Fetches and logs the latest events of the fine-tuning job.
    """
    # Use this to check on the output of your job
    openai.FineTuningJob.list_events(id=ft_id, limit=5)
    return None
