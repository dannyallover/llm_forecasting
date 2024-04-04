# Standard library imports
import asyncio
import logging
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta

# Related third-party imports
from gnews import GNews
import newspaper
from newscatcherapi import NewsCatcherApiClient
import requests

# Local application/library-specific imports
from config.constants import IRRETRIEVABLE_SITES
from config.keys import NEWSCASTCHER_KEY
from config.site_whitelist import NEWS_WHITE_LIST
import model_eval
from utils import time_utils, string_utils

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
if NEWSCASTCHER_KEY:
    newscatcherapi = NewsCatcherApiClient(x_api_key=NEWSCASTCHER_KEY)
WIKIPEDIA_API_ENDPOINT = "https://en.wikipedia.org/w/api.php"


class NewscatcherArticle:
    """
    Article object processed by the returned JSON from the Newscatcher API.

    Note: The "summary" field of Newscatcher is actually the full text of the article.
    """

    def __init__(self, article_dict, search_term):
        self.title = article_dict.get("title", "")
        self.author = article_dict.get("author")
        self.published_date = article_dict.get("published_date", "")  # string
        self.published_date_precision = article_dict.get("published_date_precision")
        self.link = article_dict.get(
            "link", ""
        )  # Full url to the article page (not the domain)
        self.clean_url = article_dict.get(
            "clean_url"
        )  # Domain of the article (such as cnn.com)
        self.excerpt = article_dict.get("excerpt")
        if article_dict.get("summary") is None:  # wikipedia case
            self.text = article_dict.get("text", "")
        else:  # newscatcher summary is actually the full text
            self.text = article_dict.get("summary", "")
        self.rights = article_dict.get("rights")
        self.rank = article_dict.get("rank")
        self.topic = article_dict.get("topic")
        self.country = article_dict.get("country")
        self.language = article_dict.get("language")
        self.authors = article_dict.get("authors")
        self.media = article_dict.get("media")
        self.is_opinion = article_dict.get("is_opinion")
        self.twitter_account = article_dict.get("twitter_account")
        self._score = article_dict.get("_score")
        self._id = article_dict.get("_id")

        # Alternative names for the same fields (mostly for compatibility with
        # GNews)
        if self.published_date is not None:
            try:  # datetime object, parsed from string
                self.publish_date = datetime.strptime(  # newscatcher
                    self.published_date, "%Y-%m-%d %H:%M:%S"
                )
            except ValueError:  # wikipedia
                self.publish_date = datetime.fromisoformat(
                    self.published_date.rstrip("Z")
                )
        if self.published_date is None:
            logger.error(
                f"Published date is None for {self.link} (should be parsed from {self.published_date})."
            )
        self.meta_site_name = self.clean_url
        self.canonical_link = self.link
        self.text_cleaned = self.text
        self.search_term = search_term  # The search term that retrieved this article
        self.summary = self.text  # Initialize the summary field to the full text
        self.relevance_rating = None  # Initialize the relevance rating to None
        self.relevance_rating_reasoning = ""


def is_irretrievable_site(url, site_list=IRRETRIEVABLE_SITES):
    """
    Check if the given URL contains any of the substrings from the site list.

    Additionally, |site_list| contains site URLs that are not retrievable for getting full texts.

    Args:
        url (str): The URL to check. If it is not a string, returns True.
        site_list (list, optional): A list of strings representing parts of URLs to check against.

    Returns:
        bool: True if the URL contains any of the listed strings, False otherwise.
    """
    if isinstance(url, str) is False:  # url is not a string, then it is not retrievable
        return True
    return any(site in url for site in site_list)


def is_whitelisted(url, whitelist=NEWS_WHITE_LIST):
    """
    Check if the given URL is in the whitelist.

    Args:
        url (str): The URL to check. If it is not a string, returns True.
        whitelist (set, optional): A set of domains representing parts of URLs to check against.

    Returns:
        bool: True if the URL contains any of the listed strings, False otherwise.
    """
    if isinstance(url, str) is False:  # url is not a string, then it is bad
        return False
    return any(site in url for site in whitelist)


def get_urls_from_text(text):
    """
    Automatically detect text format (HTML, Markdown, or Generic) and extract URLs.

    Args:
        text (str): The text string to extract the URLs from.

    Returns:
        list[str]: The URLs extracted from the text.
    """
    urls = []

    if text:
        # Check for HTML format by looking for <a href=""> tags
        if '<a href="' in text:
            urls = re.findall(r'href="(https?://[^\s]+)"', text)
        # Check for Markdown format by looking for [text](url) patterns
        elif re.search(r"\[.*?\]\(https?://[^\s]+\)", text):
            urls = re.findall(r"\((https?://[^\s]+)\)", text)
        # If neither HTML nor Markdown, assume it's a generic format
        else:
            urls = re.findall(r"https?://[^\s,;?!()]+", text)

    return urls


def clean_search_queries(search_queries):
    """
    Newscatcher does not handle certain characters. It will report error if any of these characters are present in the search queries.
    This function removes those characters from the search queries.

    Args:
        search_queries (list): A list of search queries. Will be modified in place.

    Returns:
        None. The search_queries list is modified in place.
    """
    characters_to_remove = [
        "[",
        "]",
        "/",
        "\\\\",
        "%5B",
        "%5D",
        "%2F",
        "%5C",
        ":",
        "%3A",
        "^",
        "%5E",
    ]
    for i in range(len(search_queries)):
        for char in characters_to_remove:
            search_queries[i] = search_queries[i].replace(char, "")


def extract_search_queries(model_response):
    """
    Extract search queries from the last line of the model's response using regex,
    ensuring each query contains only alphabets, numbers, and certain punctuation marks.

    Args:
        model_response (str): The full text of the model's response.

    Returns:
        list: A list of cleaned search queries.
    """
    second_last_line = model_response.strip().split("\n")[-2]
    if "Search Queries:" in second_last_line:
        # Extract the last line
        last_line = model_response.strip().split("\n")[-1]
        return extract_search_queries_from_line(last_line)
    else:
        # Flatten everything after the "Search Queries:" part
        search_queries_part = model_response.split("Search Queries:", 1)[1]
        flattened_string = " ".join(
            line.strip() for line in search_queries_part.splitlines()
        )
        return extract_search_queries_from_line(flattened_string)


def extract_search_queries_from_line(line):
    # Split the last line by semicolons into search queries
    substrings = line.split(";")
    # Filter out empty strings, strip whitespace and remove double quotes
    queries = [q.strip(".-; ").replace('"', "") for q in substrings if q.strip()]
    queries = [q for q in queries if q != ""]
    return queries


def deduplicate_articles(articles):
    """
    Deduplicates a list of NewscatcherArticle objects, removing duplicates based on the article URLs and titles.

    Args:
        articles (list of NewscatcherArticle): A list of NewscatcherArticle objects.

    Returns:
        list of NewscatcherArticle: A list of NewscatcherArticle objects with no duplicates.
    """
    unique_articles = []
    unique_urls = set()
    unique_titles = set()
    for article in articles:
        if not isinstance(article.title, str) or not isinstance(
            article.canonical_link, str
        ):
            continue
        if (
            article.canonical_link.lower() not in unique_urls
            and article.title.lower() not in unique_titles
        ):
            unique_articles.append(article)
            unique_urls.add(article.canonical_link.lower())
            unique_titles.add(article.title.lower())
    return unique_articles


def get_newscatcher_articles(
    search_terms,
    retrieval_dates,
    num_articles=5,
    max_results=20,
    length_threshold=200,
    to_rank=10000,
):
    """
    Retrieve a list of news articles for each search term within the specified date range.

    This function uses the Newscatcher API to fetch news articles. For each search term provided, it retrieves articles in English, sorted by relevancy or date, up to a specified maximum count.

    It filters out None articles or those from irretrievable sites.

    Args:
        search_terms (list of str): A list of search terms to query articles for.
        retrieval_dates (list of str): A list containing two date strings (start and end dates)
            in 'YYYY-MM-DD' format to specify the date range for article retrieval.
        num_articles (int, optional): The number of articles to retrieve for each search term.
        max_results (int, optional): The maximum number of articles to retrieve for each search term.
            Defaults to 20. This is the `page_size` in the Newscatcher API.
        length_threshold (int, optional): The minimum length of the article text. Defaults to 200.
        to_rank (int, optional): The maximum page rank of websites to retrieve articles from. Lower ranked
            websites (greater than to_rank) are not retrieved. They tend to be shady websites that are not good
            sources of information. (TODO: This parameter may be tuned.)

    Returns:
        list of objects: A list where each element is a NewscatcherArticle object.
        Same output as `retrieve_articles_fulldata`, though with different object class.
    """
    assert len(retrieval_dates) == 2, "retrieval_dates should be a list of two strings."
    # return empty set for invalid date ranges.
    if not NEWSCASTCHER_KEY:
        logger.error("Skipping Newscatcher since no key is set.")
        return []
    if not time_utils.is_more_recent(retrieval_dates[0], retrieval_dates[1]):
        logger.error(
            "retrieval_dates[1] {} should be strictly more recent than retrieval_dates[0] {}.".format(
                retrieval_dates[1], retrieval_dates[0]
            )
        )
        return []
    if len(search_terms) == 0:
        return []
    retrieved_articles = []
    clean_search_queries(search_terms)
    for i in range(len(search_terms)):  # Initialize a query for each search term
        try:
            response = newscatcherapi.get_search(
                q=search_terms[i],
                lang="en",
                sort_by="relevancy",  # or date
                page_size=max_results,
                from_=retrieval_dates[0],
                to_=retrieval_dates[1],
                to_rank=to_rank,  # filter out low ranked websites
            )
        except Exception as e:  # catch potential timeout error
            logger.error(e)
            continue

        articles = []
        if response["status"] != "No matches for your search.":
            # A list of dictionaries (parsed from JSON). Take the top
            # num_articles articles.
            articles = response["articles"][:num_articles]
            # Remove None and articles too short
            articles = [
                article
                for article in articles
                if article is not None
                and isinstance(article["summary"], str)  # 'summary' may be None
                and len(article["summary"]) > length_threshold
            ]
            # Collect the results into an object. Update each article with the
            # search term that retrieved it.
            articles = [
                NewscatcherArticle(article, search_terms[i]) for article in articles
            ]
        logger.info(
            f"Retrieved {len(articles)} articles for {search_terms[i]} via Newscatcher."
        )
        # Add the articles to the list of retrieved articles
        retrieved_articles.extend(articles)

    # Deduplicate articles based on the article URLs and titles
    unique_articles = deduplicate_articles(retrieved_articles)
    return unique_articles


def get_gnews_articles(search_terms, retrieval_dates, max_results=20):
    """
    Fetch news articles from Google News.

    Args:
        search_terms (list of str): Search queries.
        retrieval_dates (list of str): Start and end dates ['YYYY-MM-DD',
            'YYYY-MM-DD'].
        max_results (int, optional): Max articles per term (default 20).

    Returns:
        List of lists containing article data for each search term.
        Each article is a dictionary that contains title, description, url,
        published date, and publisher entries.

        The collection of articles may contain duplicates.
    """
    assert len(retrieval_dates) == 2, "retrieval_dates should be a list of two strings."
    #  return empty set for invalid date ranges.
    if not time_utils.is_more_recent(retrieval_dates[0], retrieval_dates[1]):
        logger.error(
            "retrieval_dates[1] {} should be strictly more recent than retrieval_dates[0] {}.".format(
                retrieval_dates[1], retrieval_dates[0]
            )
        )
        return []
    retrieved_articles = []
    for i in range(len(search_terms)):
        # Initialize GNews object with search terms and retrieval dates
        google_news = GNews(
            language="en",
            start_date=time_utils.convert_date_string_to_tuple(retrieval_dates[0]),
            end_date=time_utils.convert_date_string_to_tuple(retrieval_dates[1]),
            max_results=max_results,
        )
        articles = google_news.get_news(search_terms[i])
        # Remove None or articles from irretrievable sites
        articles = [
            article
            for article in articles
            if article is not None
            and "publisher" in article
            and "href" in article["publisher"]
            and not is_irretrievable_site(article["publisher"]["href"])
        ]
        # Update each article with the search term that retrieved it
        for article in articles:
            article["search_term"] = search_terms[i]
        logger.info(
            f"Retrieved {len(articles)} articles for {search_terms[i]} via GNews."
        )
        # Collect all articles into a single list
        retrieved_articles.append(articles)
    return retrieved_articles


def retrieve_gnews_articles_fulldata(
    retrieved_articles, num_articles=5, length_threshold=200
):
    """
    Retrieve a specified number of full articles from a list of article groups.
    We remove duplicates and short articles.

    The duplicated articles (same url) are retrieved only once.

    Args:
        retrieved_articles (list[list[dict]]): A list of lists, where each
            inner list contains article dictionaries.
        num_articles (int, optional): The number of articles to retrieve from
            each group. Defaults to 2.
        length_threshold (int, optional): The minimum length of the article
            text. Defaults to 200.

    Returns:
        list: A flat list of full article data, with no duplicates.
    """
    google_news = GNews()
    fulltext_articles = []
    unique_urls = set()

    for articles_group in retrieved_articles:
        articles_added = 0
        for article in articles_group:
            if articles_added >= num_articles:  # we have enough articles
                break
            if article["url"] in unique_urls:  # duplicated article
                continue
            else:  # new article, add to the set of unique urls
                unique_urls.add(article["url"])
            full_article = google_news.get_full_article(article["url"])
            logger.info(f"Retrieved full article text for {article['url']}")
            if (
                full_article is not None
                and full_article.text_cleaned
                and full_article.publish_date
                and len(full_article.text_cleaned) > length_threshold
            ):  # remove short articles
                full_article.search_term = article["search_term"]
                full_article.html = ""  # remove html, useless for us
                fulltext_articles.append(full_article)
                articles_added += 1

    return fulltext_articles


def get_wikipedia_article_on_date(title, date, api_endpoint=WIKIPEDIA_API_ENDPOINT):
    """
    Get the Wikipedia page plain text for a specific date.

    Args:
        title (str): The title of the Wikipedia page.
        date (str): The date in the format "YYYY-MM-DD".

    Returns:
        dict: A dictionary containing the url, title, and plain text of the page.
    """
    if title is None or title == "":
        return {}
    # Convert target_date to datetime object and format it for the API
    target_date_obj = datetime.strptime(date, "%Y-%m-%d")
    target = target_date_obj.strftime("%Y-%m-%dT%H:%M:%SZ")
    target_date_minus_three_years = target_date_obj - relativedelta(years=3)
    target_minus = target_date_minus_three_years.strftime("%Y-%m-%dT%H:%M:%SZ")
    # Parameters for getting the page revisions
    params = {
        "action": "query",
        "format": "json",
        "titles": title,
        "redirects": 1,
        "prop": "revisions|extracts",
        "explaintext": "",
        "rvlimit": "1",  # We only need the most recent revision before the target date
        "rvdir": "older",  # Start from the newest revisions
        "rvprop": "ids|timestamp",
        "rvstart": target,  # Start from the target date
        "rvend": target_minus,  # Get revisions older than the target date up to -3 years
    }
    session = requests.Session()
    try:
        response = session.get(url=api_endpoint, params=params)
        data = response.json()
    except Exception as e:
        logger.error("Wikipedia API query failed.")
        logger.error(e)
        return {}
    # Extract page ID (needed to handle the response format)
    if "query" not in data or "pages" not in data["query"]:
        logger.warning(f"No page {title} found.")
        return {}
    page_id = next(iter(data["query"]["pages"]))
    # Check if revisions are available
    if "revisions" in data["query"]["pages"][page_id]:
        # Get the revision details
        revision = data["query"]["pages"][page_id]["revisions"][0]
        revision_id = revision["revid"]
        # Get main information to return
        revision_url = f"https://en.wikipedia.org/w/index.php?title={title.replace(' ', '_')}&oldid={revision_id}"
        plaintext = data["query"]["pages"][page_id]["extract"]
        published_date = revision["timestamp"]
        logger.info(
            f"Retrieved Wikipedia page text for {title} on {date} (chars: {len(plaintext)}))"
        )
        return {
            "title": title,
            "text": plaintext,
            "link": revision_url,
            "published_date": published_date,
        }
    # If the page is a redirect, get the redirected title and recurse
    elif "redirects" in data["query"]:
        redirected_to = data["query"]["redirects"][0]["to"]
        return get_wikipedia_article_on_date(redirected_to, date)
    else:
        logger.warning(
            f"No revision {title} found earlier than the specified date {date}."
        )
        return {}


def retrieve_webpage_text(url, end_date):
    """
    Retrieve and parse a webpage using newspaper4k or wikipedia API.
    In particular, the method extracts the title, text, and publish date of the webpage.
    See https://pypi.org/project/newspaper4k/ for a tutorial.

    Args:
        url (str): URL of the webpage to be parsed.
        end_date (str): The end date of the retrieval in the format "YYYY-MM-DD".

    Returns:
        newspaper.article.Article: An article object containing the title,
        text, and publish date of the webpage.
    """
    if isinstance(url, str) is False:  # url is not a string, then it is not retrievable
        logger.warning(f"URL {url} is not a string.")
        return None
    # If the URL is a Wikipedia Link, utilize the page history
    if "wikipedia.org" in url and "upload.wikimedia.org" not in url:
        # Get title from wikipedia URL
        title = string_utils.extract_and_decode_title_from_wikiurl(url)
        page_dict = get_wikipedia_article_on_date(title, end_date)
        return NewscatcherArticle(page_dict, "")
    elif not is_irretrievable_site(url) and is_whitelisted(url):
        try:
            article = newspaper.article(
                url, fetch_images=False, keep_article_html=False
            )
            if article.publish_date is None:
                logger.warning(f"Cannot retrieve publish date for {url}.")
                return None
            elif article.publish_date.replace(tzinfo=None) < datetime.strptime(
                end_date, "%Y-%m-%d"
            ):
                logger.info(
                    f"Good article: publish date {article.publish_date.date()} earlier than the end date {end_date}."
                )
                return article
        except Exception as e:
            logger.error(e)


def retrieve_webpage_from_background(
    background_info, closing_date_timestamp, length_threshold=200
):
    """
    Retrieve webpage texts from background info.
    Remove short articles (less than length_threshold characters).

    Args:
        background_info (str): Background info in a markdown string that contains URLs.
        closing_date_timestamp (datetime): The closing date of the question.
        length_threshold (int, optional): The minimum length of the article text. Defaults to 200.

    Returns:
        list of article objects: A list of article objects containing the title, text, and publish date of the webpages,
      extracted from links in the background info
    """
    urls = get_urls_from_text(background_info)
    articles = []
    for url in urls:
        article = retrieve_webpage_text(url, closing_date_timestamp)
        if (
            article
            and article.text_cleaned
            and len(article.text_cleaned) > length_threshold
        ):
            articles.append(article)
    return articles


def get_search_queries(
    prompt,
    num_keywords=3,
    model_name="gpt-4-1106-preview",
    temperature=0.0,
    return_response=False,
):
    """
    Extract the search query terms from a question and its background
    information.

    The keywords are generated via OpenAI or Anthropic's LLM API, using config
    parameters. They are subsequently used to retrieve relevant articles, from
    our news retrieval system.

    Args:
        prompt (str): The prompt to use for the API call.
        num_keywords (int, optional): Number of keywords to extract (default:3).
        model_name (str, optional): The name of the model to use (default:
            "gpt-4-1106-preview").
        temperature (float, optional): The temperature to use for the API call
            (default: 0.0).
        return_response (bool, optional): Whether to return the full response.

    Returns:
        list[str]: A list of subject keywords.
    """
    # Query LLM's API for the subject keywords
    response = model_eval.get_response_from_model(
        model_name=model_name,
        prompt=prompt,
        temperature=temperature,
    )
    keywords = extract_search_queries(response)
    # Check if the number of keywords matches the specified number
    if keywords is None or len(keywords) == 0 or len(keywords) > num_keywords:
        logger.error("Number of search queries does not match the specified number.")
        logger.info("Response from the model: {}".format(response))
    if return_response:
        return keywords, response
    return keywords


async def async_get_search_queries(
    prompts,
    num_keywords=3,
    model_name="gpt-4-1106-preview",
    temperature=0.0,
    return_response=False,
):
    """
    Same as get_search_queries, but async.

    Args:
        prompts (list[str]): A list of prompts to use for the API call.
        num_keywords (int, optional): Number of search queries to extract (default:3).
        model_name (str, optional): The name of the model to use (default:
            "gpt-4-1106-preview").
        temperature (float, optional): The temperature to use for the API call
            (default: 0.0).
        return_response (bool, optional): Whether to return the full response.

    Returns:
        list[list[str]]: A list of lists of subject keywords.
        If return_response is True, also returns a list of responses.
    """
    # Query LLM's API for the subject keywords in batch
    search_query_tasks = [
        model_eval.get_async_response(
            prompt, model_name=model_name, temperature=temperature
        )
        for prompt in prompts
    ]
    search_query_responses = await asyncio.gather(*search_query_tasks)
    keywords_list = [
        extract_search_queries(response) for response in search_query_responses
    ]
    if any(
        keywords is None or len(keywords) == 0 or len(keywords) > num_keywords
        for keywords in keywords_list
    ):
        logger.error("Number of search queries does not match the specified number.")
        logger.info("Response from the model: {}".format(search_query_responses))
    if len(keywords_list) != len(prompts):
        logger.error("Number of search queries does not match the number of prompts.")
        logger.info("Response from the model: {}".format(search_query_responses))
    if return_response:
        return keywords_list, search_query_responses
    return keywords_list


async def get_search_queries_for_all_sources(
    prompt_templates,
    num_queries,
    date_range,
    question,
    background_info="",
    resolution_criteria="",
    max_words_newscatcher=5,
    max_words_gnews=8,
):
    """
    Get search queries for a single question. For both Newscatcher and GNews.

    There should be one group of search queries for each search query prompt.

    Newscatcher uses 5 words per query, GNews uses 7 words per query.

    Args:
        num_queries (int): The number of keywords used in the query.
        q (dict): The question.
        prompt_templates (list): A list of tuples, where each tuple contains a
            prompt template and a list of fields to fill in the template.

    Returns:
        tuple: A tuple containing:
            search_queries_list_nc (list): A list of search queries for Newscatcher.
            search_queries_list_gnews (list): A list of search queries for GNews.
            search_query_responses_list_nc (list): A list of the responses to the
                search query prompts for Newscatcher.
            search_query_responses_list_gnews (list): A list of the responses to the
                search query prompts for GNews.
            search_query_prompts_list_nc (list): A list of the search query prompts
                for Newscatcher.
            search_query_prompts_list_gnews (list): A list of the search query prompts
                for GNews.
    """
    # Get search queries prompts for Newscatcher
    search_query_prompts_list_nc = [
        string_utils.get_prompt(
            prompt_template,
            fields,
            question=question,
            dates=date_range,
            background=background_info,
            resolution_criteria=resolution_criteria,
            num_keywords=num_queries,
            max_words=max_words_newscatcher,  # for Newscatcher
        )
        for prompt_template, fields in prompt_templates
    ]
    # Get search queries prompts for GNews
    search_query_prompts_list_gnews = [
        string_utils.get_prompt(
            prompt_template,
            fields,
            question=question,
            dates=date_range,
            background=background_info,
            resolution_criteria=resolution_criteria,
            num_keywords=num_queries,
            max_words=max_words_gnews,  # for GNews
        )
        for prompt_template, fields in prompt_templates
    ]
    # Query LLM to get search queries for Newscatcher
    (
        search_queries_list,
        search_query_responses_list,
    ) = await async_get_search_queries(
        search_query_prompts_list_gnews + search_query_prompts_list_nc,
        num_keywords=num_queries,
        return_response=True,
    )
    # Split the search queries into two lists, one for Newscatcher and one for GNews
    search_queries_list_gnews = search_queries_list[
        : len(search_query_prompts_list_gnews)
    ]
    search_queries_list_nc = search_queries_list[len(search_query_prompts_list_gnews) :]
    search_query_responses_list_gnews = search_query_responses_list[
        : len(search_query_prompts_list_gnews)
    ]
    search_query_responses_list_nc = search_query_responses_list[
        len(search_query_prompts_list_gnews) :
    ]

    # probably better way to handle this
    search_queries_list_gnews = [
        queries + [question] for queries in search_queries_list_gnews
    ]
    search_queries_list_nc = [
        queries + [question] for queries in search_queries_list_nc
    ]

    return (
        search_queries_list_nc,
        search_queries_list_gnews,
        search_query_responses_list_nc,
        search_query_responses_list_gnews,
        search_query_prompts_list_nc,
        search_query_prompts_list_gnews,
    )


def get_articles_from_all_sources(
    queries_gnews, queries_nc, retrieval_dates, num_articles=5, length_threshold=200
):
    """
    Retrieve articles from both Newscatcher and GNews.

    Deduplicate the articles and remove short articles.

    Args:
        queries_gnews (list[str]): A list of search queries for GNews.
        queries_nc (list[str]): A list of search queries for Newscatcher.
        retrieval_dates (list[str]): A list containing two date strings (start and end dates)
            in 'YYYY-MM-DD' format to specify the date range for article retrieval.
        num_articles (int, optional): The number of articles to retrieve for each search term.
        length_threshold (int, optional): The minimum length of the article text. Defaults to 200.

    Returns:
        list: A list of full article data, with no duplicates.
    """
    #  return empty set for same-day questions or invalid date ranges.
    if not time_utils.is_more_recent(retrieval_dates[0], retrieval_dates[1]):
        logger.error(
            "retrieval_dates[1] {} should be strictly more recent than retrieval_dates[0] {}.".format(
                retrieval_dates[1], retrieval_dates[0]
            )
        )
        return []
    if queries_nc is not None and len(queries_nc) > 0:
        articles_nc = get_newscatcher_articles(
            queries_nc,
            retrieval_dates,
            num_articles=num_articles,
            length_threshold=length_threshold,
        )
    else:
        articles_nc = []
    if queries_gnews is not None and len(queries_gnews) > 0:
        articles_gnews = get_gnews_articles(
            queries_gnews, retrieval_dates, max_results=num_articles
        )
        articles_gnews = retrieve_gnews_articles_fulldata(
            articles_gnews, num_articles=num_articles, length_threshold=length_threshold
        )
    else:
        articles_gnews = []
    return deduplicate_articles(articles_nc + articles_gnews)
