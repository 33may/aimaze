import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin


class ParsingError(Exception):
    """
    Custom exception raised when content parsing fails.
    """
    pass


class PageProcessor:
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

    def _get_content(self):
        """
        Fetches the HTML content from the URL specified by self.link.

        Returns:
            str: The HTML content of the page if the request is successful.

        Raises:
            ParsingError: If the content could not be parsed.

        Note:
            If the protected flag is True, additional authentication handling might be required.
        """
        try:
            response = requests.get(self.link)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching content from {self.link}: {e}")
            raise ParsingError

    def html_to_md(self):
        """
        Converts HTML content to Markdown format.
        """
        pass

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