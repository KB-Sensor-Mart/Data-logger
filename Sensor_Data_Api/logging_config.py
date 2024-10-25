import logging
import os
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime

def get_logger(name: str) -> logging.Logger:
    # Get today's date in the desired format (e.g., '24-10-2024')
    today_date = datetime.now().strftime('%d-%m-%Y')

    # Construct the log directory path using the current date
    LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'log', 'system_log', today_date)
    os.makedirs(LOG_DIR, exist_ok=True)

    # Set the log file path inside the date-based folder
    LOG_FILE = os.path.join(LOG_DIR, 'log')

    logger = logging.getLogger(name)
    logger.propagate = False

    if logger.hasHandlers():
        return logger
    logger.setLevel(logging.DEBUG)

    # Console Handler (for INFO and higher logs)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)  # Console logs from INFO level and above
    console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)

    # File Handler (for ERROR and higher logs, rotated daily)
    file_handler = TimedRotatingFileHandler(LOG_FILE, when="midnight", interval=1, backupCount=7)
    file_handler.setLevel(logging.INFO)  # File logs from ERROR level and above
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    file_handler.suffix = "%Y-%m-%d"  # Date-based rotation for the file

    # Add handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger