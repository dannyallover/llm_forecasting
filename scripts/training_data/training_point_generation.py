# Standard library imports
import argparse
import asyncio
import logging
import random

# Local application/library specific imports
from utils import data_utils
from prompts.prompts import PROMPT_DICT
import evaluation

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TRAINING_RETRIEVAL_CONFIG = {
    # Number of search query keywords per question.
    "NUM_SEARCH_QUERY_KEYWORDS": [4, 5, 6],
    "MAX_WORDS_NEWSCATCHER": [5],
    "MAX_WORDS_GNEWS": [7, 8, 9],
    "SEARCH_QUERY_MODEL_NAME": ["gpt-4-1106-preview"],
    "SEARCH_QUERY_TEMPERATURE": [0.0],
    "SEARCH_QUERY_PROMPT_TEMPLATES": [
        [PROMPT_DICT["search_query"]["0"]],
        [PROMPT_DICT["search_query"]["1"]],
        [PROMPT_DICT["search_query"]["0"], PROMPT_DICT["search_query"]["1"]],
    ],
    "NUM_ARTICLES_PER_QUERY": [5, 7, 9],
    "SUMMARIZATION_MODEL_NAME": ["gpt-3.5-turbo-1106"],
    "SUMMARIZATION_TEMPERATURE": [0.2],
    "SUMMARIZATION_PROMPT_TEMPLATE": [
        PROMPT_DICT["summarization"]["0"],
        PROMPT_DICT["summarization"]["1"],
        PROMPT_DICT["summarization"]["9"],
    ],
    "RANKING_MODEL_NAME": ["gpt-3.5-turbo-1106"],
    "RANKING_TEMPERATURE": [0.0],
    "RANKING_PROMPT_TEMPLATE": [PROMPT_DICT["ranking"]["0"]],
    "RANKING_RELEVANCE_THRESHOLD": [4],
    "SORT_BY": ["relevancy"],
    "RANKING_METHOD": ["llm-rating"],
    "RANKING_METHOD_LLM": ["title_250_tokens"],
    "NUM_SUMMARIES_THRESHOLD": [15, 20, 25],
}

TRAINING_REASONING_CONFIG = {
    "BASE_REASONING_MODEL_NAMES": [["claude-2.1", "gpt-4-1106-preview"]],
    "BASE_REASONING_TEMPERATURE": [0.2, 0.3, 0.4],
    "BASE_REASONING_PROMPT_TEMPLATES": [[], []],
    "AGGREGATION_METHOD": ["meta"],
    "AGGREGATION_PROMPT_TEMPLATE": [PROMPT_DICT["meta_reasoning"]["0"]],
    "AGGREGATION_TEMPERATURE": [0.2, 0.3, 0.4],
    "AGGREGATION_MODEL_NAME": ["claude-2.1", "gpt-4-1106-preview"],
    "AGGREGATION_WEIGTHTS": None,
}


def sample_retrieval_hyperparms(ir_config):
    """
    Sample hyperparameters for information retrieval configuration.

    Args:
        ir_config (dict): A dictionary containing different hyperparameters for information retrieval.

    Returns:
        dict: A dictionary with the same keys as ir_config, but each key has a single randomly
        sampled hyperparameter.
    """
    sampled_ir_config = ir_config.copy()
    for key, hyperparams in ir_config.items():
        sampled_ir_config[key] = random.choice(hyperparams)
    return sampled_ir_config


def sample_reasoning_hyperparams(reasoning_config, prompts_to_sample, prompt_weights):
    sampled_reasoning_config = reasoning_config.copy()
    for key, hyperparams in reasoning_config.items():
        if key != "BASE_REASONING_PROMPT_TEMPLATES":
            sampled_reasoning_config[key] = random.choice(hyperparams)
        else:
            # For BASE_REASONING_PROMPT_TEMPLATES, sample 5 prompts for each model
            models = sampled_reasoning_config["BASE_REASONING_MODEL_NAMES"]
            print(models)
            sampled_prompts = []
            for model in models:
                model_prompts = random.choices(
                    prompts_to_sample, weights=prompt_weights[model], k=5
                )
                sampled_prompts.append(model_prompts)
            sampled_reasoning_config[key] = sampled_prompts
    return sampled_reasoning_config


async def generate_training_points(
    s3_path,
    retrieval_index,
    num_retrievals,
    questions_after,
    ir_config,
    reasoning_config,
    output_dir,
    prompts_to_sample,
    prompt_weights,
):
    """
    Asynchronously generates training data points.

    Args:
        s3_path (str): The S3 path to retrieve initial data.
        retrieval_index (int): An index specifying the location or category for retrieval.
        num_retrievals (int): Number of data retrievals to perform.
        questions_after (str): A filtering criterion for questions.
        ir_config (dict, optional): Configuration for information retrieval. Defaults to {}.
        reasoning_config (dict, optional): Configuration for reasoning processes. Defaults to {}.
        output_dir (str, optional): The directory where output files are stored. Defaults to 'data_point_generation'.

    Description:
        Retrieves training data, iterates through questions, evaluates them if necessary, processes them
        based on given configurations, and saves the output.

    Returns:
        None: The function is used for its side effect of processing and saving data.
    """
    data_dict, raw_data = data_utils.get_data(
        s3_path,
        retrieval_index,
        num_retrievals,
        questions_after=questions_after,
        return_raw_question_data=True,
    )
    for q_index, question in enumerate(data_dict["question_list"]):
        if not evaluation.to_eval(question, retrieval_index, output_dir):
            logger.info(f"Already processed question, {q_index}: {question}")
            continue

        logger.info(f"Starting question, {q_index}: {question}")
        try:
            ir_config_samp = sample_retrieval_hyperparms(ir_config)
            reasoning_config_samp = sample_reasoning_hyperparams(
                reasoning_config, prompts_to_sample, prompt_weights
            )
            output, _, ranked_articles = await evaluation.retrieve_and_forecast(
                data_utils.format_single_question(data_dict, q_index),
                raw_data[q_index],
                ir_config=ir_config_samp,
                reason_config=reasoning_config_samp,
                return_articles=True,
                calculate_alignment=True,
            )
            output["ranked_articles"] = [
                (art.summary, art.relevance_rating) for art in ranked_articles
            ]
            evaluation.save_results(output, question, retrieval_index, output_dir)
        except Exception as e:
            logger.error(f"Error processing question {q_index}: {e}")

    return None


async def main():
    """
    Start the training point generation job.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--s3_path",
        type=str,
        default="training_sets/forecasting_binary_training_set.pickle",
        help="S3 dataset path to run (use 'default' for metaculus training set).",
    )
    parser.add_argument(
        "--retrieval_index",
        type=int,
        default=1,
        help="Index for retrieval (1 to |num_retrievals|).",
    )
    parser.add_argument(
        "--num_retrievals",
        type=int,
        default=5,
        help="Number of ideal retrieval dates.",
    )
    parser.add_argument(
        "--questions_after",
        type=str,
        default="2015",
        help="The lower-bound year for questions to evaluate.",
    )
    args = parser.parse_args()

    await generate_training_points(
        args.s3_path,
        args.retrieval_index,
        args.num_retrievals,
        args.questions_after,
        ir_config=TRAINING_RETRIEVAL_CONFIG,
        reasoning_config=TRAINING_REASONING_CONFIG,
        output_dir="data_point_generation",
    )


if __name__ == "__main__":
    asyncio.run(main())
