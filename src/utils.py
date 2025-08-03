import logging
import os
from logging.handlers import TimedRotatingFileHandler

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


def archive(data):
    """
    archives the data from the sources to the database
    """
    
    capsule = None
    return capsule