import re


def extract_code(response: str) -> list:
    """
    Extracts code blocks from the response, regardless of the language.
    Returns a list of extracted code snippets.
    """
    code_blocks = re.findall(r'```(?:\w+)?\n(.*?)```', response, re.DOTALL)

    return code_blocks if code_blocks else []

