import cloudscraper
import time
import random
import sys
from pathlib import Path
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

sys.path.append(str(Path(__file__).resolve().parents[1]))
from gatherer_base import GathererBase


TIMEOUT = 10
MAX_RETRIES = 3


class GathererWeb(GathererBase):
    """
    Gatherer type for HTML scraping sources.
    Provides a fetch_website() method that handles fetching and parsing.
    Subclasses receive the BeautifulSoup object and implement extraction logic.
    """

    def fetch_website(self, url):
        """
        Fetches a web page and returns a parsed BeautifulSoup object.
        Uses cloudscraper for Cloudflare bypass and a randomized user agent
        to avoid bot detection. Adds a randomized delay before the request
        to avoid machine-regular cadence, and retries with exponential backoff
        on timeout.

        Args:
            url (str): the page URL to fetch

        Returns:
            BeautifulSoup: parsed HTML, or None on failure
        """
        ua = UserAgent()
        headers = {
            "User-Agent": ua.random,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "*",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Cache-Control": "max-age=0",
        }

        session = cloudscraper.CloudScraper()
        session.headers.update(headers)

        time.sleep(random.uniform(1.5, 4.0))

        for attempt in range(MAX_RETRIES):
            try:
                response = session.get(url, timeout=TIMEOUT)
                self.logger.debug("status code: %s", response.status_code)
                self.logger.info("successfully reached %s", url)
                return BeautifulSoup(response.text, "lxml")
            except cloudscraper.exceptions.CloudflareChallengeError as e:
                self.logger.error("Cloudflare challenge failed for %s: %s", url, e)
                return None
            except Exception as e:
                if "timeout" in str(e).lower():
                    wait = 2 ** (attempt + 1)
                    self.logger.warning("request timed out for %s (attempt %d/%d), retrying in %ds", url, attempt + 1, MAX_RETRIES, wait)
                    time.sleep(wait)
                else:
                    self.logger.error("could not fetch HTML from %s: %s", url, e)
                    return None

        self.logger.error("all %d attempts timed out for %s", MAX_RETRIES, url)
        return None
