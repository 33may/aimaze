from openai import OpenAI

import json
from transpiler import wrap_api

from shared.schema import OPENAI_SCHEMA

 
# Explain general_info in schema for auth more in prompt.
SCHEMA_EXTRACTION_PROMPT = """
The markdown section below is part of an API documentation, containing endpoints with their input/output schema's. Convert every endpoint as listed in the documentation into json schema's as instructed below. 

Here is the page you need to parse:
```markdown
{docs}
```
"""


client = OpenAI(api_key="")

with open("src/test/all_types.py", "r") as f:
    types = f.read()

def extract_schemas(pages: dict[str, str]) -> dict:
    # Chunk here. Simple chop on len (count tokens and split when entry goes over ctx window)

    print("{processed}/{total} endpoints converted to code.")

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": SCHEMA_EXTRACTION_PROMPT.format(docs=str(pages))
            }
        ],
        model="gpt-4o",
        response_format=OPENAI_SCHEMA
    )

    return json.loads(chat_completion.choices[0].message.content)

def generate_code(schema: dict, base_url: str, api_name: str, output_file_loc: str):
    with open(output_file_loc, "w") as f:
        f.write(wrap_api(schema, base_url, api_name))

# if __name__ == "__main__":
#     URL = "https://docs.github.com/en/rest/actions/artifacts?apiVersion=2022-11-28"
