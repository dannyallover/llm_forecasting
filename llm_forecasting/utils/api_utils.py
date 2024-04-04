# Standard library imports
import logging
import time

# Related third-party imports
import requests

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def request_with_retries(
    method, url, headers, params=None, data=None, max_retries=5, delay=30
):
    """
    Make an API request (GET or POST) with retries in case of rate-limiting
    (HTTP 429) or other defined conditions and return the JSON content or log
    an error and return None.

    Args:
        method (str): HTTP method ('GET' or 'POST').
        url (str): The API endpoint.
        headers (dict): Headers for the API request.
        params (dict, optional): Parameters for the API request.
        data (dict, optional): JSON data for the API request (used for POST).
        max_retries (int, optional): Maximum number of retries. Defaults to 5.
        delay (int, optional): Delay (in seconds) between retries. Defaults to
        30.

    Returns:
        dict or None: The JSON response content as a dictionary or None if an
        error occurred.
    """
    for _ in range(max_retries):
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, params=params)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data)
            else:
                logging.error(f"Unsupported method: {method}")
                return None

            if response.status_code == 429:
                time.sleep(delay)
                continue

            response.raise_for_status()
            return response.json()

        except requests.RequestException as e:
            logging.error(f"Request error: {e}")
            return None

    logging.error(f"Exceeded max retries for URL: {url}")
    return None


def get_response_content(url, headers, params=None, max_retries=5, delay=30):
    """
    Create a wrapper function that issues a GET API request, utilizing a
    generic retry mechanism.
    """
    return request_with_retries(
        "GET", url, headers, params=params, max_retries=max_retries, delay=delay
    )


def post_request_with_retries(endpoint, headers, payload, retries=5):
    """
    Create a wrapper function that makes a POST API request using the generic
    retry mechanism.
    """
    response = request_with_retries(
        "POST", endpoint, headers, data=payload, max_retries=retries
    )
    if (
        response
        and "detail" in response
        and "Expected available in" in response["detail"]
    ):
        wait_seconds = int(response["detail"].split(" ")[-2]) + 1
        time.sleep(wait_seconds)
        return request_with_retries(
            "POST", endpoint, headers, data=payload, max_retries=retries
        )
    return response


def fetch_all_questions(base_url, headers, params):
    """
    Fetch all questions from the API using pagination.

    Args:
    - base_url (str): The base URL of the API.
    - headers (dict): The headers to use for the requests.
    - params (dict): The parameters to use for the requests.

    Returns:
    - list: List of all questions fetched from the API.
    """
    all_questions = []

    current_url = base_url
    while current_url:
        logging.info(f"Fetching data from {current_url} with params: {params}")

        data = get_response_content(current_url, headers, params)
        if not data:
            break

        if "results" in data:
            all_questions.extend(data["results"])
        else:
            all_questions.append(data)

        current_url = data.get("next")

    return all_questions
