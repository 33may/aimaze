from os.path import isfile
from tiktoken._educational import *
from urllib.parse import urljoin
from markdownify import markdownify as md
from requests import get
import re
from collections import defaultdict
import json


from scraper import bfs_site

cl100k_base = tiktoken.get_encoding("cl100k_base")


WEBSITES_STATIC = [
    ("https://docs.github.com/en/rest/rate-limit/rate-limit?apiVersion=2022-11-28", "/en/rest"),
    ("https://developer.spotify.com/documentation/web-api/reference/check-if-user-follows-playlist", "/documentation/web-api"),
    ("https://woocommerce.github.io/woocommerce-rest-api-docs/", "/woocommerce-rest-api-docs"),
    ("https://developers.notion.com/reference/intro/", "/reference"),
    ("https://developers.pipedrive.com/docs/api/v1/ActivityTypes#getActivityTypes", "/docs/api/v1"),
    ("https://developer.calendly.com/api-docs/d37c7f031f339-list-activity-log-entries", "/api-docs"),
    ("https://docs.stripe.com/api/", "/api"),
    ("https://docs.webwinkelkeur.nl/", "/"),
    ("https://www.storyblok.com/docs/api/", "/docs/api"),
    ("https://developers.etrusted.com/reference/api-introduction", "/reference"),
    ("https://developers.hubspot.com/docs/reference/api/overview", "/docs/reference/api"),
    ("https://learn.microsoft.com/en-us/linkedin/", "/linkedin"),
    ("https://learn.microsoft.com/en-us/rest/api/aks/agent-pools/abort-latest-operation?view=rest-aks-2025-01-01&tabs=HTTP", "/en-us/rest/api"),
    # ("", ""),
]

WEBSITES_DYNAMIC = [
    ("https://developer.apple.com/documentation/", "/documentation"),
    ("https://shopify.dev/docs/api", "/docs/api"),
    ("https://doc.magentochina.org/swagger/#/", "/swagger"),
    ("https://demo.anewspring.com/apidocs#/", "/apidocs"),
    # ("", ""),
]

WEBSITES_WITH_OPENAPI = [
    "https://api.bol.com/retailer/public/Retailer-API/key-concepts.html",

]

MEGA_APIS = [
    "github",
    "microsoft.com/en-us/rest/api",
    "apple",
    "stripe",
    "storyblok",
    "shopify"
]

data = defaultdict(dict)

for (website, domain_url) in WEBSITES_STATIC:
    if not domain_url.endswith('/'):
        domain_url += '/'
    base_url = urljoin(website, domain_url)

    for (url, content) in bfs_site(website, domain_url).items():
        temp_base_url = base_url
        n_tokens = len(cl100k_base.encode(content, disallowed_special=()))

        # Temp base to go one folder deeper in docs for 'sub-APIs'.
        if any(x in base_url for x in MEGA_APIS):
            temp_base_url = base_url + url.replace(base_url, "").split("/")[0]

        data[temp_base_url][url] = n_tokens
        print(f"{url}: {n_tokens} tokens")

# with open('results.json', "r") as f:
    # data.update(json.load(f))

with open('results.json', 'w') as f:
    json.dump(data, f, indent=4)
