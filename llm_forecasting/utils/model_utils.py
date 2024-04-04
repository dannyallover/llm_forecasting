# Related third-party imports
import tiktoken

# Local application/library specific imports
from config.constants import OAI_SOURCE, MODEL_NAME_TO_SOURCE


def count_tokens(text, model_name):
    """
    Count the number of tokens for a given text.

    Args:
    - text (str): The input text whose tokens need to be counted.
    - model_name (str): Name of the OpenAI model to be used for token counting.

    Returns:
    - int: Number of tokens in the text for the specified model.
    """
    model_source = infer_model_source(model_name)
    if model_source == OAI_SOURCE:
        enc = tiktoken.encoding_for_model(model_name)
        token_length = len(enc.encode(text))
    else:
        token_length = len(text) / 3

    return token_length


def infer_model_source(model_name):
    """
    Infer the model source from the model name.

    Args:
    - model_name (str): The name of the model.
    """
    if "ft:gpt" in model_name:  # fine-tuned GPT-3 or 4
        return OAI_SOURCE
    if model_name not in MODEL_NAME_TO_SOURCE:
        raise ValueError(f"Invalid model name: {model_name}")
    return MODEL_NAME_TO_SOURCE[model_name]
