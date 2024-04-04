# Standard library imports
import logging
import re

# Third-party imports
import urllib.parse

# Local application/library-specific imports
from config.constants import TOKENS_TO_PROBS_DICT

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def is_string_in_list(target_string, string_list):
    """
    Check if the target string is in the list of strings; case insensitive.
    """
    # Convert the target string to lowercase
    target_string_lower = target_string.lower()

    # Check if the lowercase target string is in the list of lowercase strings
    return any(s.lower() == target_string_lower for s in string_list)


def find_end_word(paragraph, end_words, window_size=50):
    """
    Find one of the end_words in the last window_size words of the paragraph.
    Return the found word or None if no word is found.

    TODO: Lowercase the paragraph and end_words before searching so that the search is case-insensitive?

    Args:
    - paragraph (str): The paragraph to search in.
    - end_words (list of str): The words to search for.
    - window_size (int): The number of words from the end to search within.

    Returns:
    str: found word or None
    """
    sorted_words = sorted(end_words, key=lambda s: len(s.split(" ")), reverse=True)
    for end_word in sorted_words:
        if end_word in paragraph[-window_size:]:
            return end_word
    logger.debug(f"Could not find any end word in {paragraph[-window_size:]}.")
    return None


def get_prompt(
    prompt_template,
    fields,
    question=None,
    data_source=None,
    dates=None,
    background=None,
    resolution_criteria=None,
    num_keywords=None,
    retrieved_info=None,
    reasoning=None,
    article=None,
    summary=None,
    few_shot_examples=None,
    max_words=None,
):
    """
    Fill in a prompt template with specific data based on provided fields.

    Args:
        prompt_template (str): The template containing placeholders for data
            insertion.
        fields (list): Placeholders within the template to be filled ('QUESTION',
            'DATES', 'FEW_SHOT_EXAMPLES', 'RETRIEVED_INFO').
        question (str, optional): The question text for the 'QUESTION'
            placeholder.
        data_source (str, optional): The platform (e.g. "metaculus").
        background (str, optional): Background information for the 'BACKGROUND'
            placeholder.
        resolution_criteria (str, optional): Resolution criteria for the
            'RESOLUTION_CRITERIA' placeholder.
        dates (tuple or list of strs, optional): Start and end dates for the
            'DATES' placeholder (length == 2)
        retrieved_info (str, optional): Information text for the 'RETRIEVED_INFO'
            placeholder.
        reasoning (str, optional): Reasoning text for the 'REASONING' placeholder.
        article (str, optional): Article text for the 'ARTICLE' placeholder.
        summary (str, optional): Summary text for the 'SUMMARY' placeholder.
        few_shot_examples (list, optional): List of (question, answer) tuples for
            the 'FEW_SHOT_EXAMPLES' placeholder.
        max_words (int, optional): Maximum number of words for the 'MAX_WORDS'
            used for search query generation.

    Returns:
        str: A string with the placeholders in the template replaced with the provided
            data.
    """
    mapping = {}
    for f in fields:
        if f == "QUESTION":
            mapping["question"] = question
        elif f == "DATES":
            mapping["date_begin"] = dates[0]
            mapping["date_end"] = dates[1]
        elif f == "FEW_SHOT_EXAMPLES":
            examples = few_shot_examples or []
            for j, (q, answer) in enumerate(examples, 1):
                mapping[f"question_{j}"] = q
                mapping[f"answer_{j}"] = answer
        elif f == "RETRIEVED_INFO":
            mapping["retrieved_info"] = retrieved_info
        elif f == "BACKGROUND":
            mapping["background"] = background
        elif f == "RESOLUTION_CRITERIA":
            mapping["resolution_criteria"] = resolution_criteria
        elif f == "REASONING":
            mapping["reasoning"] = reasoning
        elif f == "BASE_REASONINGS":
            mapping["base_reasonings"] = reasoning
        elif f == "NUM_KEYWORDS":
            mapping["num_keywords"] = num_keywords
        elif f == "MAX_WORDS":
            mapping["max_words"] = str(max_words)
        elif f == "ARTICLE":
            mapping["article"] = article
        elif f == "SUMMARY":
            mapping["summary"] = summary
        elif f == "DATA_SOURCE":
            mapping["data_source"] = data_source
    return prompt_template.format(**mapping)


def extract_probability_with_stars(text):
    """
    Extract a probability value from a given text string.

    The function searches for numbers enclosed in asterisks (*), interpreting
    them as potential probability values. If a percentage sign is found with
    the number, it's converted to a decimal. The function returns the last
    number found that is less than or equal to 1, as a probability should be.
    If no such number is found, a default probability of 0.5 is returned.

    Args:
    - text (str): The text string from which the probability value is to be
    extracted.

    Returns:
    - float: The extracted probability value, if found. Otherwise, returns 0.5.
    """
    # Regular expression to find numbers between stars
    pattern = r"\*(.*?[\d\.]+.*?)\*"
    matches = re.findall(pattern, text)

    # Extracting the numerical values from the matches
    extracted_numbers = []
    for match in matches:
        # Extract only the numerical part (ignoring potential non-numeric
        # characters)
        number_match = re.search(r"[\d\.]+", match)
        if number_match:
            try:
                number = float(number_match.group())
                if "%" in match:
                    number /= 100
                extracted_numbers.append(number)
            except BaseException:
                continue

    if len(extracted_numbers) > 0 and extracted_numbers[-1] <= 1:
        return extracted_numbers[-1]

    # Regular expression to find numbers between stars
    pattern = r"([\d\.]+.*?)\*"
    matches = re.findall(pattern, text)

    # Extracting the numerical values from the matches
    extracted_numbers = []
    for match in matches:
        # Extract only the numerical part (ignoring potential non-numeric
        # characters)
        number_matches = re.findall(r"[\d\.]+", match)
        for num_match in number_matches:
            try:
                number = float(num_match)
                extracted_numbers.append(number)
            except BaseException:
                continue

    if len(extracted_numbers) > 0 and extracted_numbers[-1] <= 1:
        return extracted_numbers[-1]

    return 0.5


def extract_prediction(
    response,
    answer_type="probability",
    end_words=list(TOKENS_TO_PROBS_DICT["ten_options"].keys()),
):
    """
    A generic function to extract a prediction from a response string.

    Args:
        response (str): The response string from which the prediction is to be
            extracted.
        answer_type (str): The type of answer to extract. Can be "probability"
            or "tokens".
        end_words (list): The list of end words to search for in the response
            string. The first end word found in the response string will be
            used to extract the prediction.
            Only used if answer_type == "tokens".

    Returns:
        str or float: The extracted prediction.
    """
    if answer_type == "probability":
        return extract_probability_with_stars(response)
    elif answer_type == "tokens":
        return find_end_word(response, end_words)
    else:
        raise ValueError(f"Invalid answer_type: {answer_type}")


def extract_and_decode_title_from_wikiurl(url):
    """
    Extract the title from a Wikipedia URL and decode it.

    Args:
        url (str): The Wikipedia URL.

    Returns:
        str: The decoded title. None if the URL is invalid.
    """
    if "wikipedia.org" in url and "upload.wikimedia.org" not in url:
        # Extract the part after '/wiki/' and before the first '#?' if present
        match = re.search(r"/wiki/([^#?]+)", url)
        if match:
            # Replace underscores with spaces and decode percent encoding
            return urllib.parse.unquote(re.sub(r"_", " ", match.group(1)))
    return None


def concat_summaries_from_fields(summary_texts, titles, publish_dates):
    """
    Concatenate summaries from a list of summary texts. Fill in the titles and
    publish dates for each summary.

    The length of the summary_texts, titles, and publish_dates lists should be
    the same.

    Args:
        summary_texts (list of str): A list of summary texts.
        titles (list of str): A list of titles.
        publish_dates (list str): A list of publish dates.

    Returns:
        str: The concatenated summaries with titles and publish dates.
    """
    logger.info(
        f"Concatenating summaries from {len(summary_texts)} articles ({len(titles)} titles and {len(publish_dates)} dates)."
    )
    if (len(summary_texts) != len(titles)) or (
        len(summary_texts) != len(publish_dates)
    ):
        logger.error(
            f"Lengths of summary_texts, titles, and publish_dates should be the same. Got {len(summary_texts)}, {len(titles)}, and {len(publish_dates)}."
        )
        return "Not available."
    article_summaries = [
        f"[{i+1}] {titles[i]} (published on {(publish_dates[i] if publish_dates[i] else 'unknown date')})\nSummary: {article_summary}\n"
        for i, article_summary in enumerate(summary_texts)
    ]
    concatenated_summaries_str = (
        "---\nARTICLES\n" + "\n".join(article_summaries) + "----"
    )
    return concatenated_summaries_str