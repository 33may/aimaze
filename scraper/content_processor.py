import requests
from requests import get
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from markdownify import markdownify as md
from urllib.parse import urljoin


class ParsingError(Exception):
    """
    Custom exception raised when content parsing fails.
    """
    pass


class ContentProcessor:
    """
    A class to process and extract information from web content.

    Attributes:
        link (str): The URL of the web page to process.
        protected (bool): A flag indicating whether the page is protected and might require special handling.
    """

    def __init__(self, link, protected=False):
        self.link = link

        parsed_url = urlparse(link)
        self.link_base = parsed_url.netloc

        self.protected = protected
        self.content = self._get_content()


    def _get_content(url: str, auth_info=None) -> str:
        try:
            r = get(url)

            if not r.status_code == 200:
                raise Exception(f"Couldn't access page: {url} (HTTP {r.status_code})")  # TODO: Better way to handle this than nuke button.

            return r.content
        except requests.RequestException as e:
            print(f"Error fetching content from {self.link}: {e}")
            raise ParsingError

    def html_to_md(self, html: str) -> str:
        return md(html)

    def get_all_links(self):
        """
        Parses the HTML content and extracts all hyperlinks.

        Returns:
            (internal_links list, external_links list): A list of URLs extracted from <a> tags in the HTML content.
        """
        html = self.content
        if html is None:
            return []
        soup = BeautifulSoup(html, 'html.parser')

        links = []
        for a in soup.find_all('a', href=True):
            href = a['href'].strip()
            # Skip empty, anchor-only, javascript, or mailto links
            if not href or href.startswith("#") or href.startswith("javascript:") or href.startswith("mailto:"):
                continue
            absolute_url = urljoin(self.link, href)
            links.append(absolute_url)

        internal_links = []
        external_links = []
        for link in links:
            parsed = urlparse(link)
            if parsed.scheme not in ['http', 'https']:
                continue
            if parsed.netloc == self.link_base:
                internal_links.append(link)
            else:
                external_links.append(link)

        return internal_links, external_links