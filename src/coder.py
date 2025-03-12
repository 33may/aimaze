from scraper import get_content
from parser import extract_code
from markdownify import markdownify as md
from openai import OpenAI


client = OpenAI()

prompt = """

Write me a Python function that wraps the API call(s) in the markdown file. Make the function documentation minimal. Make sure to implement the wrapper as a BaseFunction using the classes and types in the attached python file (import these, don't copy them into your solution). For ease of access for you, these have all been merged into one file. But the code should call each function from the respective file (as listed in the comment of all_types.py) from shared.whatever, as an example: 'from shared.FunctionClass import BaseFunction'


Types (by file):
```python
{types}
````


The API documentation:
```markdown
{docs}
```


Respond only with your script wrapped in ```python ...```, and implement the tiniest test call I can run to verify the integrity off your script. Your script will be automatically executed as part of a testing procedure, so make sure the tests run automatically at the end of your script."""


with open("src/test/all_types.py", "r") as f:
    types = f.read()

URL = "https://jsonplaceholder.typicode.com/guide/"

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": prompt.format(types=types, docs=md(get_content(URL))),
        }
    ],
    model="gpt-4o",
)

response = chat_completion.choices[0].message.content
code = extract_code(response)

with open("src/test/out.py", "w") as f:
    f.write(code)
exec(code)
