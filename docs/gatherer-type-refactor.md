# Gatherer Type Refactor Proposal

## Motivation

The current codebase has two source-specific gatherers (`gather_tagesschau.py`, `gather_zeit.py`) that both inherit directly from `Gatherer` in `utils.py`. As the number of sources grows, two problems emerge:

1. **`utils.py` conflates two concerns** — infrastructure utilities (logging setup, file I/O) and the base gatherer class. These should be separate.
2. **No intermediate layer for source-type logic** — each new RSS gatherer would independently re-implement feedparser setup and date filtering; each new web scraper would re-implement BeautifulSoup initialization. Shared source-type logic has nowhere to live.

The refactor introduces a clean three-tier class hierarchy and separates infrastructure from base class.

---

## Proposed Structure

```
src/
  utils.py                          ← infrastructure only: setup_logger, standalone helpers
  gatherer_base.py                  ← Gatherer base class
  gatherer_types/
    __init__.py
    gatherer_api.py                 ← APIGatherer(Gatherer)
    gatherer_rss.py                 ← RSSGatherer(Gatherer)
    gatherer_web.py                 ← WebGatherer(Gatherer)
  gathering_scripts/
    gather_tagesschau.py            ← Tagesschau(APIGatherer)
    gather_zeit.py                  ← Zeit(WebGatherer)
    gather_spiegel.py               ← Spiegel(RSSGatherer)   [new]
```

### Dependency chain

```
utils.py → gatherer_base.py → gatherer_types/gatherer_*.py → gathering_scripts/gather_*.py
```

Each layer only imports from the layer directly above it. Source scripts contain no logic beyond extraction and field mapping.

---

## Layer Responsibilities

### `utils.py`
Unchanged in content, reduced in scope. Retains only:
- `setup_logger()`
- Any future standalone helper functions

### `gatherer_base.py` — `Gatherer`
Extracted from `utils.py`. Owns everything shared across all gatherer types:
- `__init__`: logger, date, archive path, capsule list
- `clean_html_content()`
- `normalize_content()`
- `dot_parse()`
- `create_json_structure()`
- `save_capsule()`

### `gatherer_types/gatherer_api.py` — `APIGatherer(Gatherer)`
Shared logic for JSON API sources:
- `fetch(url)`: executes `requests.get(url).json()` with logging
- Subclasses receive the parsed JSON and handle extraction

**Current source using this type:** Tagesschau

### `gatherer_types/gatherer_web.py` — `WebGatherer(Gatherer)`
Shared logic for HTML scraping sources:
- `get_soup(url)`: fetches the page and returns a BeautifulSoup object with error handling and logging
- Subclasses receive the soup and handle extraction

**Current source using this type:** Zeit

### `gatherer_types/gatherer_rss.py` — `RSSGatherer(Gatherer)`
Shared logic for RSS feed sources:
- `fetch_feed()`: calls `feedparser.parse(self.source)` and filters entries to `self.today`
- `parse_entry(entry)`: extracts title, link, and description from a standard RSS entry; calls `clean_html_content` on description since RSS descriptions frequently contain HTML
- Subclasses call `fetch_feed()` and pass results to `create_json_structure()`

Date filtering relies on `feedparser`'s `entry.published_parsed` (`time.struct_time`), converted to ISO date for comparison against `self.today`.

**Dependency to add:** `feedparser` (via `pip install feedparser`)

---

## Migration Plan

1. Create `gatherer_base.py` by extracting `Gatherer` from `utils.py`; update `utils.py` to import and re-export `Gatherer` temporarily to avoid breaking existing scripts during migration
2. Create `gatherer_types/` with `__init__.py`
3. Implement `gatherer_api.py`, `gatherer_web.py`, `gatherer_rss.py`
4. Update `gather_tagesschau.py` to inherit from `APIGatherer`
5. Update `gather_zeit.py` to inherit from `WebGatherer`
6. Remove the temporary re-export from `utils.py`
7. Implement `gather_spiegel.py` (or another RSS source) as the first concrete use of `RSSGatherer`

Steps 1–6 are a pure refactor with no behavior change. Step 7 is the first net-new functionality.

---

## New RSS Gatherer Type — `RSSGatherer`

### Core logic

```python
import feedparser
from datetime import datetime
from gatherer_base import Gatherer

class RSSGatherer(Gatherer):
    def __init__(self):
        super().__init__()
        self.source = ""  # set by subclass

    def fetch_feed(self):
        feed = feedparser.parse(self.source)
        self.logger.info("fetched RSS feed: %s", self.source)
        today = self.today  # ISO string: "2026-04-01"

        for entry in feed.entries:
            published = entry.get("published_parsed")
            if not published:
                continue
            entry_date = datetime(*published[:3]).date().isoformat()
            if entry_date != today:
                continue

            title = entry.get("title", "")
            link = entry.get("link", "")
            description = self.clean_html_content(entry.get("summary", ""))
            content = self.normalize_content(description)

            capsule_part = self.create_json_structure(
                title=title,
                content=content,
                url=link,
                source=self.source,
                language=self.language,  # set by subclass
            )
            self.capsule.append(capsule_part)
```

### Source-specific subclass example

```python
# gather_spiegel.py
from gatherer_types.gatherer_rss import RSSGatherer

class Spiegel(RSSGatherer):
    def __init__(self):
        super().__init__()
        self.source = "https://www.spiegel.de/schlagzeilen/index.rss"
        self.language = "de"

def main():
    gatherer = Spiegel()
    gatherer.fetch_feed()
    gatherer.save_capsule()

if __name__ == "__main__":
    main()
```

The source script contains nothing but a URL, a language code, and the standard `main()` boilerplate — consistent with the adapter pattern established by the existing gatherers.

---

## Open Questions

- **`language` field**: currently hardcoded per source script. Could be moved to a subclass attribute (as shown above) or kept in `create_json_structure` calls. The subclass attribute approach is cleaner for RSS since `fetch_feed()` calls `create_json_structure` internally.
- **Category field**: RSS entries sometimes carry a `<category>` tag. `RSSGatherer` could optionally map this to the `category` field in `create_json_structure`.
- **Timezone handling**: `published_parsed` from feedparser is in UTC. If a feed publishes at 23:00 UTC and the local date is the next day, entries could be missed. Acceptable tradeoff for a daily gatherer, but worth noting.
