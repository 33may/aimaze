from scraper import get_content
from parser import extract_code
from markdownify import markdownify as md
from openai import OpenAI

from shared.schema import OPENAI_SCHEMA


SCHEMA_EXTRACTION_PROMPT = """
The markdown section below is part of an API documentation, containing endpoints with their input/output schema's. Convert every endpoint as listed in the documentation into json schema's as instructed below.

Here is the page you need to parse:
```markdown
{docs}
```
"""


client = OpenAI(api_key="")

CODING_PROMPT = """

Write me a Python function that wraps the API call(s) in the json schema. Make the function documentation minimal. Make sure to implement the wrapper for each endpoint as a BaseFunction using the classes and types in the attached python file (import these, don't copy them into your solution). For ease of access for you, these have all been merged into one file. But the code should call each function from the respective file (as listed in the comment of all_types.py) from shared.whatever, as an example: 'from shared.FunctionClass import BaseFunction'


Types (by file):
```python
{types}
````


The API schema:
```json
{docs}
```


Respond only with your script wrapped in ```python ...```. In order to test the validity, you need to create one global dictionary called "SCHEMAS" containing endpoint: get_schema() pairs for each endpoint in the script. This outputted schema shoudl reconcile with the input schema."""


with open("test/all_types.py", "r") as f:
    types = f.read()

URL = "https://docs.github.com/en/rest/actions/artifacts?apiVersion=2022-11-28"
chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            # "content": CODING_PROMPT.format(types=types, docs=md(get_content(URL))),
            "content": SCHEMA_EXTRACTION_PROMPT.format(docs=md(get_content(URL))),
        }
    ],
    model="gpt-4o",
    response_format=OPENAI_SCHEMA
)


import json
from json_to_code import wrap_api

schema = json.loads(chat_completion.choices[0].message.content)

from pprint import pprint
pprint(schema)

print(wrap_api(schema))
