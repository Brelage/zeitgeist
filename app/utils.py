import logging
import os
import yaml
import sys
from pathlib import Path
from logging.handlers import TimedRotatingFileHandler

sys.path.append(str(Path(__file__).resolve().parents[1]))

LOG_LEVEL = logging.DEBUG

def setup_logger(name=None):
    logs_path = os.path.join("logs")
    os.makedirs(logs_path, exist_ok=True)
    
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)  

    if not logger.handlers:
        formatter = logging.Formatter(fmt="%(module)s - %(asctime)s: %(message)s", datefmt="%Y.%m.%d %H:%M:%S")
        
        file_handler = TimedRotatingFileHandler(
            f"logs/{__name__}.log",
            when="midnight",
            backupCount=3
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

        return logger


def load_source(adress):
    config_path = os.environ.get("SOURCES_YAML")
    if config_path is None:
        raise ValueError("SOURCES_YAML environment variable not set")
    with open(config_path, "r") as file:
        data = yaml.safe_load(file)
        source = data[adress]
        return source


def archive(data):
    """
    archives the data from the sources to the database
    """
    
    capsule = None
    return capsule