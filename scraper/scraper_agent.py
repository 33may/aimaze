import random

from loguru import logger

from scraper.content_processor import PageProcessor, ParsingError, html_to_md
from collections import deque


class ScraperAgent:
    def __init__(self, url):
        self.url = url

        self.queue = deque()
        self.queue.append(url)

        self.visited = [url]

        self.result = []

    def scrape(self):
        while self.queue:
            cur_url = self.queue.popleft()

            try:
                page_processor = PageProcessor(cur_url)
            except ParsingError:
                logger.error(f"Parsing Error foor page {cur_url}")
                continue

            content = page_processor.content

            if self._is_page_useful(content):
                logger.debug(f"Page {cur_url} is useful")
                self.result.append({
                    'url': cur_url,
                    'content': html_to_md(content),
                })

            internal_links, _ = page_processor.get_all_links()

            for link in internal_links:
                if self._is_link_useful(content, link) and link not in self.visited:
                    logger.debug(f"Link {link} is useful")
                    self.queue.append(link)
                    self.visited.append(link)
                # else:
                #     logger.debug(f"Link {link} skip")

        logger.debug([f"link: {item["url"]} content: {item["content"][:100]}\n" for item in self.result])
        return self.result


    def _is_page_useful(self, content: str) -> bool:
        return random.random() > 0.33

    def _is_link_useful(self, content: str, next_url: str) -> bool:
        return random.random() > 0.33