# Standard library imports
import logging

# Related third-party imports
import numpy as np
from numpy.linalg import norm
import torch

# Local application/library-specific imports
from utils import time_utils

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def brier_score(probabilities, answer_idx):
    """
    Calculate the Brier score for a set of probabilities and the correct answer
    index.

    Args:
    - probabilities (numpy array): The predicted probabilities for each class.
    - answer_idx (int): Index of the correct answer.

    Returns:
    - float: The Brier score.
    """
    answer = np.zeros_like(probabilities)
    answer[answer_idx] = 1
    return ((probabilities - answer) ** 2).sum() / 2


def calculate_cosine_similarity_bert(text_list, tokenizer, model):
    """
    Calculate the average cosine similarity between texts in a given list using
    embeddings.

    Define Bert outside the function:
    from transformers import BertTokenizer, BertModel
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    model = BertModel.from_pretrained('bert-base-uncased')

    Parameters:
    text_list (List[str]): A list of strings where each string is a text
    document.

    Returns:
    float: The average cosine similarity between each pair of texts in the list.
           Returns 0 if the list contains less than two text documents.
    """
    if len(text_list) < 2:
        return 0

    # Function to get embeddings
    def get_embedding(text):
        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        outputs = model(**inputs)
        return torch.mean(outputs.last_hidden_state, dim=1)

    # Generating embeddings for each text
    embeddings = [get_embedding(text) for text in text_list]

    # Calculating cosine similarity between each pair of embeddings
    similarity_scores = []
    for i in range(len(embeddings)):
        for j in range(i + 1, len(embeddings)):
            similarity = torch.nn.functional.cosine_similarity(
                embeddings[i], embeddings[j]
            )
            similarity_scores.append(similarity.item())

    # Calculating average similarity
    average_similarity = np.mean(similarity_scores)

    return average_similarity


def cosine_similarity(u, v):
    """
    Compute the cosine similarity between two vectors.
    """
    return np.dot(u, v) / (norm(u) * norm(v))


def get_average_forecast(date_pred_list):
    """
    Retrieve the average forecast value from the list of predictions.

    Args:
    - date_pred_list (list of tuples): list contain tuples of (date str, pred).

    Returns:
    - float: The average prediction.
    """
    if not date_pred_list or len(date_pred_list) == 0:
        return 0.5  # Return a default value of 0.5 if there is no history
    return sum(tup[1] for tup in date_pred_list) / len(date_pred_list)


def compute_bs_and_crowd_bs(pred, date_pred_list, retrieve_date, answer):
    """
    Computes Brier scores for individual prediction and community prediction.

    Parameters:
    - pred (float): The individual's probability prediction for an event.
    - date_pred_list (list of tuples): A list of tuples containing dates
        and community predictions. Each tuple is in the format (date, prediction).
    - retrieve_date (date): The date for which the community prediction is to be retrieved.
    - answer (int): The actual outcome of the event, where 0 indicates the event
        did not happen, and 1 indicates it did.

    Returns:
    - bs (float): The Brier score for the individual prediction.
    - bs_comm (float): The Brier score for the community prediction closest to the specified retrieve_date.
    """
    pred_comm = time_utils.find_closest_date(retrieve_date, date_pred_list)[-1]
    bs = brier_score([1 - pred, pred], answer)
    bs_comm = brier_score([1 - pred_comm, pred_comm], answer)

    return bs, bs_comm
