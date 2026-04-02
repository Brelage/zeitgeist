import logging
import os
import inspect
from pathlib import Path
from logging.handlers import TimedRotatingFileHandler

LOG_LEVEL = logging.INFO


def setup_logger(name=None):
    """
    Standard logging setup for all scripts in this project.

    Args:
        name: identifier for the logger; defaults to the calling script's filename
    """
    if name is None:
        frame = inspect.stack()[1]
        name = os.path.splitext(os.path.basename(frame.filename))[0]

    logs_path = os.path.join("logs")
    os.makedirs(logs_path, exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)

    if not logger.handlers:
        formatter = logging.Formatter(fmt="%(name)s - %(asctime)s: %(message)s", datefmt="%Y.%m.%d %H:%M:%S")

        file_handler = TimedRotatingFileHandler(
            f"logs/{name}.log",
            when="midnight",
            backupCount=3
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    return logger
