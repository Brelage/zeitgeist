import requests
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from utils import Gatherer


def main():
    gatherer = Tagesschau()
    gatherer.fetch_tagesschau_headlines()
    gatherer.save_capsule()


class Tagesschau(Gatherer):
    def __init__(self):
        super().__init__()
        self.source = "https://www.tagesschau.de/api2u/homepage/"


    def fetch_tagesschau_headlines(self):
        data = requests.get(self.source).json()
        self.logger.info("reached Tagesschau API")
        news = data["news"]
        
        for item in news[:5]:
            title = item["title"]
            content = item.get("content", [])
            link = item["detailsweb"]
            text = ""
            for entry in content[:4]:
                text += entry.get("value", "")
            text = self.clean_html_content(text)
            category = item.get("ressort")
            breaking_news = item["breakingNews"]
            
            capsule_part = self.create_json_structure(
                title,
                text,
                link,
                self.source,
                language="de",
                category=category,
                is_breaking_news=breaking_news
            )
            self.capsule.append(capsule_part)



if __name__ == "__main__":
    main()