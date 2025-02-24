from requests import get, RequestException
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from markdownify import markdownify as md
from urllib.parse import urljoin

from time import sleep

class ParsingError(Exception):
    """
    Custom exception raised when content parsing fails.
    """
    pass


def bfs_site(starting_url: str, auth_info=None, slowdown_s: float = 0.05) -> dict[str, str]:
    "Returns all pages found on the given site labeled by URL."
    
    pages = dict()
    links = {starting_url}  # Sets so duplicates get filtered automatically.
    
    base_url = urljoin(starting_url, "/")

    while links:
        link = links.pop()
        
        if link in pages:
            continue  # Filtering bandaid.

        print("Processing", link)

        html = get_content(link, auth_info)
        if not html:
            continue  # Skipping failed pages (find better way to handle this).

        pages[link] = html_to_md(html)

        # Add new links which aren't already processed.
        links |= get_all_links(html, base_url) ^ set(pages.keys())

        sleep(slowdown_s)  # So we don't accidentaly DoS the docs.
    return pages

def get_content(url: str, auth_info=None) -> str:
    try:
        r = get(url)

        if not r.status_code == 200:
            print(f"Couldn't access page: {url} (HTTP {r.status_code})")  
            
            return ""

        return r.content
    except RequestException as e:
        print(f"Error fetching content from {self.link}: {e}")
        # raise ParsingError

def html_to_md(html: str) -> str:
    return md(html)

def get_all_links(html: str, base_url: str, internal_only=True) -> set[str]:
    soup = BeautifulSoup(html, 'html.parser')

    # '/page/1#Header-2' -> 'https://full-url.com/page/1' (and doesn't fuck up on already full URLs.)
    links = {urljoin(base_url, a.get('href')).split('#')[0] for a in soup.find_all('a')}

    return {l for l in links if l.startswith(base_url)} if internal_only else links

