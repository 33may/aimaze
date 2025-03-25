from os.path import isfile
from tiktoken._educational import *
from urllib.parse import urljoin
from markdownify import markdownify as md
from requests import get
import re
from collections import defaultdict
import os
import json


cl100k_base = tiktoken.get_encoding("cl100k_base")


def shrink_entry(text: str) -> str:
    """Converts html to markdown, and removes excessive whitelines/spaces."""
    shrunk = re.sub(r"\n+", r"\n", md(text))

    return re.sub(r"  +", " ", shrunk)


def get_content(url: str, auth_info=None) -> str:
    r = get(url)

    if not r.status_code == 200:
        raise Exception(f"Couldn't access page: {url} (HTTP {r.status_code})")

    return str(r.content)


SPLITTER = "#-#endpoint"

data = defaultdict(lambda: defaultdict(list))
if os.path.isfile('results.json'):
    with open('results.json', 'r') as f:
        for base_url, stats in json.load(f).items():
            data[base_url] = defaultdict(list, stats)

while True:
    url = input("Enter URL: ")

    with open('download.md', 'w') as f:
        if url.startswith("https://developer.spotify.com/"):
            f.write(shrink_entry(get_content(url)).split("Request")[1])
        elif url.startswith("https://developers.pipedrive.com/"):
            endpoints_only = (shrink_entry(get_content(url)
                                           .replace("\\n#### ", f"\\n{SPLITTER}\n#### ")
                                           .split("### Subscribe to Pipedrive’s")[0]
                                           .split(SPLITTER)[1:]))

            f.write(SPLITTER.join(endpoints_only))
        else:
            f.write(shrink_entry(get_content(url)))

            if not input(f"Place '{SPLITTER}' markers ([y]es): ").lower().startswith("y"):
                print("Quitting EDA tool")
                exit()

    while True:
        with open('download.md', 'r') as f:
            endpoints = f.read().split(SPLITTER)
        ok = input(f"Found {len(endpoints)} endpoints. Is this correct? ([y]es, [r]eload): ")

        if ok.startswith('y'):
            break
        if ok.startswith('r'):
            continue
        exit()


    base_url = urljoin(url, "/")
    for i, ep in enumerate(endpoints):
        n_tokens = len(cl100k_base.encode(ep, disallowed_special=()))
        from pprint import pprint
        data[base_url][url].append(n_tokens)
        print(f"Endpoint {i}: {n_tokens} tokens")

    with open('results.json', 'w') as f:
        json.dump(data, f, indent=4)

    print(f"Processed {url}")
