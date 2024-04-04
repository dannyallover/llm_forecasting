# Standard library imports
import asyncio
from datetime import datetime
import logging

# Related third-party imports
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Local application/library-specific imports
from config.constants import CHARS_PER_TOKEN, DEFAULT_RETRIEVAL_CONFIG
import information_retrieval
import model_eval
import summarize
from prompts.prompts import PROMPT_DICT
from utils import metrics_utils, string_utils, utils

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def tfidf_cosine_sim(text_list):
    """
    Calculate the average cosine similarity between texts in a given list.

    This function computes the Term Frequency-Inverse Document Frequency (TF-IDF)
    for a list of texts, and then calculates the cosine similarity between each pair
    of texts. The function returns the average of these similarity scores.
    If the provided list contains less than two texts, the function returns 0,
    as similarity calculation is not applicable.

    Args:
        text_list (List[str]): A list of strings where each string is a text document.

    Returns:
        float: The average cosine similarity between each pair of texts in the list.
           Returns 0 if the list contains less than two text documents.

    """
    if len(text_list) < 2:
        # If there's only one or no text, similarity doesn't make sense
        return 0

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(text_list)
    similarity_matrix = cosine_similarity(tfidf_matrix)

    # Exclude diagonal elements and divide by the number of comparisons
    upper_triangle_indices = np.triu_indices_from(similarity_matrix, k=1)
    average_similarity = np.mean(similarity_matrix[upper_triangle_indices])

    return average_similarity


def extract_rating_from_response(response_str):
    """
    Extract the rating from the response string returned by LLM.

    Args:
        response_str (str): Response string returned by LLM (such as OpenAI's API).

    Returns:
        float: The rating extracted from the response string (at the scale of 1-4).
    """
    # If the rating is the first word, return it
    rating = response_str.split()[0]
    if rating.isnumeric():
        return float(rating)
    else:  # If the rating is not the first word, try to find it after "Rating:"
        loc = response_str.split("Rating:")
        if len(loc) > 1:
            # Assuming the it is followed by "Rating:" (after removing spaces)
            rating = loc[1].split()[0]
            if rating.isnumeric():
                return float(rating)
            else:
                return 1.0  # If the rating is not numeric, return 1


async def get_relevance_ratings(
    articles,
    method="title_250_tokens",
    prompt_template=PROMPT_DICT["ranking"]["0"],
    question=None,
    background=None,
    resolution_criteria=None,
    dates=None,
    model_name="gpt-3.5-turbo-1106",
    temperature=0.0,
    use_summary=False,
):
    """
    Compute the relevance ratings for a list of articles given a question and background information.

    The method calls OpenAI's API to generate a rating for each article, using config parameters.

    Args:
        articles (list of article obj): List of articles to be rated.
        method (str): Method for generating relevance ratings.
            Options are "full-text", "title_250_tokens" and "title".
        question (str): Forecast question to be answered.
        background_info (str): Background information of the question.

    Returns:
        list: List of relevance ratings for each article.
    """
    if method == "full-text":
        prompts = [
            string_utils.get_prompt(
                prompt_template[0],
                prompt_template[1],
                question=question,
                background=background,
                resolution_criteria=resolution_criteria,
                dates=dates,
                article="\n---\nTitle: {title}\n\n{text}\n---\n".format(
                    title=article.title,
                    text=(
                        article.text_cleaned[:40000]
                        if not use_summary
                        else article.summary[:40000]
                    ),
                ),
            )
            for article in articles
        ]
    elif method == "title_250_tokens":
        prompts = [
            string_utils.get_prompt(
                prompt_template[0],
                prompt_template[1],
                question=question,
                background=background,
                resolution_criteria=resolution_criteria,
                dates=dates,
                article="\n---\n(Below I provide the first 250 tokens of the article.)\n\nTitle: {title}\n\n{text}\n---\n".format(
                    title=article.title,
                    text=article.text_cleaned[: 250 * CHARS_PER_TOKEN],
                ),
            )
            for article in articles
        ]
    elif method == "title":
        prompts = [
            string_utils.get_prompt(
                prompt_template[0],
                prompt_template[1],
                question=question,
                background=background,
                resolution_criteria=resolution_criteria,
                dates=dates,
                article="\n---\n(Below I provide the title of the article.)\n\nTitle: {title}\n---\n".format(
                    title=article.title
                ),
            )
            for article in articles
        ]
    relevance_rating_tasks = [
        model_eval.get_async_response(
            prompt,
            model_name=model_name,
            temperature=temperature,
        )
        for prompt in prompts
    ]
    all_responses = await asyncio.gather(*relevance_rating_tasks)
    for i in range(len(all_responses)):  # save reasoning for rating
        articles[i].relevance_rating_reasoning = all_responses[i]
    ratings = [extract_rating_from_response(response) for response in all_responses]
    return ratings


def _sort_and_filter_articles(articles, default_date, threshold=4, sort_by="date"):
    """
    Sorts articles based on their ratings and filters out articles with a relevance score <= a given threshold.

    Args:
        articles (list of obj): List of articles (objects).
            The relevance rating of each article is stored in the "relevance_rating" field.
            This field may be cosine similarity or a relevance rating (e.g., at the scale of 1-6).
        default_date (str): The default date to use if an article's publish date is not available.
            relevance_threshold (int): The minimum relevance score required to keep an article (default is 2)
        threshold (int, optional): The minimum relevance score required to keep an article (default is 4)
        sort_by (str, optional): The method for sorting the articles.
            Options are "date", "relevance" and both (default is "date").
            If "both" is selected, the method returns two lists of articles,
            sorted by date and relevance, respectively.

    Returns:
        list: List of sorted and filtered articles

    Raises:
        ValueError: If the lengths of articles and ratings are not the same
    """
    # Filter out articles with a relevance score below the relevance_threshold
    filtered_articles = [
        article
        for article in articles
        if article.relevance_rating and article.relevance_rating >= threshold
    ]
    # Sort by relevance ratings, from high to low
    if sort_by == "relevance":
        return sorted(filtered_articles, key=lambda x: x.relevance_rating, reverse=True)
    elif sort_by == "date":
        # fill in default date if publish date is not available
        for article in filtered_articles:
            if not article.publish_date:
                article.publish_date = datetime.strptime(default_date, "%Y-%m-%d")
        return sorted(
            filtered_articles, key=lambda x: x.publish_date.date(), reverse=True
        )
    logger.error(f"Not a valid sorting criterion: {sort_by}")
    return filtered_articles


async def rank_articles(
    articles,
    method="llm-rating",  # alternative is "embedding"
    method_llm="title_250_tokens",  # alternative is "full-text" or "title"
    cosine_similarity_threshold=0.72,
    relevance_rating_threshold=4,
    prompt_template=PROMPT_DICT["ranking"]["0"],
    question=None,
    background=None,
    resolution_criteria=None,
    dates=None,
    sort_by="date",
    model_name="gpt-3.5-turbo-1106",
    temperature=0.0,
    sort_and_filter=True,
):
    """
    Rank and filter a list of articles given a question and background information.

    The method updates the articles' objects, by filling in the "relevance_rating"
    field to each article.

    Args:
        articles (list of obj): List of articles to be ranked.
        method (str, optional): Method for ranking articles. Options are "llm-rating" and "embedding".
            "llm-rating": Use LLM to generate a relevance rating for each article.
            "embedding": Use OpenAI's embedding model to get cosine similarity between the question and each article.
        method-llm (str, optional): Method for generating relevance ratings if llm-rating is used.
            Options are "full-text", "title_250_tokens" and "title".
        cosine_similarity_threshold (float, optional): The minimum cosine similarity required to keep an article (default is 0.71).
            This is only used if method is "embedding".
        relevance_rating_threshold (int, optional): The minimum relevance score required to keep an article (default is 4).
        prompt_template (tuple, optional): Prompt for generating the relevance rating.
            This is only used if method is "llm-rating".
        question (str, optional): Forecast question to be answered.
        background (str, optional): Background information of the question.
        resolution_criteria (str, optional): Resolution criteria of the question.
        dates (list of str, optional): Date range for the news retrieval (e.g. ["2021-01-01", "2021-01-31"]).
        sort_by (str, optional): The method for sorting the articles. Options are "date" and "relevance" (default is "date").
        model_name (str, optional): Name of the LLM model to use (default is "gpt-3.5-turbo-1106").
        temperature (float, optional): Temperature for LLM (default is 0.0).
        sort_and_filter (bool, optional): Whether to sort and filter the articles (default is True).

    Returns:
        list of obj: List of sorted and filtered articles.
    """
    if len(articles) == 0:
        return []
    if method == "llm-rating":
        ratings = await get_relevance_ratings(
            articles,
            method=method_llm,  # "title_250_tokens" by default
            prompt_template=prompt_template,
            question=question,
            background=background,
            resolution_criteria=resolution_criteria,
            dates=dates,
            model_name=model_name,
            temperature=temperature,
        )
        # Update the articles' objects, by adding a "relevance_rating" field.
        for i, rating in enumerate(ratings):
            articles[i].relevance_rating = rating
            logger.info(
                "Article {} gets rating: {}".format(
                    articles[i].title, articles[i].relevance_rating
                )
            )
        # Sort and filter the articles
        if sort_and_filter:
            return _sort_and_filter_articles(
                articles,
                dates[1],
                threshold=relevance_rating_threshold,
                sort_by=sort_by,
            )
    elif method == "embedding":
        # question and background are concatenated, then embedded; this is a
        # list of Embedding objects (with one element)
        q_embedding, a_embeddings = get_question_article_embeddings(
            articles, question, background
        )
        # Compute the cosine similarity between the question and each article
        for i, a_embedding in enumerate(
            a_embeddings
        ):  # each a_embedding is an Embedding object, with a_embedding.embedding being a list of floats
            articles[i].relevance_rating = metrics_utils.cosine_similarity(
                q_embedding[0].embedding, a_embedding.embedding
            )
        # Sort and filter the articles
        if sort_and_filter:
            return _sort_and_filter_articles(
                articles,
                dates[1],
                threshold=cosine_similarity_threshold,
                sort_by=sort_by,
            )
    return articles


def get_question_article_embeddings(articles, question, background):
    """
    Compute the embeddings for the question and each article.

    Args:
        articles (list of obj): List of articles to be ranked.
        question (str): Forecast question to be answered.
        background (str): Background information of the question.

    Returns:
        tuple: Tuple containing the question embedding and a list of article embeddings.
    """
    article_texts = [article.text_cleaned[:18000] for article in articles]
    q_embedding = model_eval.get_openai_embedding(
        [
            "Question: {question}\n\nBackground:{background}".format(
                question=question, background=background
            )
        ]
    )
    a_embeddings = model_eval.get_openai_embedding(article_texts)
    return q_embedding, a_embeddings


async def retrieve_summarize_and_rank_articles(
    question,
    background_info,
    resolution_criteria,
    date_range,
    urls=None,
    return_intermediates=False,
    config=DEFAULT_RETRIEVAL_CONFIG,
):
    """
    Retrieve, summarize and rank articles given a *single* question and its background information.

    The method works by first extracing keywords from the question and background information,
        and then retrieving relevant articles using these keywords.

    Args:
        question (str): Forecast question to be answered.
        background_info (str): Background information of the question.
        resolution_criteria (str): Resolution criteria of the question.
        date_range (list of str): Date range for the news retrieval (e.g. ["2021-01-01", "2021-01-31"]).
            The first date is the start date and the second date is the end date.
        urls (list of str, optional): List of additional URLs to extract webpages from.
        return_intermediates (bool, optional): Whether to return intermediate outputs of the retrieval system (default is False).
        config (dict, optional): Dictionary containing the configuration parameters. See config/constants.py for details.

    Returns:
        list: List of sorted and filtered articles relevant to the question.
    """
    # Step 1: Extract search query terms, including the question itself
    logger.info(
        "Finding {} search query keywords via LLM...".format(
            config["NUM_SEARCH_QUERY_KEYWORDS"]
        )
    )
    (
        search_queries_list_nc,
        search_queries_list_gnews,
        _,
        _,
        _,
        _,
    ) = await information_retrieval.get_search_queries_for_all_sources(
        config["SEARCH_QUERY_PROMPT_TEMPLATES"],
        config["NUM_SEARCH_QUERY_KEYWORDS"],
        date_range,
        question,
        background_info=background_info,
        resolution_criteria=resolution_criteria,
    )
    # Flatten and deduplicate the search queries
    search_queries_list_nc = utils.flatten_list(search_queries_list_nc)
    search_queries_list_gnews = utils.flatten_list(search_queries_list_gnews)
    search_queries_list_nc = list(set(search_queries_list_nc))
    search_queries_list_gnews = list(set(search_queries_list_gnews))
    logger.info(f"Search queries for NC: {search_queries_list_nc}")
    logger.info(f"Search queries for GNews: {search_queries_list_gnews}")
    # Step 2: Retrieve articles using the search query terms
    articles = []
    articles = information_retrieval.get_articles_from_all_sources(
        search_queries_list_gnews,
        search_queries_list_nc,
        date_range,
        num_articles=config["NUM_ARTICLES_PER_QUERY"],
        length_threshold=200,
    )
    articles = information_retrieval.deduplicate_articles(articles)
    articles_unfiltered = articles.copy()
    # Step 2.5 (optional): filter articles via quick embedding model
    if config.get("PRE_FILTER_WITH_EMBEDDING") and len(articles) >= 25:
        logger.info(f"Filtering {len(articles)} articles with embedding model.")
        cos_sim = []
        q_embedding, a_embeddings = get_question_article_embeddings(
            articles, question, background_info
        )
        # each a_embedding is an Embedding object, with a_embedding.embedding being a list of floats
        for a_embedding in a_embeddings:
            cos_sim.append(
                metrics_utils.cosine_similarity(
                    q_embedding[0].embedding, a_embedding.embedding
                )
            )
        logger.info(
            f"Get {len(cos_sim)} cosine similarities for {len(articles)} articles."
        )
        sim_threshold = config["PRE_FILTER_WITH_EMBEDDING_THRESHOLD"]
        # If there are too many articles, use a higher threshold
        if len(articles) >= 100:
            sim_threshold = 0.36
        logger.info(f"Using {sim_threshold} as the cosine similarity threshold.")
        # filter articles with cosine similarity below threshold
        articles = [
            article for i, article in enumerate(articles) if cos_sim[i] > sim_threshold
        ]
        logger.info(f"{len(articles)} articles survived the embedding filtering.")
    # Step 3: Filter irrelevant articles and rank the remaining articles (by
    # recency or relevance)
    ranked_articles = await rank_articles(
        articles,
        method=config["RANKING_METHOD"],  # "llm-rating" by default
        # "title_250_tokens" by default
        method_llm=config["RANKING_METHOD_LLM"],
        prompt_template=config["RANKING_PROMPT_TEMPLATE"],
        question=question,
        dates=date_range,
        resolution_criteria=resolution_criteria,
        background=background_info,
        sort_by=config["SORT_BY"],
        relevance_rating_threshold=config["RANKING_RELEVANCE_THRESHOLD"],
        cosine_similarity_threshold=config.get(
            "RANKING_COSINE_SIMILARITY_THRESHOLD", 0.5
        ),
        model_name=config["RANKING_MODEL_NAME"],
        temperature=config["RANKING_TEMPERATURE"],
    )
    logger.info("Finished ranking the articles!")
    # Step 3.5 (optional): Extract webpages linked in the additional URLs
    if config.get("EXTRACT_BACKGROUND_URLS") and urls and len(urls) > 0:
        articles_from_urls = []
        urls = list(set(urls))  # remove duplicates
        for link in urls:
            # If the link is not already in the ranked articles, extract the
            # webpage text and add it to the list of articles
            if link not in [article.canonical_link for article in ranked_articles]:
                article = information_retrieval.retrieve_webpage_text(
                    link, date_range[1]
                )
                # If the article is retrieved fully, add it to the list of articles
                if article and article.text_cleaned and len(article.text_cleaned) > 200:
                    article.search_term = "additional-url"
                    article.relevance_rating = 6  # highest relevance rating
                    articles_from_urls.append(article)
        # add articles from urls to the top of the list
        if len(articles_from_urls) > 0:
            ranked_articles = articles_from_urls + ranked_articles
    # Step 4: Summarize articles. The method updates the articles object in
    # place, by adding a "summary" field to each article.
    prompt = config["SUMMARIZATION_PROMPT_TEMPLATE"][0].format(
        question=question,
        background=background_info,
        article="{article}",
        # The article text will be inserted here by the `summarize_articles` method.
    )
    # If a threshold NUM_SUMMARIES_THRESHOLD is given, only summarize
    # the top NUM_SUMMARIES_THRESHOLD articles
    if config.get("NUM_SUMMARIES_THRESHOLD"):
        logger.info(
            f"Summarizing the top {config['NUM_SUMMARIES_THRESHOLD']} articles."
        )
        ranked_articles = ranked_articles[: config["NUM_SUMMARIES_THRESHOLD"]]
    await summarize.summarize_articles(
        ranked_articles,
        prompt=prompt,
        update_object=True,
        temperature=config["SUMMARIZATION_TEMPERATURE"],
        model_name=config["SUMMARIZATION_MODEL_NAME"],
    )
    logger.info(f"Finished summarizing the {len(ranked_articles)} articles!")
    # Return the ranked articles, along with the articles and keywords (if
    # return_intermediates is True)
    if return_intermediates:
        return (
            ranked_articles,
            articles_unfiltered,
            search_queries_list_gnews,
            search_queries_list_nc,
        )
    else:
        return ranked_articles


async def all_retrieve_summarize_rank_articles(
    questions,
    background_infos,
    date_ranges,
    num_articles=5,
    use_newscatcher=True,
    return_intermediates=False,
    config=DEFAULT_RETRIEVAL_CONFIG,
):
    """
    Create wrapper that lets you retrieve, summarize, and rank articles for multiple questions.

    Args:
        questions (str): Forecast questions to be answered.
        background_info (str): Background information of the question.
        date_range (list of str): Date range for the news retrieval (e.g. ["2021-01-01", "2021-01-31"]).
            The first date is the start date and the second date is the end date.

    Returns:
        list: List of sorted and filtered articles relevant to the question.
    """
    articles_by_question = {}
    for index in range(len(questions)):
        articles_by_question[questions[index]] = (
            await retrieve_summarize_and_rank_articles(
                questions[index],
                background_infos[index],
                date_ranges[index],
                num_articles,
                use_newscatcher,
                return_intermediates,
                config,
            )
        )
    return articles_by_question
