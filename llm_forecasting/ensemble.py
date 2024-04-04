# Standard library imports
import logging

# Related third-party imports
import numpy as np

# Local application/library-specific imports
from config.constants import TOKENS_TO_PROBS_DICT
import model_eval
from prompts.prompts import PROMPT_DICT
from utils import string_utils, utils

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def concatenate_reasonings(reasonings):
    """
    Concatenate a list of reasonings into a single string.

    Each reasoning is separated by a newline, a separator (---) and a number
    (Response 1, 2, 3, ...).

    Args:
        reasonings (list[str]): A list of reasonings.

    Returns:
        str: A single string containing all reasonings.
    """
    concat_reasonings = []
    for i, reasoning in enumerate(reasonings):
        reason_str = f"Response from forecaster {i + 1}:\n{reasoning}"
        concat_reasonings.append(reason_str)
    return "---\n" + "\n\n-\n".join(concat_reasonings) + "\n---"


async def meta_reason(
    question,
    background_info,
    resolution_criteria,
    today_to_close_date_range,
    retrieved_info,
    reasoning_prompt_templates,
    base_model_names=["gpt-4-1106-preview", "claude-2.1"],
    base_temperature=1.0,  # temperature for the base reasonings
    aggregation_method="meta",
    answer_type="probability",
    weights=None,
    end_words=list(TOKENS_TO_PROBS_DICT["ten_options"].keys()),
    meta_model_name="gpt-4-1106-preview",
    meta_prompt_template=PROMPT_DICT["meta_reasoning"]["0"],
    meta_temperature=0.2,
):
    """
    Given a question and its retrieved articles, elicit model reasonings via
    reasoning_prompts, aggregate the reasonings and return the answer.

    Args:
        question (str): Forecast question to be answered.
        background_info (str): Background information of the question.
        resolution_criteria (str): Resolution criteria for the question.
        retrieved_info (str): Retrieved articles from our news retrieval system
        (a concatenation of the article titles and summaries).
        today_to_close_date_range (str): A string containing the today's date
        and the close date.
        retrieved_info (str): Retrieved articles from our news retrieval system.
        reasoning_prompt_templates (list[list[[str]]): A list of reasoning prompts; string templates
            that must have tow fields {question} and {retrieved_info}.
            There should be a list of reasoning prompts for each base model.
        base_model_names (list[str], optional): A list of base model names.
        base_temperature (float, optional): Sampling temperature for the base reasonings.
        aggregation_method (str, optional): The method to aggregate the reasonings.
            Must be either 'vote-or-median','mean', 'weighted-mean', 'meta'.
        answer_type (str, optional): The type of the answer to return. Must be either 'probability' or 'tokens'.
        weights (np.array, optional): A numpy array of weights for the reasonings.
            It will only be used if aggregation_method is 'weighted-mean'.
            It must have the same length as reasoning_prompt_templates: shape[0] ==
            len(reasoning_prompt_templates).
        end_words (list, optional): A list of words like "Very Unlikely" and "Very Likely" that represent the answer.
            It will only be used if answer_type is 'tokens' and aggregation_method
            is 'vote-or-median'.
        meta_model_name (str, optional): The name of the meta model.
        meta_prompt_template (tuple of str, optional): A meta reasoning prompt template; a string template
        meta_temparature (float, optional): Sampling temperature for the meta-reasoning.

    Returns:
        tuple: The method returns the final answer, all base reasonings, and the meta-reasoning
            (if aggregation_method is 'meta').

    For the final answer:
        If answer_type is 'probability' and aggregation_method is 'vote-or-median',
            the function returns the median of all answers.
        If answer_type is 'tokens' and aggregation_method is 'vote-or-median',
            the function returns the most frequent answer.
        If the aggregation_method is 'meta', the function returns an answer
            by eliciting another meta-reasoning using the meta_prompt_template.
    """
    assert answer_type in [
        "probability",
        "tokens",
    ], "answer_type must be either 'probability' or 'tokens'"
    assert aggregation_method in [
        "vote-or-median",
        "meta",
        "mean",
        "weighted-mean",
    ], "aggregation_method must be either 'vote-or-median', 'meta', 'mean', or 'weighted-mean'"
    if aggregation_method == "weighted-mean":
        assert (
            weights is not None
        ), "weights must be provided if aggregation_method is 'weighted-mean'"
        assert weights.shape[0] == len(
            reasoning_prompt_templates
        ), "weights must have the same length as reasoning_prompt_templates"
    all_base_reasonings = []
    all_base_reasoning_full_prompts = []
    for i, base_model_name in enumerate(base_model_names):
        (
            base_reasonings,
            base_reasoning_full_prompts,
        ) = await model_eval.async_make_forecast(
            question=question,
            background_info=background_info,
            resolution_criteria=resolution_criteria,
            dates=today_to_close_date_range,
            retrieved_info=retrieved_info,
            reasoning_prompt_templates=reasoning_prompt_templates[i],
            model_name=base_model_name,
            temperature=base_temperature,
            return_prompt=True,
        )
        # list of lists (not flattened)
        all_base_reasonings.append(base_reasonings)
        all_base_reasoning_full_prompts.append(base_reasoning_full_prompts)
    aggregation_dict = aggregate_base_reasonings(
        base_reasonings=all_base_reasonings,
        question=question,
        background_info=background_info,
        today_to_close_date_range=today_to_close_date_range,
        resolution_criteria=resolution_criteria,
        retrieved_info=retrieved_info,
        aggregation_method=aggregation_method,
        answer_type=answer_type,
        weights=weights,
        end_words=end_words,
        model_name=meta_model_name,  # meta model name
        meta_prompt_template=meta_prompt_template,
        meta_temperature=meta_temperature,
    )
    aggregation_dict["base_reasoning_full_prompts"] = all_base_reasoning_full_prompts
    return aggregation_dict


def aggregate_base_reasonings(
    base_reasonings,
    question,
    background_info,
    today_to_close_date_range,
    resolution_criteria,
    retrieved_info,
    aggregation_method="meta",
    answer_type="probability",
    weights=None,
    end_words=list(TOKENS_TO_PROBS_DICT["ten_options"].keys()),
    model_name="gpt-4-1106-preview",  # meta model name
    meta_prompt_template=PROMPT_DICT["meta_reasoning"]["0"],
    meta_temperature=0.2,
):
    """
    Aggregate a list of lists of base reasonings via ensembling method.

    Args:
        base_reasonings (list[list[str]]): A list of lists of base reasonings.
        question (str): Forecast question to be answered.
        background_info (str): Background information of the question.
        today_to_close_date_range (str): A string containing the today's date and the close date.
        resolution_criteria (str): Resolution criteria for the question.
        retrieved_info (str): Retrieved articles from our news retrieval system
            (a concatenation of the article titles and summaries).
        aggregation_method (str, optional): The method to aggregate the reasonings.
            Must be either 'vote-or-median','mean', 'weighted-mean', 'meta'.
        answer_type (str, optional): The type of the answer to return. Must be either 'probability' or 'tokens'.
        weights (np.array, optional): A numpy array of weights for the reasonings.
            It will only be used if aggregation_method is 'weighted-mean'.
            It must have the same length as reasoning_prompt_templates: shape[0] ==
            len(reasoning_prompt_templates).
        end_words (list, optional): A list of words like "Very Unlikely" and "Very Likely" that represent the answer.
            It will only be used if answer_type is 'tokens' and aggregation_method
            is 'vote-or-median'.
        model_name (str, optional): The name of the meta model.
        meta_prompt_template (str, optional): A string that represents the meta reasoning prompt.
        meta_temperature (float, optional): Sampling temperature for the meta-reasoning.

    Returns:
        dict: A dictionary containing the final answer, all base reasonings, and the meta-reasoning
            (if aggregation_method is 'meta').
    """
    assert len(base_reasonings) > 0, "base_reasonings must be a non-empty list"
    # Extract final prediction from each reasoning
    all_base_predictions = []  # list of lists of floats
    for base_reasonings_list in base_reasonings:
        base_predictions = [  # for one model; list of floats
            string_utils.extract_prediction(
                reasoning, answer_type=answer_type, end_words=end_words
            )
            for reasoning in base_reasonings_list
        ]
        all_base_predictions.append(base_predictions)
    flattened_all_base_predictions = [
        item for sublist in all_base_predictions for item in sublist
    ]
    if len(flattened_all_base_predictions) == 1:  # no aggregation needed
        return {
            "base_reasonings": base_reasonings,
            "base_predictions": all_base_predictions,
            "meta_prediction": flattened_all_base_predictions[0],
            "meta_prompt": None,
            "meta_reasoning": None,
        }
    if answer_type == "probability" and aggregation_method != "meta":
        if aggregation_method == "mean" or aggregation_method is None:
            meta_prediction = np.mean(flattened_all_base_predictions)  # default to mean
        if aggregation_method == "vote-or-median":
            meta_prediction = np.median(flattened_all_base_predictions)
        if aggregation_method == "weighted-mean":
            meta_prediction = np.average(
                flattened_all_base_predictions, weights=weights
            )
        if meta_prediction is None or meta_prediction < 0.0 or meta_prediction > 1.0:
            logger.debug(
                "final_answer {} is not between 0 and 1".format(meta_prediction)
            )
            meta_prediction = 0.5  # default to 0.5
        return {
            "base_reasonings": base_reasonings,
            "base_predictions": all_base_predictions,
            "meta_prediction": meta_prediction,
            "meta_prompt": None,
            "meta_reasoning": None,
        }
    elif answer_type == "tokens" and aggregation_method == "vote-or-median":
        meta_prediction = utils.most_frequent_item(
            flattened_all_base_predictions
        )  # majority vote
        if meta_prediction is None or not string_utils.is_string_in_list(
            meta_prediction, end_words
        ):
            logger.debug("final_answer {} is not valid".format(meta_prediction))
            meta_prediction = "Slightly Unlikely"  # default to "Slightly Unlikely"
        return {
            "base_reasonings": base_reasonings,
            "base_predictions": all_base_predictions,
            "meta_prediction": meta_prediction,
            "meta_prompt": None,
            "meta_reasoning": None,
        }

    # If aggregation_method is 'meta', elicit a meta-reasoning using the
    # meta_prompt_template
    prompt, fields = meta_prompt_template
    flattened_base_reasonings = [
        item for sublist in base_reasonings for item in sublist
    ]
    meta_full_prompt = string_utils.get_prompt(
        prompt,
        fields,
        question=question,
        background=background_info,
        dates=today_to_close_date_range,
        retrieved_info=retrieved_info,
        reasoning=concatenate_reasonings(flattened_base_reasonings),
        resolution_criteria=resolution_criteria,
    )
    meta_reasoning = model_eval.get_response_from_model(
        model_name=model_name,
        prompt=meta_full_prompt,
        temperature=meta_temperature,
    )  # raw response
    # Extract final prediction from raw response
    if answer_type == "probability":
        # Get the probability from the meta-reasoning
        meta_prediction = string_utils.extract_probability_with_stars(meta_reasoning)
        if meta_prediction is None or meta_prediction < 0.0 or meta_prediction > 1.0:
            logger.debug(
                "final_answer {} is not between 0 and 1".format(meta_prediction)
            )
            meta_prediction = 0.5
    elif answer_type == "tokens":
        # Get the final token answer from the meta-reasoning
        meta_prediction = string_utils.find_end_word(meta_reasoning, end_words)
        if meta_prediction is None or not string_utils.is_string_in_list(
            meta_prediction, end_words
        ):
            logger.debug("final_answer {} is not valid".format(meta_prediction))
            meta_prediction = "Slightly Unlikely"

    return {
        "base_reasonings": base_reasonings,
        "base_predictions": all_base_predictions,
        "meta_prompt": meta_full_prompt,
        "meta_reasoning": meta_reasoning,
        "meta_prediction": meta_prediction,
    }


def calculate_normalized_weighted_trimmed_mean(predictions):
    """
    Calculate the normalized weighted trimmed mean of a set of predictions.

    This function performs the following steps:
    1. Compute the median of the predictions to serve as a reference point.
    2. Identify the prediction that is furthest from the median value.
    3. Reduce the weight of the furthest prediction by half, acknowledging its potential outlier status.
    4. Equally distribute the reduced weight from the furthest prediction among the remaining predictions, ensuring the total weight remains constant.
    5. Compute and return the weighted mean of the predictions, using the adjusted weights to account for outliers and variance.

    Parameters:
    - predictions (np.ndarray): An array of numerical prediction values.

    Returns:
    - float: The normalized weighted trimmed mean of the predictions.
    """
    # Step 1: Find the median
    median_prediction = np.median(predictions)

    # Step 2: Determine the prediction farthest from the median
    distances = np.abs(predictions - median_prediction)
    max_distance = np.max(distances)

    # Step 3: Down-weight the furthest prediction by half
    weights = np.ones(len(predictions))
    weights[distances == max_distance] *= 0.5

    # Step 4: Distribute the saved weight among other predictions
    saved_weight = (1.0 - 0.5) / (len(predictions) - 1)
    weights[distances != max_distance] += saved_weight

    # Step 5: Calculate the weighted mean
    weighted_mean = np.average(predictions, weights=weights)

    return weighted_mean
