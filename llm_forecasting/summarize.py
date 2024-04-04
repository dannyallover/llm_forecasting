# Standard library imports
import asyncio
import logging
import time

# Local application/library-specific imports
from config.constants import MODEL_TOKEN_LIMITS
import model_eval
from prompts.prompts import PROMPT_DICT
from utils import model_utils

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def concat_summaries(articles, return_summaries_list=False):
    """
    Combine the summaries of various articles into a single, cohesive string,
    ensuring to incorporate each article's title, publication date, and a
    sequential index for easy reference.

    Args:
        articles (list of article objects): List of article objects with
            a 'summary' field.
        return_summaries_list (bool, optional): Whether to return the list of
            summaries as well. Defaults to False.

    Returns:
        str: A string containing the concatenated summaries of the articles.

        Example output:
        ---
        ARTICLES
        [1] Title 1 (published on 2021-01-01)
            ....
        [2] Title 2 (published on 2021-01-02)
            ....
        ----

        If return_summaries_list is True, then the function returns a tuple
        containing the concatenated summaries string and the list of summaries.
    """
    if not articles:
        return "---\nNo articles were retrieved for this question.\n----"
    article_summaries = [
        f"[{index}] {article.title} (published on {(article.publish_date.date() if article.publish_date else 'unknown date')})\nSummary: {article.summary}\n"
        for index, article in enumerate(articles, start=1)
    ]
    concatenated_summaries_str = (
        "---\nARTICLES\n" + "\n".join(article_summaries) + "----"
    )
    if return_summaries_list:
        return concatenated_summaries_str, article_summaries
    return concatenated_summaries_str


def split_text_into_chunks(text, model_name, token_limit):
    """
    Split the text into chunks, ensuring each chunk is below the token limit.

    Args:
        text (str): Input text to be split.
        model_name (str): Name of the model to be used for token counting.
        token_limit (int): Maximum number of tokens allowed per chunk.

    Returns:
        list: List of text chunks.
    """
    words = text.split()
    current_chunk = []
    current_chunk_tokens = 0
    chunks = []

    for word in words:
        word_tokens = model_utils.count_tokens(word, model_name)
        if current_chunk_tokens + word_tokens > token_limit:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
            current_chunk_tokens = word_tokens
        else:
            current_chunk.append(word)
            current_chunk_tokens += word_tokens

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


def recursive_summarize(
    text,
    model_name,
    prompt,
    output_token_length=None,
    temperature=0,
):
    """
    Recursively summarize the text until the summary fits within the context
    window.

    Args:
        text (str): The input text to be summarized.
        model_name (str): Name of the model to be used for summarization.
        primary_prompt (str): Main prompt to guide the summarization.
        output_token_length (int, optional): Desired word count of the final
        summary. Defaults to None.
        temperature (float, optional): Sampling temperature for the completion.
        Defaults to 0.

    Returns:
        str: Summarized text.
    """
    start_time = time.time()

    total_tokens = model_utils.count_tokens(text, model_name)
    logger.info(f"Total number of tokens of the given text: {total_tokens}")

    if total_tokens <= MODEL_TOKEN_LIMITS[model_name]:
        if output_token_length:
            prompt += (
                f"\n\nAlso, ensure the summary is under {output_token_length} words.\n"
            )

        output = model_eval.get_response_from_model(
            model_name=model_name,
            prompt=prompt.format(article=text),
            max_tokens=output_token_length,
        )

        end_time = time.time()
        elapsed_time = end_time - start_time
        logger.info(f"Time taken for summarization: {elapsed_time:.2f} seconds")
        logger.info("Finished summarizing the article!")
        return output
    else:
        token_limit = MODEL_TOKEN_LIMITS[model_name] - 1000
        chunks = split_text_into_chunks(text, model_name, token_limit)

        summarized_chunks = []
        for chunk in chunks:
            summarized_chunk = recursive_summarize(
                chunk,
                model_name,
                prompt,
                output_token_length,
                temperature,
            )
            summarized_chunks.append(summarized_chunk)

        summarized_text = " ".join(summarized_chunks)
        return recursive_summarize(
            summarized_text,
            model_name,
            prompt,
            output_token_length,
            temperature,
        )


async def summarize_articles(
    articles,
    model_name="gpt-3.5-turbo-1106",
    prompt=PROMPT_DICT["summarization"]["0"][0],
    temperature=0.2,
    update_object=True,
    inline_questions=[],
):
    """
    Summarizes a list of articles asynchronously.

    Long articles are truncated down to token limit and summarized separately.

    Example usage:
        >> summarized_results = await summarize_articles(articles)

    Args:
        articles (list of obj): List of article objects. Each article object should have the following fields:
            text_cleaned (str): Full text of the article.
        model_name (str, optional): Name of the OpenAI model to be used for summarization (defaults to "gpt-3.5-turbo-1106").
        prompt (str, optional): Prompt to use for the API call (defaults to PROMPT_DICT["summarization"]["0"][0]).
            This is not the full prompt, but contains a placeholder for the article text.
        output_token_length (int, optional): Desired word count of the final summary. Defaults to None.
        temperature (float, optional): Sampling temperature for the completion. Defaults to 0.2.
        update_object (bool, optional): Whether to update the article object with the summary (defaults to True).
        inline_questions (dict, optional): List containing the inline questions. Defaults to [].

    Returns:
        dict: Dictionary containing the summarized results for each article.
        Example output:
        ---
        {
            "Title 1": "Summary 1",
            "Title 2": "Summary 2",
            ...
        }
        ---
        Also, the article objects are updated with the summaries if update_object is True.
    """
    summarized_results = {}
    # Truncate articles that are too long
    for article in articles:
        if (  # exceeds token limit
            model_utils.count_tokens(article.text_cleaned, model_name)
            > MODEL_TOKEN_LIMITS[model_name] - 1000
        ):
            article.text_cleaned = split_text_into_chunks(
                article.text_cleaned, model_name, MODEL_TOKEN_LIMITS[model_name] - 1000
            )[0]
    # Summarize all articles asynchronously
    logger.info(f"Async summarizing {len(articles)} short articles")
    all_summaries = await async_summarize(
        articles,
        prompt,
        update_object=update_object,
        temperature=temperature,
        model_name=model_name,
        inline_questions=inline_questions,
    )
    for i, article in enumerate(articles):
        summarized_results[article.title] = all_summaries[i]
    return summarized_results


async def async_summarize(
    articles,
    prompt=PROMPT_DICT["summarization"]["0"][0],
    update_object=True,
    model_name="gpt-3.5-turbo-1106",
    temperature=0.2,
    inline_questions=[],
):
    """
    Asynchronously summarizes a list of articles.
    Example usage:
        >> all_summaries = await async_summarize(articles)
    The order of the returned summaries is the same as the order of the input articles.
    All summaries are stored in the "summary" field of each article object, if update_object is True.

    Args:
        articles (list of obj): List of article objects. Each article object should have the following fields:
            text_cleaned (str): Full text of the article.
        prompt (str): Prompt to use for the API call (defaults to PROMPT_DICT["summarization"]["0"][0]).
            This is not the full prompt, but contains a placeholder for the article text.
        update_object (bool): Whether to update the article object with the summary (defaults to True).

    Returns:
        list of str: List of summaries (str) for each article.
    """
    if len(articles) == 0 or not articles:
        return []
    if inline_questions:
        question = inline_questions["title"]
        background = inline_questions["background"]
        resolution_criteria = inline_questions["resolution_criteria"]
        prompts = [
            prompt.format(
                question=question,
                background=background,
                resolution_criteria=resolution_criteria,
                article=article.text_cleaned,
            )
            for article in articles
        ]
    else:
        prompts = [prompt.format(article=article.text_cleaned) for article in articles]

    summarization_tasks = [
        model_eval.get_async_response(
            prompt, model_name=model_name, temperature=temperature
        )
        for prompt in prompts
    ]
    all_summaries = await asyncio.gather(*summarization_tasks)
    if update_object:
        for i, article in enumerate(articles):
            article.summary = all_summaries[i]
    return all_summaries
