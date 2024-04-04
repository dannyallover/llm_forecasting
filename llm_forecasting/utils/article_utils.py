# Standard library imports
from datetime import datetime

# Local application/library-specific imports
from utils import db_utils
from config.keys import keys
from config.constants import S3_BUCKET_NAME, S3

# Set up constants
AWS_ACCESS_KEY = keys["AWS_ACCESS_KEY"]
AWS_SECRET_KEY = keys["AWS_SECRET_KEY"]


def article_object_to_dict(article):
    """
    Convert an article object to a dictionary

    Args:
        article (Article): An article object (such as NewscatcherArticle)

    Returns:
        article_dict (dict): A dictionary containing the article's attributes
            such as title, text, authors, etc.
    """
    article_dict = {}
    for attribute in article.__dict__:
        field = getattr(article, attribute)
        if (
            isinstance(field, str)  # title, text, etc
            or isinstance(field, int)
            or isinstance(field, float)  # relevance ratings
            or isinstance(field, list)  # authors list
        ):
            article_dict[attribute] = field
        if isinstance(field, datetime):  # datetime, etc
            article_dict[attribute] = field.strftime("%Y-%m-%d")
    return article_dict


def article_object_list_to_dict(article_list):
    """
    Convert a list of article objects to a list of dictionaries
    """
    return [article_object_to_dict(article) for article in article_list]


def upload_articles_to_s3(article_list, s3_path="system/info-hp"):
    """
    Upload a list of articles to S3

    Args:
        article_list (list): A list of article objects (such as NewscatcherArticle)
        s3_path (str): The path to save the articles to in S3

    Returns:
        None
    """
    articles_dict = article_object_list_to_dict(article_list)
    s3_filename = f"{s3_path}/articles.pickle"
    db_utils.upload_data_structure_to_s3(
        s3=S3, data_structure=articles_dict, bucket=S3_BUCKET_NAME, s3_path=s3_filename
    )
