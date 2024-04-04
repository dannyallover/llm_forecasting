#!/usr/bin/env python3
import argparse
import datetime
import json
import logging
import os
import time
import traceback

# Related third-party imports
import jsonlines
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config.keys import keys
import data_scraping
import information_retrieval
from utils import api_utils, data_utils, time_utils

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

headers = {"Authorization": f"Token {keys['METACULUS_KEY']}"}
params = {"limit": 100}
METACULUS_API_URL = "https://www.metaculus.com/api2/"
CHROME_DRIVER_PATH = "/Users/apple/Downloads/chromedriver-mac-x64/chromedriver"
# Writing to file for debugging purposes. It will be deleted once the script is done.
OUTPUT_FILE = "metaculus_resolution_criteria.jsonl"
DISCUSSION_FILE = "metaculus_discussion.jsonl"
NOT_FOUND_FILE = "metaculus_not_found.jsonl"
WEIRD_ERRORS_FILE = "metaculus_weird_errors.jsonl"


def map_comments_to_questions(all_comments):
    """
    Map comments to their respective questions.

    Parameters:
    all_comments (list of dicts): A list of dictionaries where each dictionary contains
                                  details of a comment and its associated question.

    Returns:
    dict: A dictionary mapping question IDs to a list of comment information.
    """
    comments_by_question = {}
    for comment in all_comments:
        question_id = comment["question"]["id"]
        comment_info = {
            "comment_text": comment["comment_text"],
            "created_time": comment["created_time"],
            "author_name": comment["author_name"],
            "comment_id": comment["id"],
            "is_moderator": comment["is_moderator"],
            "is_admin": comment["is_admin"],
        }
        comments_by_question.setdefault(question_id, []).append(comment_info)
    return comments_by_question


def append_comments_to_questions(questions, comments_by_question):
    """
    Append comments to their respective questions.

    Parameters:
    questions (list of dicts): A list of dictionaries, each representing a question.
    comments_by_question (dict): A dictionary mapping question IDs to lists of comments.

    Returns:
    None: The function modifies the input 'questions' list in-place.
    """
    for question in questions:
        question_id = question["id"]
        question["comments"] = comments_by_question.get(question_id, [])


def setup_driver():
    """
    Initialize and return a WebDriver instance.
    """
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    service = Service(executable_path=CHROME_DRIVER_PATH)
    return webdriver.Chrome(service=service, options=chrome_options)


def check_page_condition(driver, condition_text):
    """
    Check if the current page contains specified text.
    Supports checking for 'Page not found' and 'DISCUSSION'.
    Parameters:
    driver (webdriver): The Selenium WebDriver instance.
    condition_text (str): Text to search for on the page.

    Returns:
    bool: True if text is found, False otherwise.
    """
    if condition_text == "Page not found":
        try:
            return (
                driver.find_element(
                    By.XPATH, '//div[@class="main-container text-center"]/h1'
                ).text
                == "Page not found"
            )
        except BaseException:
            return False
    elif condition_text == " DISCUSSION ":
        try:
            return (
                driver.find_element(
                    By.XPATH,
                    "//div[@class='main-container  ng-scope']/div[@class='page-header is-green']",
                ).text
                == " DISCUSSION "
            )
        except BaseException:
            return False


def click_show_more(driver, xpath):
    """
    Click the 'Show More' button on the page using its XPath.
    Ignores click action if the button is not clickable or not found.

    Parameters:
    driver (webdriver): The Selenium WebDriver instance.
    xpath (str): XPath of the 'Show More' button.
    """
    try:
        show_more_button = WebDriverWait(driver, 2).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        show_more_button.click()
    except Exception:
        pass


def extract_text_elements(driver, xpath):
    """
    Extract and concatenate text from elements located by XPath.
    Returns a single string of all text items, separated by spaces.

    Parameters:
    driver (webdriver): The Selenium WebDriver instance.
    xpath (str): XPath to locate text elements.

    Returns:
    str: Concatenated string of text from elements.
    """
    elements = driver.find_elements(By.XPATH, xpath)
    return " ".join([el.text.strip() for el in elements if el.text])


def process_questions(questions, driver):
    """
    Iterate and process a list of questions using web scraping.

    This function goes through each question in a list, navigates to their web pages,
    and processes them based on certain conditions. It categorizes questions as
    discussions or not found, and processes others as needed.

    Parameters:
    questions (list): List of question dictionaries to process.
    driver (webdriver): Selenium WebDriver for web navigation.

    Returns:
    None: Outputs results to files, doesn't return a value.
    """
    question_ids = [questions[i]["id"] for i in range(len(questions))]

    for question_id in question_ids:
        url = f"https://www.metaculus.com/questions/{question_id}"
        driver.get(url)

        if check_page_condition(driver, " DISCUSSION "):
            filename = DISCUSSION_FILE
            logger.info(f"Question ID {question_id} is a discussion.")
            with jsonlines.open(filename, mode="a") as file:
                file.write({"id": question_id})
            continue

        if check_page_condition(driver, "Page not found"):
            filename = NOT_FOUND_FILE
            logger.info(f"Question ID {question_id} is not found.")
            with jsonlines.open(filename, mode="a") as file:
                file.write({"id": question_id})
            continue

        try:
            process_individual_question(driver, question_id)
        except Exception as e:
            log_error(question_id, e)


def process_individual_question(driver, question_id):
    """
    Process and extract data from an individual question's web page.

    Navigates to a question page using its ID, extracting details like text,
    resolution criteria, and background. Handles element expansion for more
    information.

    Parameters:
    driver (webdriver): Selenium WebDriver for web navigation.
    question_id (int): ID of the question to process.

    Returns:
    None: Writes extracted data to a file, no return value.
    """
    props = {
        "id": question_id,
        "question": None,
        "resolution_criteria": None,
        "background": None,
    }
    props["question"] = driver.find_element(
        By.XPATH, "//meta[@property='og:title']"
    ).get_attribute("content")

    click_show_more(driver, "//resolution-criteria//button[contains(., 'Show More')]")
    click_show_more(driver, "//resolution-criteria//button[contains(., 'Show More')]")
    props["resolution_criteria"] = extract_text_elements(
        driver, "//div[contains(@class, 'prediction-section-resolution-criteria')]"
    )
    if len(props["resolution_criteria"]) == 0:
        logger.info(f"{question_id} did not successfully scrape question criteria.")

    click_show_more(
        driver, "//background-info//button[contains(@class, 'inline-flex')]"
    )
    props["background"] = extract_text_elements(
        driver,
        '//div[@class="content font-sans [&>:first-child]:mt-0 [&>:last-child]:mb-0"]',
    )
    if len(props["background"]) == 0:
        logger.info(
            f"{question_id} did not successfully scrape background or \
             the question does not have background."
        )

    with jsonlines.open(OUTPUT_FILE, mode="a") as writer:
        writer.write(props)


def log_error(question_id, error):
    """
    Log an error that occurred while processing a question.
    """
    print(f"Error for question {question_id}: {error}")
    traceback.print_exc()
    with jsonlines.open(WEIRD_ERRORS_FILE, mode="a") as file:
        file.write(
            {"id": question_id, "error": str(error), "trace": traceback.format_exc()}
        )


def map_datasets(data_dict, questions):
    """
    Map resolution criteria and background information from a data dictionary
    to a list of questions based on matching titles.

    Parameters:
    data_dict (dict): A dictionary containing question data, keyed by question
                      titles.
    questions (list): A list of question dictionaries to be updated with data
                      from data_dict.

    Returns:
    list: The updated list of question dictionaries, each supplemented with
          'resolution_criteria' and 'background' from the data_dict.
    """
    # Define a function to map data to metaculus based on question and title
    # similarity
    for m in questions:
        title = m["id"]
        matched_data = data_dict.get(
            title, {"resolution_criteria": "", "background": ""}
        )
        m["resolution_criteria"] = matched_data["resolution_criteria"]
        m["background"] = matched_data["background"]

    return questions


def fetch_all_valid_questions(base_url, headers, params):
    """
    Fetch all valid questions from the Metaculus API.

    Retrieve questions from the Metaculus API, excluding discussion-type questions.
    Attach the description (background) and close time for each valid question.

    Args:
        base_url (str): Base URL of the Metaculus API.
        headers (dict): Headers to include in the API request.
        params (dict): Parameters for the API request.

    Returns:
        list: List of filtered and enriched Metaculus questions.
    """
    questions = api_utils.fetch_all_questions(base_url, headers, params)

    # Filter out discussion type questions directly
    valid_questions = [q for q in questions if q["type"] != "discussion"]

    # Fetch description (background) for each question
    for question in valid_questions:
        question["close_time"] = time_utils.safe_to_datetime(question["close_time"])
        question["is_resolved"] = True if question["active_state"] != "OPEN" else False
        question["data_source"] = "metaculus"
        q_type = (
            question["possibilities"].get("type")
            if question["possibilities"]
            else "no_type"
        )
        question["question_type"] = q_type
    return valid_questions


def main(n_days=None):
    """
    Execute the main script for processing Metaculus data.

    Orchestrate the fetching, processing, and summarizing of Metaculus questions.
    Filter questions based on a specified time range and incorporate comments and
    resolution criteria.

    Args:
        n_days (int, optional): Number of days to look back for questions.
                                Defaults to None.

    Returns:
        list: List of complete Metaculus questions with associated data.
    """
    logger.info("Starting the metaculus script...")

    start_time = time.time()

    if n_days is not None:
        some_time_ago = datetime.datetime.now() - datetime.timedelta(days=n_days)
        start_date = some_time_ago.strftime("%Y-%m-%d")
        questions_url = (
            METACULUS_API_URL
            + f"questions/?include_description=true&publish_time__gt={start_date}"
        )
        comments_url = METACULUS_API_URL + f"comments/?created_time__gt={start_date}"
    else:
        questions_url = METACULUS_API_URL + "questions/?include_description=true"
        comments_url = METACULUS_API_URL + "comments/"

    questions = fetch_all_valid_questions(questions_url, headers, params)
    logger.info(f"Number of metaculus questions fetched: {len(questions)}")

    data_utils.reformat_metaculus_questions(questions)

    all_comments = api_utils.fetch_all_questions(comments_url, headers, params)
    comments_by_question = map_comments_to_questions(all_comments)
    append_comments_to_questions(questions, comments_by_question)

    driver = setup_driver()
    process_questions(questions, driver)
    driver.quit()

    # map resolution criteria and background into questions
    data = []
    with open(OUTPUT_FILE, "r") as file:
        for line in file:
            json_line = json.loads(line)
            data.append(json_line)

    data_dict = {d["id"]: d for d in data if d["id"]}

    complete_metaculus_questions = map_datasets(data_dict, questions)

    # add data source and question type
    for q in complete_metaculus_questions:
        q["data_source"] = "metaculus"
        q_type = q["possibilities"].get("type") if q["possibilities"] else "no_type"
        q["question_type"] = q_type

    logger.info("Start extracting articles links...")

    for question in complete_metaculus_questions:
        question["extracted_articles_urls"] = []
        if "background" in question.keys() and question["background"]:
            question[
                "extracted_articles_urls"
            ] += information_retrieval.get_urls_from_text(question["background"])
        if "resolution_criteria" in question.keys() and question["resolution_criteria"]:
            question[
                "extracted_articles_urls"
            ] += information_retrieval.get_urls_from_text(
                question["resolution_criteria"]
            )
        if "comments" in question.keys() and question["comments"]:
            comments_urls = []
            for comment in question["comments"]:
                comments_urls += information_retrieval.get_urls_from_text(
                    comment["comment_text"]
                )
            question["extracted_articles_urls"] += comments_urls

    elapsed_time = time.time() - start_time
    logger.info(f"Total execution time: {elapsed_time} seconds")

    logger.info("Uploading to s3...")
    question_types = list(
        set([q["question_type"] for q in complete_metaculus_questions])
    )
    data_scraping.upload_scraped_data(
        complete_metaculus_questions, "metaculus", question_types, n_days
    )

    # Delete the files after script completion
    files_to_delete = [OUTPUT_FILE, DISCUSSION_FILE, NOT_FOUND_FILE, WEIRD_ERRORS_FILE]
    for file_name in files_to_delete:
        if os.path.exists(file_name):
            os.remove(file_name)
            logger.info(f"Deleted the file: {file_name}")
        else:
            logger.info(f"The file {file_name} does not exist")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch metaculus data.")
    parser.add_argument(
        "--n_days",
        type=int,
        help="Fetch questions created in the last N days",
        default=None,
    )
    args = parser.parse_args()

    main(args.n_days)
