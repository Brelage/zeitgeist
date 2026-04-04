# zeitgeist

a news gatherer and archive, providing daily briefings and perspective.


## Features

- using a GitHub Action, this project gathers a selection of news headlines and summaries.
- the data gathering automation structure is scalable, with the same automation functioning even if more automation scripts for news sources are added in the gatherer_sources folder.
- every news piece is saved as a single line in a JSONL file, enabling natural language processing.


## Dataset structure

The dataset will enable the following analysis:
1. Track political figures: "How often is 'Scholz' mentioned vs 'Merz'?"
2. Monitor crisis sentiment: "How did sentiment about inflation change in 2024?"
3. Geographic analysis: "Which German cities appear most in economic news?"
4. Source bias detection: "Does Tagesschau report more positively on EU topics than other sources?"


## Setup

Setup
1. use git clone to clone this repository into an IDE:
`git clone https://github.com/Brelage/zeitgeist`


2. install dependencies
`pip install -r requirements.txt`


3. run `src/run_gatherers.py` for manual data collection. Alternatively, use the `gather_news.yml` GitHub Action in `.github/workflows` for automated gathering.


4. add new sources by creating a script in `src/gatherer_sources/` that inherits from the appropriate gatherer type in `src/gatherer_types/`.

   Each source script follows a strict separation of configuration and behavior:
   - `__init__` is for configuration only (setting `self.source`, `self.language`, etc.) — no network calls, no side effects
   - fetching, parsing, and saving are explicit steps called in sequence by `main()`

   ```python
   def main():
       gatherer = GatherExample()   # configure
       gatherer.fetch()             # fetch
       gatherer.extract()           # parse
       gatherer.save_capsule()      # save
   ```

   This keeps instantiation safe regardless of network state, makes the execution sequence readable, and allows steps to be retried or skipped independently.


## Planned features

- daily briefings built on the gathered news
- natural language processing 
    - this project is intended to create a database to be used for statistical analysis about news headlines using natural language processing.
