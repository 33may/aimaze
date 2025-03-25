from os.path import isfile
from tiktoken._educational import *
from urllib.parse import urljoin
from markdownify import markdownify as md
from requests import get
import re
from collections import defaultdict
import os
import json

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

cl100k_base = tiktoken.get_encoding("cl100k_base")


def shrink_entry(text: str) -> str:
    """Converts html to markdown, and removes excessive whitelines/spaces."""

    data = md(text)

    shrunk = re.sub(r"\n\n+", "\n\n", data)

    return re.sub(r"  +", " ", shrunk)


def get_content(url: str, auth_info=None):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get(url)

        WebDriverWait(driver, 100).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        content = driver.page_source
    finally:
        driver.quit()

    return content



URL = "https://developers.hubspot.com/docs/reference/api/marketing/emails/marketing-emails"

with open('download.md', 'w') as f:
    f.write(shrink_entry(get_content(URL)))

with open('download.md', 'r') as f:
    endpoint = f.read()


# data = defaultdict(lambda: defaultdict(list))
# if os.path.isfile('results.json'):
#     with open('results.json', 'r') as f:
#         for base_url, stats in json.load(f).items():
#             data[base_url] = defaultdict(list, stats)

base_url = urljoin(URL, "/")
n_tokens = len(cl100k_base.encode(endpoint, disallowed_special=()))
# data[base_url][URL].append(n_tokens)
print(f"Endpoint: {n_tokens} tokens")

# with open('results.json', 'w') as f:
#     json.dump(data, f, indent=4)