def extract_code(response: str) -> str:
    if  '```python' not in response:
        return ""

    response = response[response.index('```python')+len('```python'):]

    if "```" not in response:
        return ""

    print(response)

    return response[:response.index('```')]
