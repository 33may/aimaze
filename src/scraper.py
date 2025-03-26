from requests import get, RequestException
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from markdownify import markdownify as md
from urllib.parse import urljoin
import re

from time import sleep


def _shrink_entry(text: str) -> str:
    """Converts html email to markdown, and removes excessive whitelines/spaces."""
    shrunk = re.sub(r"\n\n+", "\n", md(text))

    return re.sub(r"  +", " ", shrunk)


def bfs_site(starting_url: str, domain_url= "/", auth_info=None, slowdown_s: float = 0.1) -> dict[str, str]:
    """
    Returns all pages found on the given site labeled by URL.
    domain_url speficies our 'root', because just '/' to determine internal links will lead to nightmares processing github.com/documentation.
    """

    pages = dict()
    links = {starting_url}  # Sets so duplicates get filtered automatically.

    base_url = urljoin(starting_url, domain_url)

    while links:
        link = links.pop()
        print("Processing", link)

        html = get_content(link, auth_info)

        pages[link] = _shrink_entry(html)

        # Add new links which aren't already processed.
        links |= _get_all_links(html, base_url) - set(pages)

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
        print(f"Couldn't access page: {url}, {e}")

        return ""


def _get_all_links(html: str, base_url: str) -> set[str]:
    soup = BeautifulSoup(html, 'html.parser')

    # '/page/1#Header-2' -> 'https://full-url.com/page/1' (and doesn't fuck up on already full URLs.)
    links = {urljoin(base_url, a.get('href')).split('#')[0] for a in soup.find_all('a')}

    return {l for l in links if l.startswith(base_url)}
