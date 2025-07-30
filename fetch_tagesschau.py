import requests
import os
import logging
from datetime import datetime
from utils import setup_logger, load_source


def main():
    fetcher = Fetcher()
    fetcher.fetch_tagesschau_headlines()

class Fetcher:
    def __init__(self):
        self.logger = setup_logger(__name__)
        self.source = load_source("tagesschau")
        self.today = datetime.now().date()


    def fetch_tagesschau_headlines(self):
        data = requests.get(self.source).json()
        self.logger.info("reached Tagesschau API")
        
        tagesschau_news = []
        news = data["news"]
        for item in news[:5]:
            headline = item["title"]
            link = item["detailsweb"]
            content = item.get("content", [])
            text = ""
            for entry in content[:2]:
                text += entry.get("value", "")
            tagesschau_news.append([headline, link, text])

        if self.logger.isEnabledFor(logging.DEBUG):
            os.makedirs("workbench", exist_ok=True)
            with open(f"workbench/tagesschau{self.today}.html", "w") as file:
                    file.write(str(tagesschau_news))



if __name__ == "__main__":
    main()