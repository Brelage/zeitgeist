import feedparser
import sys
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).resolve().parents[1]))
from gatherer_base import GathererBase


class GathererRSS(GathererBase):
    """
    Gatherer type for RSS feed sources.
    Provides fetch_feed() which handles feedparser integration, date filtering
    to today's entries, and HTML cleaning of descriptions.
    Subclasses set self.source and self.language.
    """

    def fetch_feed(self):
        """
        Fetches the RSS feed at self.source, filters to entries published today,
        and appends normalized entries to self.capsule.
        """
        feed = feedparser.parse(self.source)
        self.logger.info("fetched RSS feed: %s", self.source)

        for entry in feed.entries:
            published = entry.get("published_parsed")
            if not published:
                continue
            if datetime(*published[:3]).date().isoformat() != self.today:
                continue

            title = entry.get("title", "")
            link = entry.get("link", "")
            content = self.normalize_content(
                self.clean_html_content(entry.get("summary", ""))
            )

            self.capsule.append(self.create_json_structure(
                title=title,
                content=content,
                url=link,
                source=self.source,
                language=self.language,
            ))
