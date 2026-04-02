import requests
import sys
from pathlib import Path
from bs4 import BeautifulSoup as bs

sys.path.append(str(Path(__file__).resolve().parents[1]))
from utils import Gatherer

def main():
    gatherer = Japan_Times()
    gatherer.scrape_headlines()
    gatherer.scrape_most_read()
    gatherer.save_capsule()



class Japan_Times(Gatherer):
    def __init__(self):
        super().__init__()
        self.source = "https://www.japantimes.co.jp/"

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


    def fetch_japantimes_news(self):
        data = requests.get(self.source).json()
        self.logger.info("reached Japan Times API")
        news = data["news"]
        
        for item in news[:5]:
            title = item["title"]
            text = item.get("content", [])
            link = item["detailsweb"]
            content = ""
            for entry in text[:4]:
                content += entry.get("value", "")
            content = self.dot_parse(self.clean_html_content(content))
            category = item.get("ressort")
            breaking_news = item["breakingNews"]
            
            capsule_part = self.create_json_structure(
                title,
                content,
                link,
                self.source,
                language="de",
                category=category,
                is_breaking_news=breaking_news
            )
            self.capsule.append(capsule_part)