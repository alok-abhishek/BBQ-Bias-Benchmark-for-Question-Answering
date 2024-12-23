import logging
import sys
from datetime import datetime
import os

def configure_logging(level=logging.INFO, log_file=None, log_dir="../logs"):
    """
    Configure logging settings for the application.

    Args:
        level (int): Logging level (e.g., logging.INFO, logging.DEBUG).
        log_file (str): Optional path to a log file. If None, logs are sent to a default file named 'log_<date>.txt'.
        log_dir (str): Directory path to store log files. Defaults to '../logs'.

    Returns:
        None
    """
    # Ensure the log directory exists
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    handlers = []

    # Default log file name if not provided
    if log_file is None:
        log_file = os.path.join(log_dir, f"log_{datetime.now().strftime('%Y-%m-%d')}.txt")

    # Log to stdout
    handlers.append(logging.StreamHandler(sys.stdout))

    # Log to the default or specified file
    handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=handlers
    )

    logging.info("Logging is configured.")
