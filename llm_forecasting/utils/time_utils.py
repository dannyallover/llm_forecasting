# Related third-party imports
from datetime import datetime, timedelta
import pandas as pd
import math


def extract_date(datetime):
    """
    Extract a date string from a datetime object or raw string.

    Args:
        datetime (datetime or str): A datetime object or string.
            If a string in the format 'YYYY-MM-DDTHH:MM:SSZ', the date part
            is extracted.

    Returns:
        str: A date string in the format 'YYYY-MM-DD'.
    """
    if isinstance(datetime, str):
        if "T" in datetime:
            return datetime.split("T")[0]
        else:
            return datetime
    else:
        return str(datetime.date())


def convert_date_string_to_tuple(date_string):
    """
    Convert a date string of the form 'year-month-day' to a tuple (year, month, day).

    Args:
        date_string (str): A string representing the date in 'year-month-day' format.

    Returns:
        tuple: A tuple containing the year, month, and day as integers.
    """
    # Split the date string by '-'
    parts = date_string.split("-")
    # Check that the date string is in the correct format
    assert len(parts) == 3, "Date string must be in 'year-month-day' format."
    # Convert the parts to integers and return as a tuple
    return tuple(map(int, parts))


def safe_to_datetime(date_str):
    """
    Safely convert a date string to a datetime object.

    Args:
        date_str (str): Date string to be converted.

    Returns:
        datetime: Converted datetime object or None if conversion fails.
    """
    try:
        return pd.to_datetime(date_str.replace("Z", "+00:00"))
    except pd.errors.OutOfBoundsDatetime:
        return None


def move_date_by_percentage(date_str1, date_str2, percentage):
    """
    Compute a date that is a specified percentage between two dates.

    Returns the date before |date_str2| if the computed date is equal
    to |date_str2|.

    Args:
        date_str1 (str): Start date in "YYYY-MM-DD" format.
        date_str2 (str): End date in "YYYY-MM-DD" format.
        percentage (float): Percentage to move from start date towards end date.

    Returns:
        str: The new date in "YYYY-MM-DD" format.
    """
    # Parse dates
    date1 = datetime.strptime(date_str1, "%Y-%m-%d")
    date2 = datetime.strptime(date_str2, "%Y-%m-%d")

    # Ensure date1 is earlier than date2
    if date1 > date2:
        date1, date2 = date2, date1

    # Calculate new date at the given percentage between them
    target_date = date1 + (date2 - date1) * (percentage / 100.0)

    # Check if target date is the same as date_str2, if so, subtract one day
    if target_date.strftime("%Y-%m-%d") == date_str2:
        target_date -= timedelta(days=1)

    return target_date.strftime("%Y-%m-%d")


def adjust_date_by_days(date_str, days_to_adjust):
    """
    Adjust a date string by a specified number of days.

    Args:
        date_str (str): A date string in the format 'YYYY-MM-DD'.
        days_to_adjust (int): The number of days to adjust the date by. Can be
        positive or negative.

    Returns:
        str: A new date string in the format 'YYYY-MM-DD' adjusted by the
        specified number of days.
    """
    # Parse the date string into a datetime object
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")

    # Adjust the date by the given number of days
    adjusted_date = date_obj + datetime.timedelta(days=days_to_adjust)

    # Convert the adjusted datetime object back into a string
    new_date_str = adjusted_date.strftime("%Y-%m-%d")

    return new_date_str


def convert_timestamp(timestamp):
    """
    Convert a numeric timestamp into a formatted date string.

    This function checks if the given timestamp is in milliseconds or seconds,
    and converts it to a date string in the 'YYYY-MM-DD' format. It assumes that
    timestamps are in milliseconds if they are greater than 1e10, which
    typically corresponds to dates after the year 2001.

    Args:
        timestamp (float or int): The timestamp to convert. Can be in seconds
        or milliseconds.

    Returns:
        str: The converted timestamp as a date string in 'YYYY-MM-DD' format.
    """
    # Identify if the timestamp is in milliseconds or seconds
    timestamp = float(timestamp)
    is_millisecond = timestamp > 1e10  # assuming data is from after 2001
    if is_millisecond:
        timestamp = timestamp / 1000  # Convert from milliseconds to seconds

    # Convert to formatted date string
    return datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d")


def is_more_recent(first_date_str, second_date_str, or_equal_to=False):
    """
    Determine if |second_date_str| is more recent than |first_date_str|.

    Args:
        first_date_str (str): A string representing the first date to compare against. Expected format: 'YYYY-MM-DD'.
        second_date_str (str): A string representing the second date. Expected format: 'YYYY-MM-DD'.

    Returns:
        bool: True if the second date is more recent than the first date, False otherwise.
    """
    first_date_obj = datetime.strptime(first_date_str, "%Y-%m-%d")
    second_date_obj = datetime.strptime(second_date_str, "%Y-%m-%d")
    if or_equal_to:
        return second_date_obj >= first_date_obj
    return second_date_obj > first_date_obj


def is_less_than_N_days_apart(date1_str, date2_str, N=3):
    """
    Check if the difference between two dates is less than N days.

    :param date1_str: First date as a string in 'YYYY-MM-DD' format.
    :param date2_str: Second date as a string in 'YYYY-MM-DD' format.
    :param N: Number of days for comparison.
    :return: True if the difference is less than N days, otherwise False.
    """
    date_obj1 = datetime.strptime(date1_str, "%Y-%m-%d")
    date_obj2 = datetime.strptime(date2_str, "%Y-%m-%d")
    return (date_obj2 - date_obj1) < timedelta(days=N)


def find_pred_with_closest_date(date_str, date_pred_list):
    """
    Finds the tuple with the date closest to the given reference date from a list of (date, prediction) tuples.

    Parameters:
    - date_str (str): Reference date in 'YYYY-MM-DD' format.
    - date_pred_list (list of tuples): Each tuple contains a date string in 'YYYY-MM-DD' format and an associated prediction.

    Returns:
    - tuple: The tuple with the closest date to date_str. Returns None if date_pred_list is empty.

    Raises:
    - ValueError: If date_str or dates in date_pred_list are not in the correct format.
    """
    # Convert the reference date string to a datetime object
    ref_date = datetime.strptime(date_str, "%Y-%m-%d")

    # Initialize variables to store the closest date and its difference
    closest_date = None
    min_diff = float("inf")

    # Iterate through the list of tuples
    for date_tuple in date_pred_list:
        # Convert the date string in the tuple to a datetime object
        current_date = datetime.strptime(date_tuple[0], "%Y-%m-%d")

        # Calculate the absolute difference in days
        diff = abs((current_date - ref_date).days)

        # Update the closest date and min_diff if this date is closer
        if diff < min_diff:
            min_diff = diff
            closest_date = date_tuple

    return closest_date


def get_retrieval_date(
    retrieval_index, num_retrievals, date_begin, date_close, resolve_date
):
    """
    Calculate a specific retrieval date within a given time range.

    The retrieval date is determined using an exponential distribution based on the total number of retrievals.
    If the calculated date is after the resolve date, None is returned.

    Args:
        retrieval_index (int): Index of the current retrieval (starting from 0).
        num_retrievals (int): Total number of retrievals planned within the date range.
        date_begin (str): Start date of the range in 'YYYY-MM-DD' format.
        date_close (str): End date of the range in 'YYYY-MM-DD' format.
        resolve_date (str): Date by which the retrieval should be resolved in 'YYYY-MM-DD' format.

    Returns:
        str or None: The calculated retrieval date in 'YYYY-MM-DD' format, or None if it falls after the resolve date.
    """
    date_begin_obj = datetime.strptime(date_begin, "%Y-%m-%d")
    date_close_obj = datetime.strptime(date_close, "%Y-%m-%d")
    resolve_date_obj = datetime.strptime(resolve_date, "%Y-%m-%d")

    # Early return if date range is invalid or reversed
    if date_begin_obj >= date_close_obj or date_begin_obj > resolve_date_obj:
        return None

    # Calculate the total number of days in the range
    total_days = (date_close_obj - date_begin_obj).days

    # Calculate the retrieval date
    retrieval_days = math.exp((math.log(total_days) / num_retrievals) * retrieval_index)
    retrieval_date_obj = date_begin_obj + timedelta(days=retrieval_days)

    if retrieval_date_obj >= date_close_obj:
        retrieval_date_obj = date_close_obj - timedelta(days=1)
    if retrieval_date_obj >= resolve_date_obj:
        return None

    # Check against the previous retrieval date
    if retrieval_index > 1:
        previous_days = math.exp(
            (math.log(total_days) / num_retrievals) * (retrieval_index - 1)
        )
        previous_date_obj = date_begin_obj + timedelta(days=previous_days)
        if retrieval_date_obj <= previous_date_obj:
            return None

    return retrieval_date_obj.strftime("%Y-%m-%d")
