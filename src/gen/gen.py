from urllib.parse import urljoin
from openai import OpenAI
from math import ceil

import json
from gen.transpiler import wrap_api
from gen.chunker import chunk_page

from copy import deepcopy

from schemas import OPENAI_SCHEMA
import tiktoken
# MODEL = "gpt-4.1-nano"
MODEL = "gpt-4o-2024-08-06"
ENCODER = tiktoken.encoding_for_model("gpt-4o")

 
# Explain general_info in schema for auth more in prompt.
SCHEMA_EXTRACTION_PROMPT = """
The markdown section below is part of an API documentation, containing endpoints with their input/output schema's. Convert every endpoint as listed in the documentation into json schema's as instructed below, in the description of every field cover all the information required to use it. If the field is type string and have list of possible values then mention that in description. 

Here is the page you need to parse:
```markdown
{docs}
```
"""

CONTEXT_SIZE = 28_000 - len(ENCODER.encode(SCHEMA_EXTRACTION_PROMPT))

import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("API_KEY"))

# After loop prints on same lines these so we wipe longer text previously on line.
CLEARLINE = "                      "

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
                                     CONTEXT_SIZE - 10000))
            })

    schemas = {"endpoints": []}
    total = len(pages)
    processed = 0

    print("Page chunking done, extracting schemas.")
    while pages:
        chunk = {}
        key = None
        space_left = CONTEXT_SIZE

        while pages:  # This second chunker grabs as many chunks (as prepped before as it can fit into 1 call/ctx window)
            # //TODO fix token per minut 429
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
            response_format=OPENAI_SCHEMA
        )

        try:
            schema = json.loads(chat_completion.choices[0].message.content)
        except: 
            print(schema)
            exit()
        schemas["endpoints"].extend(schema["endpoints"])
        processed += len(chunk)
        print(f"{processed}/{total} pages processed.{CLEARLINE*2}", end="\r")

    with open("tmp.json", 'w') as f:
        json.dump(schemas, f, indent=4)

    return schemas

def generate_code(schema: dict, base_url: str, api_name: str, output_file_loc: str):
    with open(output_file_loc, "w") as f:
        f.write(wrap_api(schema, base_url, api_name))
