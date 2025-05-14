
import json
import os
import re
from typing import List, Dict, Tuple

import openai
from openai import OpenAI

client = OpenAI()

MAX_WORDS_PER_CHUNK = 2000
MODEL_NAME = "gpt-4o"


SYSTEM_MESSAGE = {
    "role": "system",
    "content": (
        "You segment raw API documentation.\n"
        "For the chunk provided by the user, return JSON ONLY in the form:\n"
        "{\n"
        '  "endpoints": [\n'
        "    {\"title\": <string>, \"last_line\": <string>, \"type\": <string>}, ...\n"
        "  ]\n"
        "}\n"
        "Rules:\n"
        " Analyze the structure of the separate endpoints and all the fields that should be inside single endpoint, to make the decision about the completeness of the last one \n"
        " The non-endpoint data should not be splited into subsections, it just need to be separated from endpoint data.\n"
        " List ONLY sections that are fully contained within this chunk.\n"
        " For the type field: Identify 'endpoint' if the section is ACTUAL endpoint that contains method, url, params and all other information that is intended to be used in the project. Identify 'general' if it provides useful general information that is needed to implement other endpoints(Auth methods, rate limits, etc). Make 'other' if this is not essential for implementing the endpoints\n"
        " If the endpoint have some sort of text introduction or details, put it in the same section as endpoint. The chunk should be fully self-contained and have full information to implement endpoint\n"
        " `last_line` must be the EXACT final line of that section with max length of 4 words,\n"
        " Do NOT add, rewrite or omit characters inside `last_line`.\n"
        " If the last section is cut off mid-way, omit it from the list."
    ),
}

JSON_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "endpoints": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "title": {"type": "string"},
                    "last_line": {"type": "string"},
                    "type": {
                        "type": "string",
                        "enum": ["endpoint", "general", "other"]
                    }
                },
                "required": ["title", "last_line", "type"]
            }
        }
    },
    "required": ["endpoints"]
}


def _build_messages(chunk: str) -> List[Dict[str, str]]:
    """Construct the message payload for a single chat completion call."""
    return [
        SYSTEM_MESSAGE,
        {
            "role": "user",
            "content": (
                "Below is a chunk of raw Markdown.\n"
                "Identify completed endpoint sections and respond with JSON only.\n\n"
                f"{chunk}"
            ),
        },
    ]


def _slice_by_words(text: str, start: int, limit: int) -> Tuple[str, int]:
    """Return (substring, next_absolute_index) containing ≤ `limit` words."""
    count, i = 0, start
    while i < len(text) and count < limit:
        if text[i].isspace() and (i == 0 or not text[i - 1].isspace()):
            count += 1
        i += 1
    return text[start:i], i


def _openai_call(chunk: str) -> Dict:
    """Send chunk to OpenAI and return parsed JSON."""
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=_build_messages(chunk),
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "PingResponse",
                "schema": JSON_SCHEMA,
                "strict": True
            }
        },
        temperature=0,
    )
    return json.loads(response.choices[0].message.content)

def split_api_page(
    md_text: str,
    max_words: int = MAX_WORDS_PER_CHUNK
) -> Tuple[List[Dict], List[Dict]]:
    """Split a Markdown API page into endpoint and general sections.

    Parameters
    ----------
    md_text : str
        The entire Markdown document.
    max_words : int, optional
        Soft limit for each chunk passed to the model (default 2 000 words).

    Returns
    -------
    Tuple[List[Dict], List[Dict]]
        *endpoints*, *general* – each list contains dictionaries of the form
        ``{"title": str, "content": str}``.
    """
    endpoints: List[Dict] = []
    general:   List[Dict] = []

    pos = 0
    carry = ""          # tail of the prev chunk
    pending: List[Dict] = []  # sections, with no "last_line"

    while pos < len(md_text):
        # 1. берём сырой кусок текста ≲ max_words слов
        raw_chunk, next_pos_guess = _slice_by_words(md_text, pos, max_words)
        prev_carry_len = len(carry)
        chunk = carry + raw_chunk

        # 2. concatenating the tail of prev chunk and calling model
        items = pending + _openai_call(chunk)["endpoints"]
        pending = []

        if not items:
            pos   = next_pos_guess
            carry = ""
            continue

        # 3. looking the "last_line of every section"
        segment_start = 0
        search_from   = 0
        segment_items: List[Dict] = []

        for idx, it in enumerate(items):
            loc = chunk.find(it["last_line"], search_from)
            if loc == -1:
                # cant find the last line identified by model -> merge with next section from chunk
                pending = items[idx:]
                carry   = chunk[segment_start:]
                break

            segment_items.append(it)
            end_idx = loc + len(it["last_line"])

            # define type of block (single or merged)
            types = [s["type"] for s in segment_items]
            if "endpoint" in types:
                target = endpoints
            elif "general" in types:
                target = general
            else:
                target = None

            if target is not None:
                content = chunk[segment_start:end_idx]
                target.append({"title": segment_items[0]["title"], "content": content})

            segment_items = []
            segment_start = end_idx
            search_from   = end_idx

        # segment_items might be empty, if last_line not found
        if segment_items and not pending:
            pending = segment_items
            carry   = chunk[segment_start:]

        # 4. update global pointer
        unconsumed_from_raw = max(0, len(carry) - prev_carry_len)
        pos += len(raw_chunk) - unconsumed_from_raw

    return endpoints, general



# ===== TEST ===============================

with open(file="./source_html/test.md") as f:
    md_content = f.read()

split_api_page(md_content)

