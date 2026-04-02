import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from gatherer_types.gatherer_api import GathererAPI


def main():
    gatherer = GatherTagesschau()
    gatherer.fetch_tagesschau_headlines()
    gatherer.save_capsule()


class GatherTagesschau(GathererAPI):
    def __init__(self):
        super().__init__()
        self.source = "https://www.tagesschau.de/api2u/homepage/"


    def fetch_tagesschau_headlines(self):
        data = self.fetch(self.source)
        news = data["news"]

        for item in news[:5]:
            title = item["title"]
            text = item.get("content", [])
            link = item["detailsweb"]

            entries = []
            for entry in text[:4]:
                value = self.clean_html_content(entry.get("value", "")).rstrip()
                if value:
                    entries.append(value)
            content = self.normalize_content(". ".join(entries))

            category = item.get("ressort")
            breaking_news = item["breakingNews"]

            self.capsule.append(self.create_json_structure(
                title,
                content,
                link,
                self.source,
                language="de",
                category=category,
                is_breaking_news=breaking_news,
            ))


if __name__ == "__main__":
    main()
