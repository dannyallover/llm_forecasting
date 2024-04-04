import datetime
import requests
import logging

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config.constants import S3, S3_BUCKET_NAME
from utils import db_utils

logger = logging.getLogger(__name__)


def upload_scraped_data(data, source, question_types, n_days_or_not=None):
    """
    Upload data (scraped by the script) by type to S3, partitioned by
        the specified source and date range if specified.

    Args:
        data (list): List of question data to process.
        source (str): The source identifier for categorizing uploaded data.
        question_types (list): List of question types to filter and upload.
        n_days_or_not (int or None): Number of days to look back for questions,
                                     or None for all available data.
    """
    today_date = datetime.datetime.now().strftime("%Y_%m_%d")

    for q_type in question_types:
        questions = [q for q in data if q["question_type"] == q_type]
        q_type = q_type.lower()
        if n_days_or_not:
            file_name = f"n_days_updated_{q_type}_questions_{today_date}.pickle"
            s3_path = f"{source}/n_days_updated_{q_type}_questions/{file_name}"
        else:
            file_name = f"updated_{q_type}_questions_{today_date}.pickle"
            s3_path = f"{source}/updated_{q_type}_questions/{file_name}"

        db_utils.upload_data_structure_to_s3(S3, questions, S3_BUCKET_NAME, s3_path)


def fetch_question_description(headers, question_id):
    """
    Fetch and return the description of a specific question from Metaculus.

    The function queries the Metaculus API for a given question ID and
    extracts the question's description from the response.

    Parameters:
    - headers (dict): Headers to include in the API request.
    - question_id (int): The ID of the question to fetch.

    Returns:
    - str: Description of the question, or an empty string if not found.
    """
    endpoint = f"https://www.metaculus.com/api2/questions/{question_id}"
    response = requests.get(endpoint, headers=headers)
    return response.json().get("description", "")


# Use your own executable_path (download from https://chromedriver.chromium.org/).
def initialize_and_login(
    signin_page,
    email,
    password,
    executable_path="/Users/apple/Downloads/chromedriver-mac-x64/chromedriver",
):
    """
    Initialize the WebDriver and log into the website.

    Returns:
        selenium.webdriver.Chrome: An instance of the Chrome WebDriver after logging in.
    """
    # Webdriver options
    chrome_options = Options()
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
    )
    service = Service(executable_path=executable_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # log in
    driver.get(signin_page)
    driver.find_element(By.ID, "user_email").send_keys(email)
    driver.find_element(By.ID, "user_password").send_keys(password)
    driver.find_element(By.NAME, "commit").click()

    return driver


def question_not_found(driver):
    """
    Check if a specific question is not found on the website.

    Args:
        driver (webdriver.Chrome): The Selenium Chrome WebDriver instance.

    Returns:
        bool: True if the question is not found, False otherwise.
    """
    try:
        return (
            driver.find_element(By.CLASS_NAME, "flash-message").text
            == "Could not find that question."
        )
    except BaseException:
        return False


def get_source_links(driver, url):
    """
    Retrieve source links from a given question page.

    Args:
        driver (webdriver.Chrome): The Selenium Chrome WebDriver instance.
        url (str): The URL of the question page.

    Returns:
        list: A list of retrieved source links.
    """
    source_links = set()
    try:
        driver.get(url)  # Make sure to navigate to the page first
        driver.find_element(By.XPATH, '//a[text() = "Source Links"]').click()
        WebDriverWait(driver, 2).until(
            EC.visibility_of_element_located((By.ID, "links-table"))
        )
        rows = driver.find_elements(
            By.XPATH, '//table[contains(@id, "links-table")]/tbody/tr'
        )
        for entry in rows:
            try:
                url_elem = entry.find_element(By.TAG_NAME, "a")
                source_links.add(url_elem.get_attribute("href"))
            except BaseException:
                # If no <a> tag is found in this table data, it will skip to
                # the next
                continue
    except:  # Catch any other exception
        logger.info("Failed to get links.")
    return list(source_links)


def make_hashable(e):
    """
    Convert elements, including dictionaries, into a hashable form.

    Args:
        e (Any): The element to be converted.

    Returns:
        tuple: A tuple representing the hashable form of the element.
    """
    if isinstance(e, dict):
        return tuple((key, make_hashable(val)) for key, val in sorted(e.items()))
    elif isinstance(e, list):
        return tuple(make_hashable(x) for x in e)
    else:
        return e


def unhashable_to_dict(t):
    """
    Convert tuples back into their original dictionary or list forms.

    Args:
        t (tuple): The tuple to be converted.

    Returns:
        Any: The original dictionary or list form of the tuple.
    """
    if isinstance(t, tuple):
        try:
            return dict((k, unhashable_to_dict(v)) for k, v in t)
        except ValueError:
            return [unhashable_to_dict(x) for x in t]
    else:
        return t
