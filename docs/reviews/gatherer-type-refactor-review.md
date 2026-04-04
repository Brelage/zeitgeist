# Code Review: Gatherer Type Refactor

**Proposal:** [docs/proposals/gatherer-type-refactor.md](../proposals/gatherer-type-refactor.md)
**Review date:** 2026-04-04

---

## What matched the proposal

The core three-tier hierarchy was implemented correctly:

- `utils.py` stripped to `setup_logger()` only
- `gatherer_base.py` with `GathererBase` extracted verbatim
- `gatherer_types/` package with all three types (`gatherer_api.py`, `gatherer_web.py`, `gatherer_rss.py`)
- Source scripts moved to `gatherer_sources/`, class names updated (`GatherTagesschau`, `GatherZeit`)
- `SCRIPTS_DIR` updated in `run_gatherers.py`
- `feedparser` added to both `requirements.txt` and `pyproject.toml`
- `README.md` updated to reference `gatherer_sources`

---

## Deviations from the proposal

**`GatherSpiegel` is in `workbench/`, not `src/gatherer_sources/`**
The proposal designated step 8 as a separate commit for net-new functionality. The script exists but is parked in `workbench/`, so `run_gatherers.py` never discovers it. Intentional staging, but unfinished.

**`GathererRSS` has no `__init__`**
The proposal showed stub assignments `self.source = ""` and `self.language = ""` in `GathererRSS.__init__`. The implementation omits this entirely, relying on subclasses to set these before calling `fetch_feed()`. This is consistent with `GathererAPI` and `GathererWeb`, neither of which define constructors. The inconsistency surfaces a real design question though: `fetch_feed()` reads `self.source` and `self.language` implicitly, while `fetch(url)` and `get_soup(url)` take URL as an explicit parameter. The type layer is stateless for API and Web, but stateful for RSS — worth a conscious decision either way.

**`language` field inconsistency unresolved**
The proposal flagged this as an open question. `GatherSpiegel` sets `self.language` as a subclass attribute (consumed by `GathererRSS.fetch_feed()`), but `GatherTagesschau` and `GatherZeit` pass `language="de"` as a literal string inline. The pattern is inconsistent across sources.

---

## Bugs

**`workbench/gather_spiegel.py` has a broken import path**
`sys.path.append(str(Path(__file__).resolve().parents[1]))` from `workbench/` resolves to the project root. But `gatherer_types/` lives inside `src/`. Running it directly raises `ModuleNotFoundError`.

**~~`gatherer_base.py` `sys.path` append is fragile~~** *(fixed)*
Changed `parents[1]` to `parents[0]` so the path appended is `src/` rather than the project root, making `from utils import setup_logger` work when `gatherer_base.py` is run in isolation.

**`gather_zeit.py:42` duplicates line 41**
```python
content = self.normalize_content(full_text.replace(title, "", 1).strip().lstrip(':').strip())
content = self.normalize_content(full_text.replace(title, "", 1).strip().lstrip(':').strip())
```
`normalize_content` is idempotent so there is no visible bug, but one line is dead code.

---

## Weaknesses and potential failures

**`scrape_headlines()` and `scrape_most_read()` assume `fetch_website()` was called first**
If `self.soup` is unset, both methods raise `AttributeError`. Acceptable under the explicit step convention — the call sequence is the caller's responsibility — but worth noting.

**~~`GathererAPI.fetch()` has no error handling~~** *(fixed)*
Added `try/except` matching the pattern in `GathererWeb.fetch_website()`. Returns `None` on failure; callers guard with `if data is None`.

**~~All gatherers log to the same file~~** *(fixed)*
Changed `setup_logger(__name__)` to `setup_logger(type(self).__name__)` in `GathererBase.__init__`. `type(self)` resolves to the instantiated subclass at runtime, so `GatherTagesschau` logs to `logs/GatherTagesschau.log`, `GatherZeit` to `logs/GatherZeit.log`, etc.

**~~RSS UTC timezone issue~~** *(fixed)*
Changed `datetime.now()` to `datetime.now(timezone.utc)` in `GathererBase.__init__`. `self.today` is now always a UTC date, consistent with feedparser's `published_parsed` and the `gathered_date` field written to the archive.

**`fcntl` file lock is never actually contended**
`save_capsule()` uses `fcntl.flock` to guard against concurrent writes. But `run_gatherers.py` uses blocking `subprocess.run()`, so gatherers execute sequentially. The lock is correct defensive code for a future parallel implementation, but currently does nothing.

**~~`pyproject.toml` missing dependencies~~** *(fixed)*
Added `Markdown` and `urllib3` to `pyproject.toml` dependencies to match `requirements.txt`. `setuptools` is already covered by `[build-system].requires` and is not a runtime dependency.
