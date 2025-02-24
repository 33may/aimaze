from requests import get
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from urllib.parse import urljoin


def get_content(url: str, auth_info=None) -> str:
    try:
        r = get(url)

        if not r.status_code == 200:
            raise Exception(f"Couldn't access page: {url} (HTTP {r.status_code})")  # TODO: Better way to handle this than nuke button.

        return r.content
    except requests.RequestException as e:
        print(f"Error fetching content from {self.link}: {e}")
        raise ParsingError


def html_to_md(html: str) -> str:
    return md(html)    
    

def get_all_links(html: str, base_url: str) -> list[str]:
    soup = BeautifulSoup(html, 'html.parser')

    links = [a.get('href') for a in soup.find_all('a')]
    return [urljoin(base_url, l) for l in links]

