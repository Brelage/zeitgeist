import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
from gatherer_types.gatherer_web import GathererWeb


def main():
    gatherer = GatherZeit()
    website = gatherer.fetch_website(gatherer.source)
    if website is None:
        gatherer.logger.error("failed to fetch data from %s, aborting", gatherer.source)
        return
    gatherer.scrape_headlines(website)
    gatherer.scrape_most_read(website)
    gatherer.save_capsule()


class GatherZeit(GathererWeb):
    def __init__(self):
        super().__init__()
        self.source = "https://www.zeit.de/index"
        self.language = "de"


    def scrape_headlines(self, website):
        match = website.find_all("section",
                                   class_="cp-area cp-area--headed",
                                   attrs={"data-ct-context": "headed-das_wichtigste_in_kuerze"})
        headlines = match[0].find("div", class_="zon-markup-with-author__content")
        paragraphs = headlines.find_all("p")
        paragraphs[-1].decompose()
        del paragraphs[-1]

        for paragraph in paragraphs:
            try:
                strong_tag = paragraph.find("strong")
                link_tag = paragraph.find("a")

                title = strong_tag.get_text().strip() if strong_tag else ""
                url = link_tag.get("href") if link_tag else ""

                full_text = paragraph.get_text()
                if title:
                    content = self.normalize_content(full_text.replace(title, "", 1).strip().lstrip(':').strip())
                else:
                    content = self.normalize_content(full_text.strip())

                self.capsule.append(self.create_json_structure(
                    title=title,
                    content=content,
                    url=url,
                    source=self.source,
                    language=self.language,
                    is_breaking_news=True,
                ))

            except Exception as e:
                self.logger.error(f"Error processing paragraph: {e}")
                continue

        self.logger.info("successfully gathered headlines from 'Das Wichtigste in Kürze'")


    def scrape_most_read(self, website):
        match = website.find_all("div", class_="cp-region cp-region--kpi-accordion kpi-area js-accordion")

        if not match:
            self.logger.error("No accordion regions found")
            return

        accordion_sections = match[0].find_all("section", class_="z-accordion kpi-area__section cp-area cp-area--kpi js-accordion__wrapper")
        self.logger.debug(f"Found {len(accordion_sections)} accordion sections")

        most_read_section = None
        for section in accordion_sections:
            button = section.find("button", class_="z-accordion__button")
            if button and "Meistgelesen" in button.get_text():
                most_read_section = section
                break

        if not most_read_section:
            self.logger.error("Could not find 'Meistgelesen' section")
            return

        teaser_container = most_read_section.find("div", class_="kpi-area__teasers")
        if not teaser_container:
            self.logger.error("Could not find articles container")
            return

        for article in teaser_container.find_all("article", class_="zon-teaser"):
            try:
                kicker_element = article.find("a", class_="zon-teaser__faux-link")
                title = kicker_element.get_text().strip() if kicker_element else ""

                link_element = article.find("a", class_="zon-teaser__link")
                url = link_element.get("href") if link_element else ""

                summary_element = article.find("p", class_="zon-teaser__summary")
                content = self.normalize_content(summary_element.get_text().strip() if summary_element else "")

                self.capsule.append(self.create_json_structure(
                    title=title,
                    content=content,
                    url=url,
                    source=self.source,
                    language=self.language,
                ))

            except Exception as e:
                self.logger.error(f"Error processing article: {e}")
                continue

        self.logger.info("Successfully extracted 'Meistgelesen' section")


if __name__ == "__main__":
    main()
