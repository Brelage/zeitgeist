import requests
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from gatherer_base import GathererBase


class GathererAPI(GathererBase):
    """
    Gatherer type for JSON API sources.
    Provides a fetch() method that handles the HTTP request and logging.
    Subclasses receive the parsed JSON and implement extraction logic.
    """

    def fetch(self, url):
        """
        Fetches a JSON API endpoint and returns the parsed response.

        Args:
            url (str): the API endpoint to fetch

        Returns:
            dict: parsed JSON response
        """
        response = requests.get(url).json()
        self.logger.info("reached API: %s", url)
        return response
