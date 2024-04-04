import argparse
import certifi
import concurrent.futures
import logging
import requests
from datetime import datetime, timedelta
from tqdm import tqdm

import data_scraping
import information_retrieval
from config.keys import keys
from utils import time_utils

# Logger configuration
logger = logging.getLogger(__name__)

# Manifold API configuration
MANIFOLD_API = keys["MANIFOLD_KEY"]
BASE_URL = "https://api.manifold.markets/v0/markets?"

# Headers for API requests
headers = {"Authorization": f"Key {MANIFOLD_API}"}


def fetch_all_manifold_questions(base_url, headers, limit=1000):
    """
    Fetch all questions from the Manifold API.

    Retrieve a list of questions from the Manifold API, paginating through the results
    based on the specified limit until all questions are fetched.

    Args:
        base_url (str): The base URL for the Manifold API.
        headers (dict): The headers for the API request, including authorization.
        limit (int): The maximum number of questions to fetch in each request.

    Returns:
        list: A list of all questions fetched from the API.
    """
    all_questions = []
    last_id = None

    while True:
        params = {"limit": limit, "sort": "created-time", "order": "desc"}
        if last_id:
            params["before"] = last_id

        response = requests.get(
            base_url, headers=headers, params=params, verify=certifi.where()
        )
        if response.status_code != 200:
            print(f"Error: {response.status_code}")
            break

        data = response.json()
        if not data:
            break

        all_questions.extend(data)
        last_id = data[-1]["id"]

    return all_questions


def fetch_market_details(market_id, headers):
    """
    Fetch detailed information for a specific market from the Manifold API.

    Retrieve detailed information about a specific market, identified by its market ID,
    from the Manifold API.

    Args:
        market_id (str): The unique identifier of the market.
        headers (dict): Headers for the API request, including authorization.

    Returns:
        dict or None: The detailed market information or None if an error occurs.
    """
    try:
        url = f"https://api.manifold.markets/v0/market/{market_id}"
        response = requests.get(url, headers=headers, verify=certifi.where())
        response.raise_for_status()  # Raises an HTTPError for non-200 responses
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error fetching market details for ID {market_id}: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching market details for ID {market_id}: {e}")
    return None


def fetch_bets_for_market(market_id, headers):
    """
    Fetch a list of bets for a specific market from the Manifold API.

    Retrieve all bets placed in a specific market, identified by its market ID, from
    the Manifold API. Handle any HTTP errors encountered during the request and return
    an empty list if an error occurs.

    Args:
        market_id (str): The unique identifier of the market.
        headers (dict): Headers for the API request, including authorization.

    Returns:
        list: A list of bets for the specified market or an empty list if an error occurs.
    """
    try:
        url = "https://api.manifold.markets/v0/bets"
        params = {"contractId": market_id, "limit": 1000}
        response = requests.get(
            url, headers=headers, params=params, verify=certifi.where()
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error fetching bets for market ID {market_id}: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching bets for market ID {market_id}: {e}")
    return []


def fetch_comments_for_market(market_id, headers):
    """
    Fetch a list of comments for a specific market from the Manifold API.

    Retrieve all comments made in a specific market, identified by its market ID, from
    the Manifold API. Handle any HTTP errors encountered during the request and return
    an empty list if an error occurs.

    Args:
        market_id (str): The unique identifier of the market.
        headers (dict): Headers for the API request, including authorization.

    Returns:
        list: A list of comments for the specified market or an empty list if an error occurs.
    """
    try:
        url = "https://api.manifold.markets/v0/comments"
        params = {"contractId": market_id, "limit": 1000}
        response = requests.get(
            url, headers=headers, params=params, verify=certifi.where()
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error fetching comments for market ID {market_id}: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching comments for market ID {market_id}: {e}")
    return []


def process_market(market, headers):
    """
    Process a single market by fetching its details, bets, comments, and transforming the data.

    Fetch and add market descriptions, and map bets and comments for a given market.
    Convert timestamps and restructure market data for consistency and clarity.

    Args:
        market (dict): The market data to process.
        headers (dict): Headers for the API requests.

    Returns:
        dict: The processed market data.
    """
    market_id = market["id"]

    # Fetch and add market descriptions
    try:
        market_details = fetch_market_details(market_id, headers)
        if market_details:
            market["background"] = market_details.get("description")

        background_content = market.get("background", {}).get("content", [])
        background_text = " ".join(
            [
                item["content"][0].get("text", "")
                for item in background_content
                if item.get("type") == "paragraph" and item.get("content")
            ]
        )
        market["background"] = background_text
    except Exception as exc:
        logger.error(
            f"Market id {market_id} got processing error when fetching description: {exc}"
        )
    try:
        market["resolution"] = 1 if market["resolution"] == "YES" else 0
    except Exception as exc:
        logger.error(
            f"Market id {market_id} got processing error when reformatting resolution: {exc}"
        )

    # Fetch and map bets and comments
    market["community_predictions"] = fetch_bets_for_market(market_id, headers)
    market["comments"] = fetch_comments_for_market(market_id, headers)

    for comment in market.get("comments", []):
        if "createdTime" in comment:
            comment["createdTime"] = time_utils.convert_timestamp(
                comment["createdTime"]
            )

    for bet in market.get("community_predictions", []):
        if "createdTime" in bet:
            bet["createdTime"] = time_utils.convert_timestamp(bet["createdTime"])

    try:
        market["date_close"] = market.pop("closeTime")
    except Exception as exc:
        logger.error(
            f"Market id {market_id} got processing error when popping closeTime: {exc}"
        )
    try:
        market["date_begin"] = market.pop("createdTime")
    except Exception as exc:
        logger.error(
            f"Market id {market_id} got processing error when popping createdTime: {exc}"
        )
    try:
        market["is_resolved"] = market.pop("isResolved")
    except Exception as exc:
        logger.error(
            f"Market id {market_id} got processing error when popping isResolved: {exc}"
        )
    try:
        market["question_type"] = market.pop("outcomeType")
    except Exception as exc:
        logger.error(
            f"Market id {market_id} got processing error when popping outcomeType: {exc}"
        )

    try:
        market["resolved_time"] = market.pop("resolutionTime")
    except Exception as exc:
        logger.error(
            f"Market id {market_id} got processing error when reformatting resolution time: {exc}"
        )

    if not market["background"]:
        market["background"] = "Not applicable/available for this question."

    market["resolution_criteria"] = "Not applicable/available for this question."
    market["data_source"] = "manifold"

    return market


def main(n_days):
    """
    Process and upload Manifold market data.

    Fetch market data from Manifold, process it, and upload the processed data
    to an AWS S3 bucket.
    Limit the fetched data to markets created within the last N days, if specified.

    Args:
        n_days (int or None): Number of days to look back for markets.
        If None, fetches all markets.

    Returns:
        list: A list of processed market data.
    """
    logger.info("Starting the manifold script...")

    all_markets = fetch_all_manifold_questions(BASE_URL, headers)

    # Transform time format
    ids_with_date_errors = []
    for key in [
        "createdTime",
        "closeTime",
        "resolutionTime",
        "lastUpdatedTime",
        "lastCommentTime",
    ]:
        for market in all_markets:
            if key in market:
                try:
                    market[key] = time_utils.convert_timestamp(market[key])
                except BaseException:
                    ids_with_date_errors.append(market["id"])
                    continue

    logger.info(
        f"Number of manifold questions with date errors: {len(set(ids_with_date_errors))}"
    )

    if n_days is not None:
        date_limit = datetime.now() - timedelta(days=n_days)
        all_markets = [
            q
            for q in all_markets
            if datetime.fromisoformat(q["createdTime"][:]) >= date_limit
        ]

    logger.info(f"Number of manifold questions fetched: {len(all_markets)}")

    processed_markets = []
    number_of_workers = 50

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=number_of_workers
    ) as executor:
        # Create a list to hold the futures
        futures = [
            executor.submit(process_market, market, headers) for market in all_markets
        ]

        # Use tqdm to create a progress bar. Wrap futures with tqdm.
        for future in tqdm(
            concurrent.futures.as_completed(futures),
            total=len(all_markets),
            desc="Processing",
        ):
            result = future.result()
            processed_markets.append(result)

    processed_markets = [
        q
        for q in processed_markets
        if "question_type" in q.keys() and q["community_predictions"]
    ]

    # Save itermediate data files
    logger.info("Uploading the intermediate data files to s3...")
    question_types = list(set([q["question_type"] for q in processed_markets]))
    data_scraping.upload_scraped_data(processed_markets, "manifold", question_types)

    for q in processed_markets:
        q["date_resolve_at"] = q["community_predictions"][0]["createdTime"]

    logger.info("Start extracting articles from links...")

    for question in processed_markets:
        question["extracted_urls"] = information_retrieval.get_urls_from_text(
            question["background"]
        )
        if question["comments"]:
            for comment in question["comments"]:
                try:
                    comment = comment["content"]["content"][0]["content"][-1]["text"]
                    question["extracted_articles_urls"].extend(
                        information_retrieval.retrieve_webpage_from_background(
                            comment, question["close_time"]
                        )
                    )
                except:
                    continue

    logger.info("Uploading to s3...")
    question_types = list(set([q["question_type"] for q in processed_markets]))
    data_scraping.upload_scraped_data(processed_markets, "manifold", question_types)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch Manifold data.")
    parser.add_argument(
        "--n_days",
        type=int,
        help="Fetch questions created in the last N days",
        default=None,
    )
    args = parser.parse_args()
    main(args.n_days)
