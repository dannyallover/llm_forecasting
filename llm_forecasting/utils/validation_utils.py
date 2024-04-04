# Standard library imports
import logging
import sys

# Related third-party imports
import openai

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def is_valid_openai_key(api_key):
    """
    Check if the given OpenAI API key is valid.

    Args:
        api_key (str): OpenAI API key to be validated.

    Returns:
        bool: Whether the given API key is valid.
    """
    try:
        # Set the API key
        openai.api_key = api_key
        # Make a test request (e.g., listing available models)
        openai.Model.list()
        # If the above line didn't raise an exception, the key is valid
        return True
    except openai.error.AuthenticationError:
        logger.error("Invalid API key.")
        return False
    except openai.error.OpenAIError as e:
        logger.error(f"An error occurred in validating OpenAI API key: {str(e)}")
        return False


def is_valid_openai_model(model_name, api_key):
    """
    Check if the model name is valid, given a valid OpenAI API key.

    Args:
    - model_name (str): Name of the model to be validated, such as "gpt-4"
    - api_key (str): OpenAI API key, assumed to be valid.

    Returns:
    - bool: Whether the given model name is valid.
    """
    try:
        openai.api_key = api_key
        # Attempt to retrieve information about the model
        _ = openai.Model.retrieve(model_name)
        return True
    except openai.error.OpenAIError as e:
        logger.error(f"An error occurred in validing the model name: {str(e)}")
        return False


def validate_key_and_model(key, model):
    """
    Check if the given OpenAI API key and model name are valid.

    Args:
    - key (str): OpenAI API key to be validated.
    - model (str): Name of the model to be validated, such as "gpt-4"

    If either the key or model is invalid, exit the program.
    """
    if not is_valid_openai_key(key) or not is_valid_openai_model(model, key):
        sys.exit(1)
