import logging
import os
import sys

log_folder = "logging_file"
os.makedirs(log_folder, exist_ok=True)

log_file = os.path.join(log_folder, "logs")


def get_logger(name: str, filename: str, level=logging.INFO) -> logging.Logger:
    """Create and return a logger for a specific microservice."""

    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        log_path = os.path.join(log_folder, filename)
        file_handler = logging.FileHandler(log_path)

        file_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )
        logger.addHandler(file_handler)

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )
        logger.addHandler(console_handler)

    return logger
