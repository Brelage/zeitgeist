import requests
import logging
from logging.handlers import TimedRotatingFileHandler
import os

from bs4 import BeautifulSoup as bs

from config import LOG_LEVEL

def main():
    scraper = Scraper()
    scraper.scrape()


class Scraper:
    def __init__(self):
        self.zeit_url = "https://www.zeit.de/index"
        self.tagesschau_url = "https://www.tagesschau.de/"
        
        self.zeit_website = None
        self.tagesschau_website = None
        
        self.setup_logger()
        


    def setup_logger(self):

        logs_path = os.path.join("logs")
        os.makedirs(logs_path, exist_ok=True)
        
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(LOG_LEVEL)  

        if not self.logger.handlers:
            formatter = logging.Formatter(fmt="%(asctime)s: %(message)s", datefmt="%Y.%m.%d %H:%M:%S")
            
            ## config for the .log file generated
            file_handler = TimedRotatingFileHandler(
                f"logs/scraper.log",
                when="midnight",
                backupCount=3
            )
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
            
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(formatter)
            self.logger.addHandler(stream_handler)


    def scrape(self):
        try:
            response = requests.get(self.zeit_url)
            self.logger.debug(f"status code: {response.status_code}")
            self.logger.info("successfully reached %s", self.zeit_url)
            soup = bs(response.text, "lxml")

            if self.logger.isEnabledFor(logging.DEBUG):
                os.makedirs("workbench", exist_ok=True)
                with open(f"workbench/soup_html_{self.parent.today}.html", "w") as file:
                    file.write(soup.prettify())
        except:
            self.logger.error("could not scrape successfully")

if __name__ == "__main__":
    main()