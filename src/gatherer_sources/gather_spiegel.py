import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from gatherer_types.gatherer_rss import GathererRSS


def main():
    gatherer = GatherSpiegel()
    gatherer.fetch_feed()
    gatherer.save_capsule()


class GatherSpiegel(GathererRSS):
    def __init__(self):
        super().__init__()
        self.source = "https://www.spiegel.de/schlagzeilen/index.rss"
        self.language = "de"


if __name__ == "__main__":
    main()
