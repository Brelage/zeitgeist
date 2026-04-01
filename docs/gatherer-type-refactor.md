# Gatherer Type Refactor Proposal

## Motivation

The current codebase has two source-specific gatherers (`gather_tagesschau.py`, `gather_zeit.py`) that both inherit directly from `Gatherer` in `utils.py`. As the number of sources grows, two problems emerge:

1. **`utils.py` conflates two concerns** — infrastructure utilities (logging setup) and the base gatherer class. These should be separate.
2. **No intermediate layer for source-type logic** — each new RSS gatherer would independently re-implement feedparser setup and date filtering; each new web scraper would re-implement BeautifulSoup initialization. Shared source-type logic has nowhere to live.

The refactor introduces a clean three-tier class hierarchy and separates infrastructure from base class.

---

## Proposed Structure

```
src/
  utils.py                              ← infrastructure only: setup_logger
  gatherer_base.py                      ← GathererBase (base class)
  gatherer_types/
    __init__.py
    gatherer_api.py                     ← GathererAPI(GathererBase)
    gatherer_rss.py                     ← GathererRSS(GathererBase)
    gatherer_web.py                     ← GathererWeb(GathererBase)
  gatherer_sources/
    gather_tagesschau.py                ← GatherTagesschau(GathererAPI)
    gather_zeit.py                      ← GatherZeit(GathererWeb)
    gather_spiegel.py                   ← GatherSpiegel(GathererRSS)   [new]
```

### Dependency chain

```
utils.py → gatherer_base.py → gatherer_types/gatherer_*.py → gatherer_sources/gather_*.py
```

Each layer only imports from the layer directly above it. Source scripts contain no logic beyond extraction and field mapping. Class names match their script names in PascalCase.

---

## Layer Responsibilities

### `utils.py`
Unchanged in content, reduced in scope. Retains only:
- `setup_logger()`

### `gatherer_base.py` — `GathererBase`
Extracted from `utils.py`. Owns everything shared across all gatherer types:
- `__init__`: logger, date, archive path, capsule list
- `clean_html_content()`
- `normalize_content()`
- `dot_parse()`
- `create_json_structure()`
- `save_capsule()`

### `gatherer_types/gatherer_api.py` — `GathererAPI(GathererBase)`
Shared logic for JSON API sources:
- `fetch(url)`: executes `requests.get(url).json()` with logging
- Subclasses receive the parsed JSON and handle extraction

**Current source using this type:** `GatherTagesschau`

### `gatherer_types/gatherer_web.py` — `GathererWeb(GathererBase)`
Shared logic for HTML scraping sources:
- `get_soup(url)`: fetches the page, returns a BeautifulSoup object with error handling and logging
- Subclasses receive the soup and handle extraction

**Current source using this type:** `GatherZeit`

### `gatherer_types/gatherer_rss.py` — `GathererRSS(GathererBase)`
Shared logic for RSS feed sources:
- `fetch_feed()`: calls `feedparser.parse(self.source)`, filters entries to `self.today`, delegates extraction
- `parse_entry(entry)`: extracts title, link, description; calls `clean_html_content` and `normalize_content`

Date filtering uses `feedparser`'s `entry.published_parsed` (`time.struct_time`), converted to ISO date for comparison against `self.today`.

**Dependency to add:** `feedparser` to `requirements.txt` and `pyproject.toml`

---

## Full List of Affected Files

### `src/utils.py`
Remove the `Gatherer` class entirely. Retain only `setup_logger()` and its imports. All gatherer scripts currently import `Gatherer` from here — those imports change as part of this refactor, so no temporary re-export is needed if all files are updated in a single commit.

### `src/gatherer_base.py` ← new file
Contains `GathererBase`, extracted verbatim from the current `Gatherer` class in `utils.py`. Imports `setup_logger` from `utils`.

### `src/gatherer_types/__init__.py` ← new file
Empty, makes `gatherer_types` a package.

### `src/gatherer_types/gatherer_api.py` ← new file
`GathererAPI(GathererBase)` with shared API fetch logic.

### `src/gatherer_types/gatherer_web.py` ← new file
`GathererWeb(GathererBase)` with shared BeautifulSoup setup, extracted from the current `get_soup()` pattern in `gather_zeit.py`.

### `src/gatherer_types/gatherer_rss.py` ← new file
`GathererRSS(GathererBase)` with feedparser integration and date filtering.

### `src/gatherer_sources/gather_tagesschau.py` ← renamed + updated
- Moved from `src/gathering_scripts/gather_tagesschau.py`
- Class renamed from `Tagesschau` to `GatherTagesschau`
- Import updated: `from gatherer_types.gatherer_api import GathererAPI`
- `sys.path.append` remains `parents[1]` (still resolves to `src/`)

### `src/gatherer_sources/gather_zeit.py` ← renamed + updated
- Moved from `src/gathering_scripts/gather_zeit.py`
- Class renamed from `Zeit` to `GatherZeit`
- Import updated: `from gatherer_types.gatherer_web import GathererWeb`
- `get_soup()` method removed (moves to `GathererWeb`)

### `src/gatherer_sources/gather_spiegel.py` ← new file
- `GatherSpiegel(GathererRSS)`: sets `self.source` and `self.language`, calls `fetch_feed()` and `save_capsule()`

### `src/gatherer.py`
Update `SCRIPTS_DIR`:
```python
# before
SCRIPTS_DIR = Path(__file__).parent / "gathering_scripts"
# after
SCRIPTS_DIR = Path(__file__).parent / "gatherer_sources"
```

### `.github/workflows/gather_news.yml`
No direct path change needed — it only calls `src/gatherer.py`, which handles the directory lookup internally. Verify the workflow still passes after `gatherer.py` is updated.

### `.github/workflows/generate_capsule.yml`
No changes needed. It calls `src/capsule_generator.py`, which only imports `setup_logger` from `utils.py` — that function stays in `utils.py`.

### `requirements.txt`
Add `feedparser` (current latest stable: `6.0.11`).

### `pyproject.toml`
Add `feedparser` to the `dependencies` list.

### `README.md`
Two references need updating:
- *"automation scripts for news sources are added in the `gathering_scripts` folder"* → `gatherer_sources`
- *"use the Gatherer class in `utils.py`"* → `gatherer_base.py`

---

## New RSS Gatherer — `GathererRSS` and `GatherSpiegel`

### `gatherer_types/gatherer_rss.py`

```python
import feedparser
from datetime import datetime
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from gatherer_base import GathererBase


class GathererRSS(GathererBase):
    def __init__(self):
        super().__init__()
        self.source = ""    # set by subclass
        self.language = ""  # set by subclass

    def fetch_feed(self):
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
```

### `gatherer_sources/gather_spiegel.py`

```python
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from gatherer_types.gatherer_rss import GathererRSS


class GatherSpiegel(GathererRSS):
    def __init__(self):
        super().__init__()
        self.source = "https://www.spiegel.de/schlagzeilen/index.rss"
        self.language = "de"


def main():
    gatherer = GatherSpiegel()
    gatherer.fetch_feed()
    gatherer.save_capsule()


if __name__ == "__main__":
    main()
```

---

## Migration Plan

All steps below are a pure refactor with no behavior change, except step 8 which is the first net-new functionality.

1. Create `gatherer_base.py` — extract `GathererBase` from `utils.py`; strip `utils.py` down to `setup_logger()` only
2. Create `gatherer_types/` with `__init__.py`
3. Implement `gatherer_types/gatherer_api.py` and `gatherer_types/gatherer_web.py`
4. Rename `gathering_scripts/` → `gatherer_sources/`
5. Update `gather_tagesschau.py` and `gather_zeit.py`: new location, new class names, new imports
6. Update `src/gatherer.py`: `SCRIPTS_DIR` path
7. Update `README.md`, `requirements.txt`, `pyproject.toml`
8. Implement `gatherer_types/gatherer_rss.py` and `gatherer_sources/gather_spiegel.py`

Steps 1–7 can be a single commit. Step 8 is a separate commit as it introduces new functionality.

---

## Open Questions

- **`language` field**: currently a hardcoded string in each `create_json_structure` call. Moving it to a subclass attribute (as shown above) is cleaner for RSS since `fetch_feed()` calls `create_json_structure` internally, but this pattern could also be applied consistently across all gatherer types.
- **RSS `<category>` tag**: feedparser exposes this as `entry.tags`. `GathererRSS` could optionally map this to the `category` field in `create_json_structure` if sources provide it.
- **Timezone handling**: `published_parsed` from feedparser is in UTC. If a feed publishes at 23:00 UTC and the local system date is the next day, entries could be missed or double-counted across runs. Acceptable tradeoff for a daily gatherer, but worth noting.
