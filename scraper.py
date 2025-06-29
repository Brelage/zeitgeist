from bs4 import BeautifulSoup as bs
import requests
import logging
import os

def main():
    scraper = Scraper()
    scraper.scrape()
    pass


class Scraper:
    def __init__(self):
        self.url = "https://www.zeit.de/index"
        self.setup_logger()
        pass


    def setup_logger(self):
        logging.basicConfig(level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)


    def scrape(self):
        try:
            response = requests.get(self.url)
            self.logger.debug(f"status code: {response.status_code}")
            self.logger.info("successfully reached %s", self.url)
            soup = bs(response.text, "lxml")

            if self.logger.isEnabledFor(logging.DEBUG):
                os.makedirs("workbench", exist_ok=True)
                with open(f"workbench/soup_html_{self.parent.today}.html", "w") as file:
                    file.write(soup.prettify())
        except:
            self.logger.error("could not scrape successfully")

if __name__ == "__main__":
    main()