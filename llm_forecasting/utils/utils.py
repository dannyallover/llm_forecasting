# Standard library imports
from collections import Counter


def flatten_list(nested_list):
    flat_list = [item for sublist in nested_list for item in sublist]
    return flat_list


def most_frequent_item(lst):
    """
    Return the most frequent item in the given list.

    If there are multiple items with the same highest frequency, one of them is
    returned.

    Args:
        lst (list): The list from which to find the most frequent item.

    Returns:
        The most frequent item in the list.
    """
    if not lst:
        return None  # Return None if the list is empty
    # Count the frequency of each item in the list
    count = Counter(lst)
    # Find the item with the highest frequency
    most_common = count.most_common(1)
    return most_common[0][0]  # Return the item (not its count)


def indices_of_N_largest_numbers(list_of_numbers, N=3):
    """
    Return the indices of the N largest numbers in the given list of numbers.

    Args:
        list_of_numbers (list): The list of numbers from which to find the N
            largest numbers.
        N (int, optional): The number of largest numbers to find. Defaults to 3.

    Returns:
        list: The indices of the N largest numbers in the given list of numbers.
    """
    # Get the indices of the N largest numbers
    indices = sorted(range(len(list_of_numbers)), key=lambda i: list_of_numbers[i])[-N:]
    return indices
