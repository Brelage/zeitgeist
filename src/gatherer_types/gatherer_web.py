import requests
import sys
from pathlib import Path
from bs4 import BeautifulSoup

sys.path.append(str(Path(__file__).resolve().parents[1]))
from gatherer_base import GathererBase


class GathererWeb(GathererBase):
    """
    Gatherer type for HTML scraping sources.
    Provides a get_soup() method that handles fetching and parsing.
    Subclasses receive the BeautifulSoup object and implement extraction logic.
    """

    def get_soup(self, url):
        """
        Fetches a web page and returns a parsed BeautifulSoup object.

        Args:
            url (str): the page URL to fetch

        Returns:
            BeautifulSoup: parsed HTML, or None on failure
        """
        try:
            response = requests.get(url)
            self.logger.debug("status code: %s", response.status_code)
            self.logger.info("successfully reached %s", url)
            return BeautifulSoup(response.text, "lxml")
        except Exception as e:
            self.logger.error("could not fetch HTML soup from %s: %s", url, e)
