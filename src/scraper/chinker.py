
import json
import os
import re
from typing import List, Dict, Tuple

import openai

MAX_WORDS_PER_CHUNK = 2_000
MODEL_NAME = "gpt-4o"
RE_SPACE = re.compile(r"\s+")


SYSTEM_MESSAGE = {
    "role": "system",
    "content": (
        "You segment raw API documentation.\n"
        "For the chunk provided by the user, return JSON ONLY in the form:\n"
        "{\n"
        '  "endpoints": [\n'
        "    {\"title\": <string>, \"last_line\": <string>}, ...\n"
        "  ]\n"
        "}\n"
        "Rules:\n"
        "• List ONLY sections that are fully contained within this chunk.\n"
        "• `last_line` must be the EXACT final line of that section,\n"
        "  copied verbatim from the chunk.\n"
        "• Do NOT add, rewrite or omit characters inside `last_line`.\n"
        "• If the last section is cut off mid-way, omit it from the list."
    ),
}

JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "endpoints": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "last_line": {"type": "string"},
                },
                "required": ["title", "last_line"],
            },
        }
    },
    "required": ["endpoints"],
}


def _build_messages(chunk: str) -> List[Dict[str, str]]:
    """Return messages list for the chat endpoint."""
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
    rsp = openai.chat.completions.create(
        model=MODEL_NAME,
        messages=_build_messages(chunk),
        response_format={"type": "json_schema", "schema": JSON_SCHEMA},
        temperature=0,
    )
    return json.loads(rsp.choices[0].message.content)


def _find_line_end_positions(chunk: str, lines: List[str]) -> List[int]:
    """Return end-indices (exclusive) of each `last_line` inside chunk, in order.

    Raises ValueError if a marker is not found.
    """
    indices = []
    search_from = 0
    for marker in lines:
        pos = chunk.find(marker, search_from)
        if pos == -1:
            raise ValueError(f"Marker line not found: {marker!r}")
        end = pos + len(marker)
        indices.append(end)
        search_from = end
    return indices


def split_api_doc(md_text: str, max_words: int = MAX_WORDS_PER_CHUNK) -> List[Dict]:
    """
    Parameters
    ----------
    md_text : str
        Whole Markdown page.
    max_words : int
        Chunk size (soft limit, default 2 000 words).

    Returns
    -------
    List[Dict]  –  [{"title": <str>, "content": <str>}, ...]
    """
    endpoints: List[Dict] = []

    pos = 0
    carry = ""  # fragment from previous round

    while pos < len(md_text):
        raw_chunk, next_pos_guess = _slice_by_words(md_text, pos, max_words)
        chunk = carry + raw_chunk

        data = _openai_call(chunk)
        names = [ep["title"] for ep in data["endpoints"]]
        markers = [ep["last_line"] for ep in data["endpoints"]]

        if not markers:
            # Nothing complete in this chunk: move window forward
            pos = next_pos_guess
            carry = ""
            continue

        # Locate marker positions and split
        ends = _find_line_end_positions(chunk, markers)
        start_idx = 0
        for title, end_idx in zip(names, ends):
            content = chunk[start_idx:end_idx]
            endpoints.append({"title": title, "content": content})
            start_idx = end_idx

        # Everything after the last full section becomes new carry
        carry = chunk[start_idx:]
        # Advance absolute position by amount of raw text we have consumed
        # (excluding previous carry)
        consumed = len(raw_chunk) - max(0, len(carry) - len(raw_chunk))
        pos += consumed

    return endpoints

