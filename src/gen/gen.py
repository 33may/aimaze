from openai import OpenAI
from math import ceil

import json
from gen.transpiler import wrap_api
from gen.chunker import chunk_page

from schemas import OPENAI_SCHEMA
import tiktoken
MODEL = "gpt-4o"
ENCODER = tiktoken.encoding_for_model(MODEL)

 
# Explain general_info in schema for auth more in prompt.
SCHEMA_EXTRACTION_PROMPT = """
The markdown section below is part of an API documentation, containing endpoints with their input/output schema's. Convert every endpoint as listed in the documentation into json schema's as instructed below. 

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
    schemas = {"endpoints": []}
    total = len(pages)
    processed = 0

    while pages:
        chunk = {}
        key = None
        space_left = CONTEXT_SIZE

        while pages:  # This second chunker grabs as many chunks (as prepped before as it can fit into 1 call/ctx window)
            key = list(pages)[0]
            page = pages[key]
            page_size = len(ENCODER.encode(page))

            if page_size > space_left:
                if page_size > CONTEXT_SIZE:  # Here we split a single page into multiple chunks.
                    page = pages.pop(key)
                    print(f"{processed}/{total} endpoints converted to code. Encountered large page, chunking into ~{ceil(page_size / CONTEXT_SIZE)}.", end="\r")

                    pages.update({f"{key}-#{i}": page_chunk for i, page_chunk in 
                        enumerate(chunk_page(client, 
                                             MODEL,
                                             page,
                                             CONTEXT_SIZE))
                    })
                    continue
                break

            chunk[key] = pages.pop(key)
            space_left -= page_size

        
        print(f"{processed}/{total} endpoints converted to code. Chunked {len(chunk)} pages.{CLEARLINE}", end="\r")
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

        schema = json.loads(chat_completion.choices[0].message.content)
        schemas["endpoints"].extend(schema["endpoints"])
        processed += len(chunk)
        print(f"{processed}/{total} endpoints converted to code.{CLEARLINE*2}", end="\r")

    return schemas

def generate_code(schema: dict, base_url: str, api_name: str, output_file_loc: str):
    with open(output_file_loc, "w") as f:
        f.write(wrap_api(schema, base_url, api_name))

# if __name__ == "__main__":
#     URL = "https://docs.github.com/en/rest/actions/artifacts?apiVersion=2022-11-28"
