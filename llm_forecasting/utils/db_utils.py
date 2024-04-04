# Standard library imports
from io import StringIO
import logging
import os
import pickle
import random
import string

# Related third-party imports
import boto3
import pandas as pd

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def initialize_s3_client(aws_access_key_id, aws_secret_access_key):
    """
    Initialize an Amazon S3 client using provided AWS credentials.

    Args:
    - aws_access_key_id (str): AWS access key for authentication.
    - aws_secret_access_key (str): AWS secret access key for authentication.

    Returns:
    - boto3.client: Initialized S3 client.
    """
    return boto3.client(
        "s3",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )


def upload_data_structure_to_s3(s3, data_structure, bucket, s3_path):
    """
    Upload a local file to a specified path in an Amazon S3 bucket.

    Args:
        s3 (boto3.client): An initialized S3 client instance.
        data_structure (.): Data structure to save.
        bucket (str): Name of the target S3 bucket.
        s3_path (str): Desired filename within the S3 bucket.
    """
    try:
        extension = s3_path.split(".")[-1]
        hash = "".join(random.choices(string.ascii_letters + string.digits, k=5))
        temp_file = f"temp{hash}.{extension}"
        with open(temp_file, "wb") as f:
            pickle.dump(data_structure, f)

        s3.upload_file(temp_file, bucket, s3_path)
        os.remove(temp_file)
        logging.info(f"Successfully uploaded data to {bucket}/{s3_path}")
    except Exception as e:
        logging.error(f"Error uploading data to {bucket}/{s3_path}. Error: {e}")


def upload_file_to_s3(s3, local_file, bucket, s3_path):
    """
    Upload a local file to a specified path in an Amazon S3 bucket.

    Args:
    - s3 (boto3.client): An initialized S3 client instance.
    - local_file (str): Path of the local file to upload.
    - bucket (str): Name of the target S3 bucket.
    - s3_path (str): Desired path within the S3 bucket.

    """
    try:
        s3.upload_file(local_file, bucket, s3_path)
        logging.info(f"Successfully uploaded {local_file} to {bucket}/{s3_path}")
    except Exception as e:
        logging.error(f"Error uploading {local_file} to {bucket}/{s3_path}. Error: {e}")


def read_pickle_from_s3(s3, bucket, s3_path):
    """
    Fetch and deserialize a pickle file from an S3 bucket.

    This can be used in conjunction with `upload_data_structure_to_s3` to
    upload and download arbitrary data structures to/from S3.

    Args:
    - s3 (boto3.client): An initialized S3 client.
    - bucket (str): Name of the S3 bucket containing the pickle file.
    - s3_path (str): Path of the pickle file within the S3 bucket.

    Returns:
    - object: Deserialized object from the pickle file.
    """
    obj = s3.get_object(Bucket=bucket, Key=s3_path)
    data = pickle.loads(obj["Body"].read())
    return data


def read_pickle_files_from_s3_folder(s3, bucket, s3_folder_path):
    # List objects in the specified S3 folder
    objects = s3.list_objects(Bucket=bucket, Prefix=s3_folder_path)

    pickle_files = []
    # Loop through the objects and filter for pickle files
    for obj in objects.get("Contents", []):
        key = obj["Key"]
        if key.endswith(".pickle"):
            # Download the pickle file
            response = s3.get_object(Bucket=bucket, Key=key)
            # Read the pickle file from the response
            pickle_data = pickle.loads(response["Body"].read())
            pickle_files.append(pickle_data)

    return pickle_files


def read_csv_from_s3(s3, bucket, s3_path):
    """
    Fetch and read a CSV file from an S3 bucket into a pandas DataFrame.

    Args:
    - s3 (boto3.client): An initialized S3 client.
    - bucket (str): Name of the S3 bucket containing the CSV file.
    - s3_path (str): Path of the CSV file within the S3 bucket.

    Returns:
    - pd.DataFrame: DataFrame populated with the CSV data.
    """
    obj = s3.get_object(Bucket=bucket, Key=s3_path)
    df = pd.read_csv(StringIO(obj["Body"].read().decode("utf-8")))
    return df
