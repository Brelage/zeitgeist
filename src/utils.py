import logging
import os
import sys
import json
import re
import fcntl
from bs4 import BeautifulSoup
from pathlib import Path
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

LOG_LEVEL = logging.INFO

sys.path.append(str(Path(__file__).resolve().parents[1]))


def setup_logger(name=None):
    """
    standard logging setup for every other script.

    Args:
        name: usually the __name__ special variable to identify the script
    """
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


class Gatherer:
    """
    baseline class for data gathering automations. 
    Use this class with inheritance to ensure standardized logging, behavior, and JSON structure for the capsules
    """
    def __init__(self):
        self.logger = setup_logger(__name__)
        self.today = datetime.now().date().isoformat()
        self.archive = "workbench/archive_tester.jsonl" if self.logger.isEnabledFor(logging.DEBUG) else "data/archive.jsonl"
        self.capsule = [] # list of JSON dictionaries. Each item is a line in the JSONL archive


    def clean_html_content(self, html_text):
        """
        takes HTML and strips all formatting out, leaving only the pure text
        html_text: string with HTML
        """
        soup = BeautifulSoup(html_text, 'lxml')
        for script in soup(["script", "style"]):
            script.decompose()
        text = soup.get_text()
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        return text


    def dot_parse(self, text):
        """
        Inserts a space after every dot in the text if the dot is followed by
        an uppercase letter (A-Z, Ä, Ö, Ü), unless the dot is already followed by
        a space, another dot, a double quote, or a digit.
        """
        return re.sub(
            r'\.(?![\s."\d])(?=[A-ZÄÖÜ])',
            '. ',
            text
        )


    def create_json_structure(self, title, content, url, source, language, **optional_fields):
        """
        Create standardized JSON structure of a news article for archival entry.

        Args: 
            title(str): the title of a news story
            content(str): the text of a news story
            url(str): the URL linking to the news story directly
            source(str): the news site that was used to gahter the data. Usually defined in the gather script as self.source
            language(str): the language of the news story
        
        Returns:
            a JSON dictionary containing information about an article

        """
        article = {
            # Required fields
            "gathered_date": str(self.today),
            "title": title,
            "content": content, 
            "url": url,
            "source": source,
            "language": language,
            "word_count": len(content.split()) if content else 0,
            
            # Optional fields with None defaults
            "category": optional_fields.get('category'),
            "is_breaking_news": optional_fields.get('is_breaking_news'),
            "published_date": optional_fields.get('published_date'),
            "author": optional_fields.get('author')
        }
        
        return article


    def save_capsule(self):
        """
        locks the data/archive.jsonl file and appends the capsule to it before releasing, thereby avoiding race conditions.
        """
        if self.capsule:
            with open(self.archive, "a", encoding="utf-8") as f:
                fcntl.flock(f, fcntl.LOCK_EX)
                try:
                    for l in self.capsule:
                        f.write(json.dumps(l, ensure_ascii=False) + "\n")
                finally:
                    fcntl.flock(f, fcntl.LOCK_UN)
                    
            self.logger.info("finished writing news to capsule")
        else:
            self.logger.error("Error saving capsule: capsule is empty")