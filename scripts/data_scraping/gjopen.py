# Standard library imports
import argparse
import datetime
import json
import logging
import os
import random
import time

# Related third-party imports
import jsonlines
from selenium.webdriver.common.by import By

# Local application/library-specific imports
import data_scraping
from config.keys import keys

logger = logging.getLogger(__name__)
MAX_CONSECUTIVE_NOT_FOUND = 1000
# Writing to file for debugging purposes. It will be deleted once the script is done.
FILE_PATH = "gjopen_dump.jsonl"
# Use your own executable_path (download from https://chromedriver.chromium.org/).
CHROMEDRIVER_PATH = "/Users/apple/Downloads/chromedriver-mac-x64/chromedriver"
GJOPEN_EMAIL = keys["EMAIL"]
GJOPEN_PASSWORD = keys["GJOPEN_CSET_PASSWORD"]


def main(n_days):
    """
    Scrape, process, and upload question data from gjopen (https://www.gjopen.com/)

    Args:
        n_days (int): Number of days to look back for questions.

    Returns:
        list: A list of processed question data.
    """
    driver = data_scraping.initialize_and_login(
        signin_page="https://www.gjopen.com/users/sign_in",
        email=GJOPEN_EMAIL,
        password=GJOPEN_PASSWORD,
        executable_path=CHROMEDRIVER_PATH,
    )

    question_counter = 0
    consecutive_not_found_or_skipped = 0
    while True:
        question_counter += 1
        url = f"https://www.gjopen.com/questions/{question_counter}"

        try:
            driver.get(url)
            trend_graph_element = driver.find_element(
                By.CSS_SELECTOR,
                "div[data-react-class='FOF.Forecast.QuestionTrendGraph']",
            )
            props = json.loads(trend_graph_element.get_attribute("data-react-props"))
            props["extracted_articles_urls"] = data_scraping.get_source_links(
                driver, url
            )

            with jsonlines.open(FILE_PATH, mode="a") as writer:
                writer.write(props)
            consecutive_not_found_or_skipped = 0
        except BaseException:
            if data_scraping.question_not_found(driver):
                logger.info(f"Question {question_counter} not found")
            else:
                logger.info(f"Skipping question {question_counter}")
            consecutive_not_found_or_skipped += 1
            if consecutive_not_found_or_skipped > MAX_CONSECUTIVE_NOT_FOUND:
                logger.info("Reached maximum consecutive not found.")
                break

        time.sleep(random.uniform(0, 2))  # random delay between requests

    data = []
    with open(FILE_PATH, "r") as file:
        for line in file:
            json_line = json.loads(line)
            data.append(json_line)

    # Remove duplicated dicts
    unique_tuples = {data_scraping.make_hashable(d) for d in data}
    all_questions = [data_scraping.unhashable_to_dict(t) for t in unique_tuples]

    if n_days is not None:
        date_limit = datetime.datetime.now() - datetime.timedelta(days=n_days)
        all_questions = [
            q
            for q in all_questions
            if datetime.datetime.fromisoformat(q["question"]["created_at"][:-1])
            >= date_limit
        ]

    logger.info(f"Number of gjopen questions fetched: {len(all_questions)}")

    for i in range(len(all_questions)):
        try:
            all_questions[i]["community_prediction"] = all_questions[i].pop(
                "trend_graph_probabilities"
            )
        except BaseException:
            all_questions[i]["community_prediction"] = []
        all_questions[i]["url"] = "https://www.gjopen.com/questions/" + str(
            all_questions[i]["question"]["id"]
        )
        all_questions[i]["title"] = all_questions[i]["question"]["name"]
        all_questions[i]["close_time"] = all_questions[i]["question"].pop("closed_at")
        all_questions[i]["created_time"] = all_questions[i]["question"].pop(
            "created_at"
        )
        all_questions[i]["background"] = all_questions[i]["question"]["description"]
        all_questions[i]["data_source"] = "gjopen"

        if all_questions[i]["question"]["state"] != "resolved":
            all_questions[i]["resolution"] = "Not resolved."
            all_questions[i]["is_resolved"] = False
        else:
            all_questions[i]["resolution"] = all_questions[i]["question"]["answers"][0][
                "probability"
            ]
            all_questions[i]["is_resolved"] = True

        all_questions[i]["question_type"] = "binary"
        answer_set = set(
            [answer["name"] for answer in all_questions[i]["question"]["answers"]]
        )
        if answer_set == {"Yes", "No"} or answer_set == {"Yes"}:
            all_questions[i]["question_type"] = "binary"
        else:
            all_questions[i]["question_type"] = "multiple_choice"

    logger.info("Uploading to s3...")
    question_types = ["binary", "multiple_choice"]
    data_scraping.upload_scraped_data(all_questions, "gjopen", question_types, n_days)

    # Delete the file after script completion
    if os.path.exists(FILE_PATH):
        os.remove(FILE_PATH)
        logger.info(f"Deleted the file: {FILE_PATH}")
    else:
        logger.info(f"The file {FILE_PATH} does not exist")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch gjopen data.")
    parser.add_argument(
        "--n_days",
        type=int,
        help="Fetch markets created in the last N days",
        default=None,
    )
    args = parser.parse_args()
    main(args.n_days)
