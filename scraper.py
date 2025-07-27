import requests
import logging
import os
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

from bs4 import BeautifulSoup as bs

from config import LOG_LEVEL

def main():
    scraper = Scraper()
    scraper.scrape()


class Scraper:
    def __init__(self):
        self.zeit_url = "https://www.zeit.de/index"
        self.tagesschau_url = "https://www.tagesschau.de/"
        self.today = datetime.now().date()

        self.logger = self.setup_logger()
        

    def setup_logger(self):

        logs_path = os.path.join("logs")
        os.makedirs(logs_path, exist_ok=True)
        
        logger = logging.getLogger(__name__)
        logger.setLevel(LOG_LEVEL)  

        if not logger.handlers:
            formatter = logging.Formatter(fmt="%(asctime)s: %(message)s", datefmt="%Y.%m.%d %H:%M:%S")
            
            ## config for the .log file generated
            file_handler = TimedRotatingFileHandler(
                f"logs/scraper.log",
                when="midnight",
                backupCount=3
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(formatter)
            logger.addHandler(stream_handler)

            return logger


    def scrape(self):
        try:
            response = requests.get(self.zeit_url)
            self.logger.debug(f"status code: {response.status_code}")
            self.logger.info("successfully reached %s", self.zeit_url)
            soup = bs(response.text, "lxml")

            if self.logger.isEnabledFor(logging.DEBUG):
                os.makedirs("workbench", exist_ok=True)
                with open(f"workbench/soup_html_{self.today}.html", "w") as file:
                    file.write(soup.prettify())

            match = soup.find_all("section", 
                                    class_="cp-area cp-area--headed",
                                    attrs= {"data-ct-context": "headed-das_wichtigste_in_kuerze"})
            headlines = match[0].find("div", class_="zon-markup-with-author__content")
            paragraphs = headlines.find_all("p")
            paragraphs[-1].decompose()
            self.logger.info("successfully extracted headlines")

            if self.logger.isEnabledFor(logging.DEBUG):
                with open(f"workbench/match{self.today}.html", "w") as file:
                        file.write(str(headlines))
        
        except Exception as e:
            self.logger.error("could not scrape successfully")
            self.logger.error(f"{e}")



if __name__ == "__main__":
    main()