# Standard library imports
import logging

# Local application/library-specific imports
import model_eval
import ranking
from utils import string_utils
from prompts.prompts import PROMPT_DICT

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_alignment_scores(
    reasonings,
    alignment_prompt=PROMPT_DICT["alignment"]["0"],
    model_name="gpt-3.5-turbo-1106",
    temperature=0,
    question=None,
    background=None,
    resolution_criteria=None,
):
    """
    Compute the alignment score of each reasoning for each model.

    The alignment score assesses if the reasoning is consistent with the
    model's prediction, i.e. if one were given the reasoning alone, would she
    also predict a similar probability.

    Args:
        reasonings (list[list[str]]): A list containing a list of reasonings.
        alignment_prompt(dict, optional): Alignment prompt to use.
        model_name (str, optional): Model used to compute score.
        question (str, optional): Forecasting question.
        background (str, optional): Background of question.
        resolution_criteria(str, optional): Resolution criteria of question.

    Returns:
        list[list[int]]: A list containing a list of scores.
    """
    alignment_scores = []
    for model_reasonings in reasonings:
        alignment_scores_ = []
        for reasoning in model_reasonings:
            prompt = string_utils.get_prompt(
                alignment_prompt[0],
                alignment_prompt[1],
                question=question,
                background=background,
                resolution_criteria=resolution_criteria,
                reasoning=reasoning,
            )
            try:
                alignment_response = model_eval.get_response_from_model(
                    model_name=model_name,
                    prompt=prompt,
                    max_tokens=2000,
                    temperature=temperature,
                )
                alignment_score = ranking.extract_rating_from_response(
                    alignment_response
                )
                alignment_scores_.append(alignment_score)
            except Exception as e:
                logger.error(f"Error message: {e}")
                logger.info("Failed to calculate alignment score")
                continue
        alignment_scores.append(alignment_scores_)
    return alignment_scores
