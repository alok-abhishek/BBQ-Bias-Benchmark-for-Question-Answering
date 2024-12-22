import logging
import sys

def configure_logging(level=logging.INFO, log_file=None):
    """
    Configure logging settings for the application.

    Args:
        level (int): Logging level (e.g., logging.INFO, logging.DEBUG).
        log_file (str): Optional path to a log file. If None, logs are sent to stdout.

    Returns:
        None
    """
    handlers = []

    # Log to stdout
    handlers.append(logging.StreamHandler(sys.stdout))

    # Log to a file if specified
    if log_file:
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=handlers
    )

    logging.info("Logging is configured.")

