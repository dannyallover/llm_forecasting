# Standard library imports
import logging

# Local application/library-specific imports
import alignment
from config.constants import (
    DEFAULT_RETRIEVAL_CONFIG,
    DEFAULT_REASONING_CONFIG,
    S3,
    S3_BUCKET_NAME,
)
import ensemble
import ranking
import summarize
from utils import db_utils

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def to_eval(question, retrieval_number, output_dir):
    """
    Determines if a given question needs evaluation based on its presence in an S3 storage.

    Args:
    question (str): The question to be evaluated.
    retrieval_number (int): A unique identifier for the retrieval process.
    output_dir (str): The directory path where the file is expected to be found.
    file_type (str, optional): The type of the file. Default is "pickle".

    Returns:
    bool: True if the question needs evaluation, False otherwise.
    """
    question_formatted = question.replace(" ", "_").replace("/", "")
    file_name = f"{output_dir}/{retrieval_number}/{question_formatted}.pickle"
    try:
        # Try reading the file from S3
        _ = db_utils.read_pickle_from_s3(S3, S3_BUCKET_NAME, file_name)
        return False
    except BaseException:
        # If the file is not found in S3, return True to indicate it needs evaluation
        return True


def save_results(save_dict, question, retrieval_number, output_dir, file_type="pickle"):
    """
    Save a dictionary of results to an S3 storage, formatted based on a specific question.

    Args:
        save_dict (dict): The dictionary of results to be saved.
        question (str): The title of the question related to the results.
        retrieval_number (int): A unique identifier for the retrieval process.
        output_dir (str): The directory path where the file will be saved.
        file_type (str, optional): The type of the file to save. Default is "pickle".
    """
    question_formatted = question.replace(" ", "_").replace("/", "")
    file_name = f"{output_dir}/{retrieval_number}/{question_formatted}.{file_type}"
    db_utils.upload_data_structure_to_s3(S3, save_dict, S3_BUCKET_NAME, file_name)


async def retrieve_and_forecast(
    question_dict,
    question_raw,
    ir_config=DEFAULT_RETRIEVAL_CONFIG,
    reason_config=DEFAULT_REASONING_CONFIG,
    calculate_alignment=False,
    return_articles=False,
):
    """
    Asynchronously evaluates the forecasting question using the end-to-end system.

    This function integrates steps of information retrieval, summarization, reasoning,
    and alignment scoring.

    Args:
        question_dict (dict): A dictionary containing detailed data about the question.
        question_raw (dict): The raw question data.
        ir_config (dict, optional): The configuration for information retrieval.
            Defaults to DEFAULT_RETRIEVAL_CONFIG.
        reason_config (dict, optional): The configuration for reasoning.
            Defaults to DEFAULT_REASONING_CONFIG.
        calculate_alignment (bool, optional): Flag to determine if alignment scores
            should be calculated. Defaults to False.
        return_articles (bool, optional): Flag to decide if the retrieved articles
            should be returned. Defaults to False.

    Returns:
        dict: The reasoning for the questions, along with metadata and intermediate
        outputs from the system. If return_articles is True, also includes retrieved
        articles. Returns None if the question does not meet evaluation criteria.
    """
    assert isinstance(
        reason_config["BASE_REASONING_PROMPT_TEMPLATES"], list
    ), "BASE_REASONING_PROMPT_TEMPLATES must be a list."
    assert len(reason_config["BASE_REASONING_PROMPT_TEMPLATES"]) == len(
        reason_config["BASE_REASONING_MODEL_NAMES"]
    ), "BASE_REASONING_PROMPT_TEMPLATES and BASE_REASONING_MODEL_NAMES must have the same length."

    question = question_dict["question"]
    background_info = question_dict["background"]
    resolution_criteria = question_dict["resolution_criteria"]
    answer = question_dict["answer"]
    question_dates = question_dict["question_dates"]
    retrieval_dates = question_dict["retrieval_dates"]
    urls_in_background = question_dict["urls_in_background"]
    # Information retrieval
    try:
        (
            ranked_articles,
            all_articles,
            search_queries_list_gnews,
            search_queries_list_nc,
        ) = await ranking.retrieve_summarize_and_rank_articles(
            question,
            background_info,
            resolution_criteria,
            retrieval_dates,
            urls=urls_in_background,
            config=ir_config,
            return_intermediates=True,
        )
    except Exception as e:  # skip the question if failed
        logger.error(f"Error message: {e}")
        logger.info(f"IR failed at question: {question}.")
        return None
    subset_ranked_articles = ranked_articles[
        : ir_config.get("NUM_SUMMARIES_THRESHOLD", 100)
    ].copy()
    all_summaries = summarize.concat_summaries(subset_ranked_articles)
    logger.info(f"Information retrieval complete for question: {question}.")
    logger.info(f"Number of summaries: {len(subset_ranked_articles)}.")

    # Reasoning (using ensemble)
    today_to_close_date = [retrieval_dates[1], question_dates[1]]
    ensemble_dict = await ensemble.meta_reason(
        question=question,
        background_info=background_info,
        resolution_criteria=resolution_criteria,
        today_to_close_date_range=today_to_close_date,
        retrieved_info=all_summaries,
        reasoning_prompt_templates=reason_config["BASE_REASONING_PROMPT_TEMPLATES"],
        base_model_names=reason_config["BASE_REASONING_MODEL_NAMES"],
        base_temperature=reason_config["BASE_REASONING_TEMPERATURE"],
        aggregation_method=reason_config["AGGREGATION_METHOD"],
        answer_type="probability",
        weights=reason_config["AGGREGATION_WEIGTHTS"],
        meta_model_name=reason_config["AGGREGATION_MODEL_NAME"],
        meta_prompt_template=reason_config["AGGREGATION_PROMPT_TEMPLATE"],
        meta_temperature=reason_config["AGGREGATION_TEMPERATURE"],
    )

    alignment_scores = None
    if calculate_alignment:
        alignment_scores = alignment.get_alignment_scores(
            ensemble_dict["base_reasonings"],
            alignment_prompt=reason_config["ALIGNMENT_PROMPT"],
            model_name=reason_config["ALIGNMENT_MODEL_NAME"],
            temperature=reason_config["ALIGNMENT_TEMPERATURE"],
            question=question,
            background=background_info,
            resolution_criteria=resolution_criteria,
        )

    # Compute brier score (base_predictions is a list of lists of
    # probabilities)
    base_brier_scores = []
    # For each sublist (corresponding to a base model name)
    for base_predictions in ensemble_dict["base_predictions"]:
        base_brier_scores.append(
            [(base_prediction - answer) ** 2 for base_prediction in base_predictions]
        )
    # Visualization (draw the HTML)
    base_html = visualize_utils.visualize_all(
        question_data=question_raw,
        retrieval_dates=retrieval_dates,
        search_queries_gnews=search_queries_list_gnews,
        search_queries_nc=search_queries_list_nc,
        all_articles=all_articles,
        ranked_articles=ranked_articles,
        all_summaries=all_summaries,
        model_names=reason_config["BASE_REASONING_MODEL_NAMES"],
        base_reasoning_prompt_templates=reason_config[
            "BASE_REASONING_PROMPT_TEMPLATES"
        ],
        base_reasoning_full_prompts=ensemble_dict["base_reasoning_full_prompts"],
        base_reasonings=ensemble_dict["base_reasonings"],
        base_predictions=ensemble_dict["base_predictions"],
        base_brier_scores=base_brier_scores,
    )
    meta_html = visualize_utils.visualize_all_ensemble(
        question_data=question_raw,
        ranked_articles=ranked_articles,
        all_articles=all_articles,
        search_queries_gnews=search_queries_list_gnews,
        search_queries_nc=search_queries_list_nc,
        retrieval_dates=retrieval_dates,
        meta_reasoning=ensemble_dict["meta_reasoning"],
        meta_full_prompt=ensemble_dict["meta_prompt"],
        meta_prediction=ensemble_dict["meta_prediction"],
    )
    # Generate outputs, one dict per question
    output = {
        "question": question,
        "answer": int(answer),
        "data_source": question_raw["data_source"],
        "background_info": background_info,
        "resolution_criteria": resolution_criteria,
        "retrieval_dates": retrieval_dates,
        "search_queries_gnews": search_queries_list_gnews,
        "search_queries_nc": search_queries_list_nc,
        "retrieved_info": all_summaries,
        "base_model_names": reason_config["BASE_REASONING_MODEL_NAMES"],
        "base_reasoning_full_prompts": ensemble_dict["base_reasoning_full_prompts"],
        "base_reasonings": ensemble_dict["base_reasonings"],
        "base_predictions": ensemble_dict["base_predictions"],
        "alignment_scores": alignment_scores,
        "meta_reasoning_full_prompt": ensemble_dict["meta_prompt"],
        "meta_reasoning": ensemble_dict["meta_reasoning"],
        "meta_prediction": ensemble_dict["meta_prediction"],
        "community_prediction": question_dict["community_pred_at_retrieval"],
        "base_html": base_html,
        "meta_html": meta_html,
        "base_brier_score": base_brier_scores,
        "meta_brier_score": (ensemble_dict["meta_prediction"] - answer) ** 2,
        "community_brier_score": (question_dict["community_pred_at_retrieval"] - answer)
        ** 2,
    }
    if return_articles:
        return output, all_articles, ranked_articles
    return output
