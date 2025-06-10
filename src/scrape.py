from requests import get, RequestException
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from markdownify import markdownify as md
from urllib.parse import urljoin

from time import sleep
from tqdm import tqdm


failed = 0


def bfs_site(starting_url: str, domain_url="/", auth_info=None, slowdown_s: float = 0.05) -> dict[str, str]:
    "Returns all pages found on the given site labeled by URL."

    pages = {}
    links = {starting_url}  # Sets so duplicates get filtered automatically.
    failed = 0

    base_url = urljoin(starting_url, domain_url)
    segment = domain_url.replace(urljoin(domain_url, "/"), "")

    bar = tqdm(
        total=None,
        desc=f"{segment or '/'} crawl ",
        unit=" page",
        leave=False,
    )

    while links:
        link = links.pop()
        # print("Processing", link)

        # print(f"{segment}: {len(pages)} pages processed, {len(links)} in queue ({failed} failed).     ", end="\r")
        try:
            html = get_content_no_sel(link, auth_info)
        except Exception:
            failed += 1
            bar.set_postfix(in_queue=len(links), failed=failed)
            sleep(slowdown_s)
            continue

        pages[link] = md(html)

        # Add new links which aren't already processed.
        links |= get_all_links(html, base_url) - set(pages)

        bar.update(1)
        bar.set_postfix(in_queue=len(links), failed=failed)

        sleep(slowdown_s)  # So we don't accidentaly DoS the docs.

    bar.close()
    print(f"Finished scraping {segment or '/'}: "
          f"{len(pages)} successful, {failed} failed.")

    return pages


def get_content(url: str, auth_info=None):
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver import Chrome

    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

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


def get_content_no_sel(url: str, auth_info=None) -> str:
    # Still can't get selenium working with Nix...
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
