from requests import get, RequestException
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from markdownify import markdownify as md
from urllib.parse import urljoin

from time import sleep


failed = 0


def bfs_site(starting_url: str, domain_url="/", auth_info=None, slowdown_s: float = 0.05) -> dict[str, str]:
    "Returns all pages found on the given site labeled by URL."

    pages = {}
    links = {starting_url}  # Sets so duplicates get filtered automatically.

    base_url = urljoin(starting_url, domain_url)
    segment = domain_url.replace(urljoin(domain_url, "/"), "")

    while links:
        link = links.pop()
        # print("Processing", link)

        print(f"{segment}: {len(pages)} pages processed, {len(links)} in queue ({failed} failed).", end="\r")
        html = get_content(link, auth_info)
        pages[link] = md(html)

        # Add new links which aren't already processed.
        links |= get_all_links(html, base_url) - set(pages)

        sleep(slowdown_s)  # So we don't accidentaly DoS the docs.
    
    print(f"Finished scraping {segment} ({len(pages)} successful, {failed} failed).")

    return pages


def get_content(url: str, auth_info=None) -> str:
    global failed

    try:
        r = get(url)

        if not r.status_code == 200:
            # print(f"Couldn't access page: {url} (HTTP {r.status_code})")
            failed += 1

            return ""

        return r.content
    except RequestException as e:
        # print(f"Couldn't access page: {url}, {e}")
        failed += 1

        return ""


def get_all_links(html: str, base_url: str) -> set[str]:
    soup = BeautifulSoup(html, 'html.parser')

    # '/page/1#Header-2' -> 'https://full-url.com/page/1' (and doesn't fuck up on already full URLs.)
    links = {urljoin(base_url, a.get('href')).split('#')[0] for a in soup.find_all('a')}

    return {l for l in links if l.startswith(base_url)}
