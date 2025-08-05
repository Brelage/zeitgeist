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
    def __init__(self):
        self.logger = setup_logger(__name__)
        self.today = datetime.now().date().isoformat()
        self.archive = "workbench/archive_tester.jsonl" if self.logger.isEnabledFor(logging.DEBUG) else "data/archive.jsonl"
        self.capsule = [] # list of JSON dictionaries. Each item is a line in the JSONL archive


    def clean_html_content(self, html_text):
        soup = BeautifulSoup(html_text, 'lxml')
        for script in soup(["script", "style"]):
            script.decompose()
        text = soup.get_text()
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        return text

    def create_json_structure(self, title, content, url, source, language, **optional_fields):
        """Create standardized JSON structure for archival entry"""
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
        with open(self.archive, "a", encoding="utf-8") as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            try:
                for l in self.capsule:
                    f.write(json.dumps(l, ensure_ascii=False) + "\n")
            finally:
                fcntl.flock(f, fcntl.LOCK_UN)
                
        self.logger.info("finished writing news to capsule")