import requests
from bs4 import BeautifulSoup
from  urllib.parse import urlparse


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
        self.link_base = f"{parsed_url.scheme}://{parsed_url.netloc}"

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
            list: A list of URLs extracted from <a> tags in the HTML content.
        """
        html = self.content
        if html is None:
            return []
        soup = BeautifulSoup(html, 'html.parser')

        links = [a['href'] if "https://" in a["href"] else self.link_base + a["href"] for a in soup.find_all('a', href=True)]

        internal_links = [link for link in links if self.link_base in link]

        external_links = [link for link in links if self.link_base not in link]

        return internal_links, external_links