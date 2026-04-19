import logging
import os
import json
import re
import fcntl
from bs4 import BeautifulSoup
from datetime import datetime
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from utils import setup_logger


class GathererBase:
    """
    Base class for all data gathering automations.
    Provides standardized logging, JSON structure, content normalization,
    and archive persistence. Inherit from a gatherer type in gatherer_types/
    rather than from this class directly.
    """
    def __init__(self):
        self.logger = setup_logger(__name__)
        self.today = datetime.now().date().isoformat()
        self.archive = "workbench/archive_tester.jsonl" if self.logger.isEnabledFor(logging.DEBUG) else "data/archive.jsonl"
        self.capsule = []


    def clean_html_content(self, html_text):
        """
        Takes HTML and strips all formatting out, leaving only the pure text.
        """
        soup = BeautifulSoup(html_text, 'lxml')
        for script in soup(["script", "style"]):
            script.decompose()
        text = soup.get_text()
        text = re.sub(r'\s+', ' ', text)
        return text.strip()


    def dot_parse(self, text):
        """
        Fixes sentence spacing issues in raw text:
        1. Collapses double dots that are not part of an ellipsis (...) to '. '
        2. Inserts a space after any dot directly followed by an uppercase letter
           (A-Z, Ä, Ö, Ü), unless already followed by whitespace, a dot, a
           double quote, or a digit.
        """
        text = re.sub(r'(?<!\.)\.\.(?!\.)[ ]*', '. ', text)
        text = re.sub(r'\.(?![\s."\d])(?=[A-ZÄÖÜ])', '. ', text)
        return re.sub(r' {2,}', ' ', text)


    def normalize_content(self, text):
        """
        Applies dot_parse to fix mid-text sentence spacing, then ensures the
        text ends with exactly one trailing space. Terminal punctuation from
        the source data is preserved. Returns an empty string for empty input.
        """
        text = self.dot_parse(text).rstrip()
        return text + " " if text else ""


    def create_json_structure(self, title, content, url, source, language, **optional_fields):
        """
        Creates the standardized JSON structure for an archive entry.

        Args:
            title (str): headline of the news story
            content (str): body text of the news story
            url (str): direct link to the article
            source (str): origin feed or site URL, set as self.source in subclasses
            language (str): ISO language code of the article
        """
        return {
            "gathered_date": str(self.today),
            "title": title,
            "content": content,
            "url": url,
            "source": source,
            "language": language,
            "word_count": len(content.split()) if content else 0,
            "category": optional_fields.get('category'),
            "is_breaking_news": optional_fields.get('is_breaking_news'),
            "published_date": optional_fields.get('published_date'),
            "author": optional_fields.get('author'),
        }


    def save_capsule(self):
        """
        Appends the capsule to the archive file with an exclusive lock
        to prevent race conditions when multiple gatherers run in parallel.
        """
        if self.capsule:
            with open(self.archive, "a", encoding="utf-8") as f:
                fcntl.flock(f, fcntl.LOCK_EX)
                try:
                    for entry in self.capsule:
                        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
                finally:
                    fcntl.flock(f, fcntl.LOCK_UN)
            self.logger.info("finished writing news to capsule")
        else:
            self.logger.error("Error saving capsule: capsule is empty")
