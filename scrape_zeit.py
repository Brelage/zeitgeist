import requests
import logging
import os
from datetime import datetime
from bs4 import BeautifulSoup as bs
from utils import setup_logger, load_source


def main():
    scraper = Scraper()
    scraper.scrape_headlines()
    scraper.scrape_most_read()



class Scraper:
    def __init__(self):
        self.logger = setup_logger(__name__)
        self.source = load_source("zeit")
        self.today = datetime.now().date()
        self.soup = self.get_soup()


    def get_soup(self):
        try:
            response = requests.get(self.source)
            self.logger.debug(f"status code: {response.status_code}")
            self.logger.info("successfully reached %s", self.source)
            soup = bs(response.text, "lxml")

            if self.logger.isEnabledFor(logging.DEBUG):
                os.makedirs("workbench", exist_ok=True)
                with open(f"workbench/{self.today}_zeit.html", "w") as file:
                    file.write(soup.prettify())
            
            return soup
        
        except Exception as e:
            self.logger.error("could not fetch HTML-soup successfully")
            self.logger.error(f"{e}")


    def scrape_headlines(self):
        match = self.soup.find_all("section", 
                                class_="cp-area cp-area--headed",
                                attrs= {"data-ct-context": "headed-das_wichtigste_in_kuerze"})
        headlines = match[0].find("div", class_="zon-markup-with-author__content")
        paragraphs = headlines.find_all("p")
        paragraphs[-1].decompose()
        del paragraphs[-1]
        headlines_p = "".join(str(p) for p in paragraphs if p is not None and getattr(p, "name", None) is not None)
        
        self.logger.info("successfully extracted headlines from 'Das Wichtigste in Kürze'")

        if self.logger.isEnabledFor(logging.DEBUG):
            os.makedirs("workbench", exist_ok=True)
            with open(f"workbench/{self.today}headlines.html", "w") as file:
                    soup = bs(headlines_p, "lxml")
                    file.write(soup.prettify())


    def scrape_most_read(self):
        match = self.soup.find_all("div", class_="cp-region cp-region--kpi-accordion kpi-area js-accordion")
        
        if not match:
            self.logger.error("No accordion regions found")
            return
        
        # Find all accordion sections
        accordion_sections = match[0].find_all("section", class_="z-accordion kpi-area__section cp-area cp-area--kpi js-accordion__wrapper")
        self.logger.debug(f"Found {len(accordion_sections)} accordion sections")
        
        # Find the "Meistgelesen" section specifically
        most_read_section = None
        for section in accordion_sections:
            button = section.find("button", class_="z-accordion__button")
            if button and "Meistgelesen" in button.get_text():
                most_read_section = section
                break
        
        if not most_read_section:
            self.logger.error("Could not find 'Meistgelesen' section")
            return
        
        # Extract articles data from the Meistgelesen section
        most_read = most_read_section.find("div", class_="kpi-area__teasers")
    
        if not most_read:
            self.logger.error("Could not find articles container")
            return
        
        self.logger.info("Successfully extracted 'Meistgelesen' section")

        if self.logger.isEnabledFor(logging.DEBUG):
            os.makedirs("workbench", exist_ok=True)
            with open(f"workbench/{self.today}most_read.html", "w") as file:
                    soup = bs(str(most_read), "lxml")
                    file.write(soup.prettify())

        return most_read



if __name__ == "__main__":
    main()