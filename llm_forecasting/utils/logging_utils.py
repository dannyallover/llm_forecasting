import logging


def setup_file_logger(logger, file_name):
    """
    Set up a custom logger that writes to a file.

    Args:
        file_name (str): Name of the file to write to.
        logger_name (str): Name of the logger.
    """
    logger.setLevel(logging.INFO)
    file_handler = logging.FileHandler(file_name)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
