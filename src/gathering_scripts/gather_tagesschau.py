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



if __name__ == "__main__":
    main()