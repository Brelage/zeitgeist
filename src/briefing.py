import json
import markdown

def main():
    """
    creates daily briefings as .md files based on the news from the gatherers.
    keeps a set of the 7 latest briefings.
    """
    briefing = read_daily_news()
    save_briefing(briefing)
    remove_old_briefings()



def read_daily_news():
    entries = []
    dates = set()
    with open("data/archive.jsonl", "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                try:
                    entry = json.loads(line)
                    entries.append(entry)
                    if "gathered_date" in entry:
                        dates.add(entry["gathered_date"])
                except json.JSONDecodeError as e:
                    print(f"""Skipping invalid JSON line: \n
                          {line}. \n
                          Error: {e}\n""")
                    continue
    
    if not dates:
        return []
    
    latest_date = max(dates)
    latest_entries = [
        entry for entry in entries
        if entry.get('gathered_date') == latest_date
    ]
    return latest_entries


def save_briefing(briefing):
    for i in briefing:
        line_item = i["title"]



def remove_old_briefings():
    pass


if __name__ == "__main__":
    main()