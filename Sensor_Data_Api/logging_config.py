import logging
import os
from datetime import datetime, timedelta

def get_logger(name: str) -> logging.Logger:
    # Get today's date and log directory
    today_date = datetime.now().strftime('%d-%m-%Y')
    base_log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'system_log')
    os.makedirs(base_log_dir, exist_ok=True)

    # Set the log file path with date-based filename
    LOG_FILE = os.path.join(base_log_dir, f'{today_date}.log')

    # Set up the logger
    logger = logging.getLogger(name)
    logger.propagate = False

    # Check if handlers are already added to avoid duplicate logs
    if logger.hasHandlers():
        return logger

    logger.setLevel(logging.DEBUG)

    # Console Handler (for INFO and higher logs)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)

    # File Handler (no rotation needed)
    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)

    # Add handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    # Clean up old log files, keeping only the last 15 days
    cleanup_old_logs(base_log_dir, days_to_keep=15, logger=logger)
    
    return logger
    
def cleanup_old_logs(log_dir: str, days_to_keep: int, logger: logging.Logger):
    cutoff_date = datetime.now() - timedelta(days = days_to_keep)
    for log_file in os.listdir(log_dir):
        file_path = os.path.join(log_dir, log_file)
        if log_file.endswith('.log'):
            try:
                file_date_str = log_file.replace('.log','')
                file_date = datetime.strptime(file_date_str, '%d-%m-%Y')
                if file_date < cutoff_date:
                    os.remove(file_path)
                    logger.info(f"Deleted old log files: {file_path}")
            except ValueError:
                continue
