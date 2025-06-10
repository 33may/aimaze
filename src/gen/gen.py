from pprint import pprint
from urllib.parse import urljoin
from openai import OpenAI
from math import ceil

import json
from gen.transpiler import wrap_api
from gen.chunker import chunk_page

from copy import deepcopy

from schemas import OPENAI_SCHEMA_FILTER, OPENAI_SCHEMA_PARSE
import tiktoken
MODEL = "gpt-4.1-nano"
ENCODER = tiktoken.encoding_for_model("gpt-4o")

 
# Explain general_info in schema for auth more in prompt.
SCHEMA_EXTRACTION_PROMPT = """
The markdown section below is part of an API documentation, containing endpoints with their input/output schema's. Convert every endpoint as listed in the documentation into json schema's as instructed below. 

Here is the page you need to parse:
```markdown
{docs}
```
"""

GEN_INFO_FILTER_PROMPT = """
You are part of an agentic system that extracts API information from their documentation. The end result is transpiled into python for developers to easily access the API. At the previous step an LLM extracted endpoint information and general information for each chunk in the documenation. These calls were separate from each other so the general info section likely contains duplicate fields. Please analyze the inferred general info from these calls and return a single dictionary containing only 1 instance of each unique item. For the explanation fields of duplicate items: inspect all explanations for the field and create a new description can encapsulates all insights.

Do this only for variables you encounter that make sense within a singleton config for the API code. For instance, API keys should be kept, but request specific id's shouldn't (that should be in the endpoint specific code).


Here are the general info instances:
```json
{infos}
```
"""

CONTEXT_SIZE = 28_000 - len(ENCODER.encode(SCHEMA_EXTRACTION_PROMPT))

import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("API_KEY"))

# After loop prints on same lines these so we wipe longer text previously on line.
CLEARLINE = "                      "

def filter_gen_info(info: list[dict]) -> dict:
    chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": GEN_INFO_FILTER_PROMPT.format(infos=str(info))
                }
            ],
            model=MODEL,
            response_format=OPENAI_SCHEMA_FILTER
        )

    try:
        merged = json.loads(chat_completion.choices[0].message.content)["general_info"]
    except: 
        with open("test/crash.py", "w") as f:
            f.write(chat_completion.choices[0].message.content)
        print(f"\n\nCrashed on gen :( tail: {chat_completion.choices[0].message.content[-200:]}\n\n")
        exit()

    return merged


def extract_schemas(pages: dict[str, str]) -> dict:
    print("Checking pages for need of chunking...")
    for url, page in deepcopy(pages).items():  # Individual page chunker.
        page_size = len(ENCODER.encode(page))
        if page_size > CONTEXT_SIZE:
            print(f"Chunking '{url.replace(urljoin(url, "/"), "")}' into ~{ceil(page_size / CONTEXT_SIZE)} chunks.", end="\r")
            pages.pop(url)
            pages.update({f"{url}-#{i}": chunk for i, chunk in 
                enumerate(chunk_page(client, 
                                     MODEL,
                                     page,
                                     CONTEXT_SIZE - 1000))
            })

    schemas = {"endpoints": [], "general_info": []}
    total = len(pages)
    processed = 0

    print("Page chunking done, extracting schemas.")
    while pages:
        chunk = {}
        key = None
        space_left = CONTEXT_SIZE

        while pages:  # This second chunker grabs as many chunks (as prepped before as it can fit into 1 call/ctx window)
            key = list(pages)[0]
            page = pages[key]
            page_size = len(ENCODER.encode(page))

            if page_size > space_left:
                break

            chunk[key] = pages.pop(key)
            space_left -= page_size

        print(f"{processed}/{total} pages processed. Currently handling {len(chunk)} pages.{CLEARLINE}", end="\r")
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": SCHEMA_EXTRACTION_PROMPT.format(docs=str(chunk))
                }
            ],
            model=MODEL,
            response_format=OPENAI_SCHEMA_PARSE
        )

        try:
            schema = json.loads(chat_completion.choices[0].message.content)
        except: 
            with open("test/crash.py", "w") as f:
                f.write(chat_completion.choices[0].message.content)
            print(f"\n\nCrashed on endpoints :( tail: {chat_completion.choices[0].message.content[-200:]}\n\n")
            exit()
        schemas["endpoints"].extend(schema["endpoints"])
        schemas["general_info"].extend(schema["general_info"])

        processed += len(chunk)
        print(f"{processed}/{total} pages processed.{CLEARLINE*2}", end="\r")

    schemas["general_info"] = filter_gen_info(schemas["general_info"])
    with open("tmp.json", 'w') as f:
        json.dump(schemas, f, indent=4)

    return schemas

def generate_code(schema: dict, base_url: str, api_name: str, output_file_loc: str):
    with open(output_file_loc, "w") as f:
        f.write(wrap_api(schema, base_url, api_name))

# if __name__ == "__main__":
#     URL = "https://docs.github.com/en/rest/actions/artifacts?apiVersion=2022-11-28"
