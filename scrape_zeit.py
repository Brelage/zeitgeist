import requests
import logging
import os
import yaml
from datetime import datetime
from bs4 import BeautifulSoup as bs
from utils import setup_logger


with open("sources.yaml", "r") as file:
    data = yaml.safe_load(file)
    zeit = data["zeit"]


def main():
    Scraper()
    Scraper.scrape_zeit_headlines()
    Scraper.scrape_zeit_most_read()



class Scraper:
    def __init__(self):
        self.logger = setup_logger()
        self.today = datetime.now().date()
        self.soup = self.get_soup()


    def get_soup(self):
        try:
            response = requests.get(zeit)
            self.logger.debug(f"status code: {response.status_code}")
            self.logger.info("successfully reached %s", self.zeit_url)
            soup = bs(response.text, "lxml")

            if self.logger.isEnabledFor(logging.DEBUG):
                os.makedirs("workbench", exist_ok=True)
                with open(f"workbench/{self.today}_{zeit}.html", "w") as file:
                    file.write(soup.prettify())
            
            return soup
        
        except Exception as e:
            self.logger.error("could not fetch HTML-soup successfully")
            self.logger.error(f"{e}")


    def scrape_zeit_headlines(self):
        match = self.soup.find_all("section", 
                                class_="cp-area cp-area--headed",
                                attrs= {"data-ct-context": "headed-das_wichtigste_in_kuerze"})
        headlines = match[0].find("div", class_="zon-markup-with-author__content")
        paragraphs = headlines.find_all("p")
        paragraphs[-1].decompose()
        headlines_p = "".join(str(p) for p in paragraphs)
        
        self.logger.info("successfully extracted headlines from 'Das Wichtigste in Kürze'")

        if self.logger.isEnabledFor(logging.DEBUG):
            with open(f"workbench/match{self.today}.html", "w") as file:
                    file.write(str(headlines_p))


    def scrape_zeit_most_read(self):
        match = self.soup.find_all("section", 
                                class_="cp-area cp-area--headed",
                                attrs= {"data-ct-context": "headed-das_wichtigste_in_kuerze"})



if __name__ == "__main__":
    main()