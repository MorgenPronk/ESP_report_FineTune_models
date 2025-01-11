import logging
import os

def setup_logger(log_filename):
    try:
        # Configure the logger
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)

        log_dir = os.path.dirname(log_filename)
        log_base_name = os.path.dirname(log_filename)

        # Create logs directory if it doesn't exist
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # Check if logger already has handlers to avoid duplicate log entries
        if not logger.handlers:
            # Create a file handler for the log file
            file_handler = logging.FileHandler(log_filename)
            file_handler.setLevel(logging.DEBUG)

            # Create a logging format
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)

            # Add the file handler to the logger
            logger.addHandler(file_handler)
        # print("Logger successfully setup")
        return logger
    except Exception as e:
        # print("Logger setup is UNsuccessful")
        raise
