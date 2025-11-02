import json
import argparse
from datetime import date, datetime
from utils import setup_logger

logger = setup_logger()

def generate_capsule(file_path: str, capsule_date: str = None):
    """
    Generates a capsule of news articles for a specific day from a JSONL file.

    Args:
        file_path (str): The path to the JSONL file containing the news data.
        capsule_date (str, optional): The date for which to generate the capsule in 'YYYY-MM-DD' format.
                                     If not provided, the summary will be for the current date.
    """
    articles = []
    with open(file_path, 'r') as f:
        for line in f:
            try:
                articles.append(json.loads(line))
            except json.JSONDecodeError:
                logger.error(f"Skipping invalid JSON line: {line.strip()}")

    if capsule_date:
        target_date = date.fromisoformat(capsule_date)
    else:
        target_date = datetime.now().date()

    logger.info(f"Generating capsule for {target_date.isoformat()}...")

    # Filter articles for the target date
    day_articles = [article for article in articles if article['gathered_date'] == target_date.isoformat()]

    if not day_articles:
        logger.info(f"No articles found for {target_date.isoformat()}.")
        return

    # Format articles in a human-readable way
    capsule_content = f"# News Capsule for {target_date.isoformat()}\n\n"
    for article in day_articles:
        capsule_content += f"## {article['title']}\n\n"
        capsule_content += f"> Source: {article['source']}\n"
        capsule_content += f"> URL: {article['url']}\n\n"
        capsule_content += f"{article['content']}\n\n"
        capsule_content += "---\n\n"

    # Save the formatted content to a file
    capsule_filename = f"data/capsules/{target_date.isoformat()}.md"
    with open(capsule_filename, 'w') as f:
        f.write(capsule_content)

    logger.info(f"Capsule saved to {capsule_filename}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate a news capsule for a specific date.')
    parser.add_argument('--date', help="The date for which to generate the capsule in 'YYYY-MM-DD' format.")
    args = parser.parse_args()

    generate_capsule('data/archive.jsonl', args.date)