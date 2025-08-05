import requests
import logging
import os
import sys
from pathlib import Path
from bs4 import BeautifulSoup as bs

sys.path.append(str(Path(__file__).resolve().parents[1]))
from utils import Gatherer

def main():
    gatherer = Zeit()
    gatherer.scrape_headlines()
    #gatherer.scrape_most_read()
    gatherer.save_capsule()



class Zeit(Gatherer):
    def __init__(self):
        super().__init__()
        self.source = "https://www.zeit.de/index"
        self.soup = self.get_soup()


    def get_soup(self):
        try:
            response = requests.get(self.source)
            self.logger.debug(f"status code: {response.status_code}")
            self.logger.info("successfully reached %s", self.source)
            soup = bs(response.text, "lxml")
            
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

        for paragraph in paragraphs:
            try:
                # Extract components
                strong_tag = paragraph.find("strong")
                link_tag = paragraph.find("a")
                
                title = strong_tag.get_text().strip() if strong_tag else ""
                url = link_tag.get("href") if link_tag else ""
                
                # Get full text and remove title part
                full_text = paragraph.get_text()
                if title:
                    content = full_text.replace(title, "", 1).strip().lstrip(':').strip()
                else:
                    content = full_text.strip()
                
                capsule_part = self.create_json_structure(
                    title=title,
                    content=content,
                    url=url,
                    source=self.source,
                    language="de"
                )
                self.capsule.append(capsule_part)
            

            except Exception as e:
                self.logger.error(f"Error processing paragraph: {e}")
                continue
            
        self.logger.info("successfully gathered headlines from 'Das Wichtigste in Kürze'")


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