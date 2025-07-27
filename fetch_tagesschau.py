import requests
import yaml
from utils import setup_logger

with open("sources.yaml", "r") as file:
    data = yaml.safe_load(file)
    tagesschau = data["tagesschau"]

logger = setup_logger()

def main():
    scrape_tagesschau_headlines()

def scrape_tagesschau_headlines():
    data = requests.get(tagesschau).json()
    logger.info("reached Tagesschau API")
    
    news = data["news"]
    for item in news[:5]:
        headline = item["title"]
        link = item["detailsweb"]
        content = item.get("content", [])
        text = ""
        for entry in content[:2]:
            text += "  -" + entry.get("value", "") + "\n"
        
        aricle = f"""
        {headline}
        {link}
        {text}
        """


if __name__ == "__main__":
    main()