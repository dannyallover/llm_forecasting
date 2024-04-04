# run this script with a venv with python 3.9 so it's compatible with
# py_clob_client (polymarket API python client)

# Standard library imports
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
import argparse
import ast
import logging
import time

# Related third-party imports
import requests
from tqdm import tqdm

# Local application/library-specific imports
import data_scraping
import information_retrieval
from config.keys import keys
from py_clob_client.client import ClobClient
from py_clob_client.constants import POLYGON

# Setup logging and other configurations
logger = logging.getLogger(__name__)

client = ClobClient(
    "https://clob.polymarket.com", key=keys["CRYPTO_PRIVATE_KEY"], chain_id=POLYGON
)


def get_market_query(offset_value):
    """
    Construct and return a GraphQL query string for fetching market data.

    Args:
    offset_value (int): The offset value to use in the query for pagination.

    Returns:
    str: A GraphQL query string.
    """
    query = f"""{{
      markets(offset: {offset_value}) {{
        id
        conditionId
        question
        description
        category
        createdAt
        questionID
        outcomes
        outcomePrices
        clobTokenIds
        endDate
        volume
        closed
      }}
    }}"""
    return query


def get_comment_query(market_id, offset_value):
    """
    Construct and return a GraphQL query string for fetching comments related
    to a specific market ID with pagination.

    Args:
    market_id (int): The unique identifier of the market.
    offset_value (int): The offset value to use for pagination.

    Returns:
    str: A GraphQL query string for fetching comments.
    """
    query = f"""{{
      comments(marketID: {market_id}, offset: {offset_value}) {{
        id
        body
        createdAt
        }}
    }}"""
    return query


def generate_json_markets(field, market_id=None):
    """
    Perform a POST request to retrieve market or comment data from the
    Polymarket API.

    Args:
    field (str): Specifies the type of data to fetch ('markets' or 'comments').
    market_id (int, optional): The market ID for which comments are to be fetched.
                               Required if 'field' is 'comments'.

    Returns:
    list: A list of dictionaries containing market or comment data.
    """
    url = "https://gamma-api.polymarket.com/query"
    offset_value = 0
    all_data = []

    while True:
        if field == "comments":
            query = get_comment_query(market_id, offset_value)
        elif field == "markets":
            query = get_market_query(offset_value)
        else:
            print("Wrong field name!")

        try:
            response = requests.post(url, json={"query": query})
            # Will raise an HTTPError if the HTTP request returned an
            # unsuccessful status code
            response.raise_for_status()
            data = response.json().get("data", {}).get(field, [])

            if not data:
                break  # Exit loop if no more markets are returned

            all_data.extend(data)
            offset_value += 1000

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            break  # Break the loop in case of request failure

    return all_data


def question_to_url(question, base_url="https://polymarket.com/event/"):
    """
    Convert a Polymarket question into a URL format.

    Args:
    question (str): The question text to be formatted.
    base_url (str, optional): The base URL to prepend to the formatted question.

    Returns:
    str: The formatted URL representing the Polymarket question.
    """
    cleaned_question = "".join(
        "" if char == "$" else char
        for char in question.strip()
        if char.isalnum() or char in [" ", "-", "$"]
    )

    # Replace spaces with hyphens and convert to lowercase
    url_formatted_question = cleaned_question.replace(" ", "-").lower()

    # Concatenate with the base URL
    url = base_url + url_formatted_question
    return url


def fetch_price_history(market_id):
    """
    Retrieve the price history of a market from the Polymarket API.

    Args:
    market_id (str): The unique identifier of the market.

    Returns:
    list: A list of dictionaries containing the price history data, or an empty list
          if the data retrieval fails.
    """
    url = (
        f"https://clob.polymarket.com/prices-history?interval=all&market="
        f"{market_id}&fidelity=60"
    )

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        history_data = data.get("history", [])
        return history_data
    else:
        print("Failed to retrieve data:", response.status_code)
        return []


def process_market(m):
    """
    Process a single market dictionary by adding additional information
    such as comments, URLs, community predictions, and other metadata.
    It also renames fields to align with a specific format.

    Args:
    market (dict): A dictionary representing a single market with its initial data.

    Returns:
    dict: The processed market dictionary with additional fields and formatted data.
    """
    m["comments"] = generate_json_markets("comments", market_id=int(m["id"]))
    m["url"] = question_to_url(m["question"])

    # Resolution
    try:
        m["outcomes"] = ast.literal_eval(m["outcomes"])
        m["outcomePrices"] = ast.literal_eval(m["outcomePrices"])

        # Make sure that 'outcomes' and 'outcomePrices' have the same length
        if len(m["outcomes"]) != len(m["outcomePrices"]):
            raise ValueError(
                "The lengths of 'outcomes' and 'outcomePrices' do not match."
            )

        # Find the outcome with the highest price
        highest_price = max(m["outcomePrices"], key=lambda x: float(x))
        highest_price_index = m["outcomePrices"].index(highest_price)
        resolution_outcome = m["outcomes"][highest_price_index]

        m["resolution"] = resolution_outcome

        if m["resolution"] == "Yes":
            m["resolution"] = 1
        elif m["resolution"] == "No":
            m["resolution"] = 0
    except Exception as e:
        print(f"An error occurred: {e}")
        m["resolution"] = "Error"

    # Question type
    m["question_type"] = "multiple_choice"
    if set(m["outcomes"]) == {"Yes", "No"}:
        m["question_type"] = "binary"

    # Community predictions for the first outcome
    try:
        if m["clobTokenIds"] is not None:
            # Attempt to fetch community predictions
            m["community_predictions"] = fetch_price_history(
                m["clobTokenIds"].split('"')[1]
            )
        else:
            m["community_predictions"] = []
    except IndexError as e:
        # Print the error and the problematic clobTokenIds
        print(f"Error: {e}, clobTokenIds: {m.get('clobTokenIds')}")
        m["community_predictions"] = []

    # Rename field names so it aligns with mateculus
    m["title"] = m.pop("question")
    m["close_time"] = m.pop("endDate")
    m["created_time"] = m.pop("createdAt")
    m["background"] = m.pop("description")
    m["is_resolved"] = m.pop("closed")

    # Data source
    m["data_source"] = "polymarket"

    return m


def main(n_days):
    """
    Main function to fetch and process Polymarket data.

    Args:
    n_days (int): Number of days in the past to limit the data fetching.
    If None, fetches all available data.

    Returns:
    list: A list of processed market dictionaries.
    """
    logger.info("Starting the polymarket script...")

    start_time = time.time()

    all_markets = generate_json_markets("markets")

    if n_days is not None:
        date_limit = datetime.now() - timedelta(days=n_days)
        all_markets = [
            market
            for market in all_markets
            if datetime.fromisoformat(market["createdAt"][:-1]) >= date_limit
        ]

    logger.info(f"Number of polymarket questions fetched: {len(all_markets)}")

    logger.info("Start preprocess the question...")
    with ThreadPoolExecutor(max_workers=50) as executor:
        results = list(
            tqdm(
                executor.map(process_market, all_markets),
                total=len(all_markets),
            )
        )

    logger.info("Start extracting articles links...")

    for question in results:
        question["extracted_articles_urls"] = information_retrieval.get_urls_from_text(
            question["background"]
        )
        if question["comments"]:
            for comment in question["comments"]:
                question["extracted_articles_urls"].extend(
                    information_retrieval.get_urls_from_text(comment["body"])
                )

    elapsed_time = time.time() - start_time
    logger.info(f"Total execution time: {elapsed_time} seconds")

    logger.info("Uploading to s3...")
    question_types = ["binary", "multiple_choice"]
    data_scraping.upload_scraped_data(results, "polymarket", question_types, n_days)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch polymarket data.")
    parser.add_argument(
        "--n_days",
        type=int,
        help="Fetch questions created in the last N days",
        default=None,
    )
    args = parser.parse_args()
    main(args.n_days)
