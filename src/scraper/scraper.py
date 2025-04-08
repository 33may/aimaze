from requests import get, RequestException
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from markdownify import markdownify as md
from urllib.parse import urljoin
import re

from time import sleep

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver import Chrome

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def _shrink_entry(text: str) -> str:
    """Converts html email to markdown, and removes excessive whitelines/spaces."""
    shrunk = re.sub(r"\n\n+", "\n", md(text))

    return re.sub(r"  +", " ", shrunk)


def bfs_site(starting_url: str, filter_fn, domain_url= "/", auth_info=None, slowdown_s: float = 0.01) -> dict[str, str]:
    """
    Returns all pages found on the given site labeled by URL.
    domain_url speficies our 'root', because just '/' to determine internal links will lead to nightmares processing github.com/documentation.
    """

    pages = dict()
    links = {starting_url}  # Sets so duplicates get filtered automatically.

    base_url = urljoin(starting_url, domain_url)

    while links:
        print(f"Processing {len(links)} links...")
        link = links.pop()
        print("Processing", link)

        html = get_content(link, auth_info)

        cleaned_html = _shrink_entry(html)

        if filter_fn(cleaned_html):
            pages[link] = html

        # Add new links which aren't already processed.
        links |= _get_all_links(html, base_url) - set(pages)

        sleep(slowdown_s)  # So we don't accidentaly DoS the docs.

    return {
        "name": base_url,
        "base_url": base_url,
        "endpoint_pages": pages,
    }


# def get_content(url: str, auth_info=None) -> str:
#     try:
#         r = get(url)
#
#         if not r.status_code == 200:
#             print(f"Couldn't access page: {url} (HTTP {r.status_code})")
#             return ""
#
#         return r.content
#     except RequestException as e:
#         print(f"Couldn't access page: {url}, {e}")
#
#         return ""

def get_content(url: str, auth_info=None):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")


    service = Service(ChromeDriverManager().install())
    driver = Chrome(service=service, options=chrome_options)

    try:
        driver.get(url)

        WebDriverWait(driver, 100).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        content = driver.page_source
    finally:
        driver.quit()

    return content


def _get_all_links(html: str, base_url: str) -> set[str]:
    soup = BeautifulSoup(html, 'html.parser')

    # '/page/1#Header-2' -> 'https://full-url.com/page/1' (and doesn't fuck up on already full URLs.)
    links = {urljoin(base_url, a.get('href')).split('#')[0] for a in soup.find_all('a')}

    return {l for l in links if l.startswith(base_url)}

if __name__ == "__main__":
    a = get_content("https://developers.asana.com/reference/getusers")

    with open("asana.html", "w", encoding="utf-8") as f:
        f.write(a)

    print(a)