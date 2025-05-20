
import json
import os
import re
from typing import List, Dict, Tuple

import openai
from loguru import logger
from markdownify import markdownify
from openai import OpenAI

# ============================= V1

# client = OpenAI()
#
# WORDS_PER_CHUNK = 2000
# MODEL_NAME = "gpt-4o"
#
#
# SYSTEM_MESSAGE = {
#     "role": "system",
#     "content": (
#         "You segment raw API documentation.\n"
#         "For the chunk provided by the user, return JSON ONLY in the form:\n"
#         "{\n"
#         '  "endpoints": [\n'
#         "    {\"title\": <string>, \"last_line\": <string>, \"type\": <string>}, ...\n"
#         "  ]\n"
#         "}\n"
#         "Rules:\n"
#         " Analyze the structure of the separate endpoints and all the fields that should be inside single endpoint, to make the decision about the completeness of the last one \n"
#         " The non-endpoint data should not be splited into subsections, it just need to be separated from endpoint data.\n"
#         " List ONLY sections that are fully contained within this chunk.\n"
#         " For the type field: Identify 'endpoint' if the section is ACTUAL endpoint that contains method, url, params and all other information that is intended to be used in the project. Identify 'general' if it provides useful general information that is needed to implement other endpoints(Auth methods, rate limits, etc). Make 'other' if this is not essential for implementing the endpoints\n"
#         " If the endpoint have some sort of text introduction or details, put it in the same section as endpoint. The chunk should be fully self-contained and have full information to implement endpoint\n"
#         " `last_line` must be the EXACT final line of that section with max length of 4 words,\n"
#         " Do NOT add, rewrite or omit characters inside `last_line`.\n"
#         " If the last section is cut off mid-way, omit it from the list."
#     ),
# }
#
# JSON_SCHEMA = {
#     "type": "object",
#     "additionalProperties": False,
#     "properties": {
#         "endpoints": {
#             "type": "array",
#             "items": {
#                 "type": "object",
#                 "additionalProperties": False,
#                 "properties": {
#                     "title": {"type": "string"},
#                     "last_line": {"type": "string"},
#                     "type": {
#                         "type": "string",
#                         "enum": ["endpoint", "general", "other"]
#                     }
#                 },
#                 "required": ["title", "last_line", "type"]
#             }
#         }
#     },
#     "required": ["endpoints"]
# }
#
#
# def _build_messages(chunk: str) -> List[Dict[str, str]]:
#     """Construct the message payload for a single chat completion call."""
#     return [
#         SYSTEM_MESSAGE,
#         {
#             "role": "user",
#             "content": (
#                 "Below is a chunk of raw Markdown.\n"
#                 "Identify completed endpoint sections and respond with JSON only.\n\n"
#                 f"{chunk}"
#             ),
#         },
#     ]
#
#
# def _slice_by_words(text: str, start: int, limit: int) -> Tuple[str, int]:
#     """Return (substring, next_absolute_index) containing ≤ `limit` words."""
#     count, i = 0, start
#     while i < len(text) and count < limit:
#         if text[i].isspace() and (i == 0 or not text[i - 1].isspace()):
#             count += 1
#         i += 1
#     return text[start:i], i
#
#
# def _openai_call(chunk: str) -> Dict:
#     """Send chunk to OpenAI and return parsed JSON."""
#     response = client.chat.completions.create(
#         model=MODEL_NAME,
#         messages=_build_messages(chunk),
#         response_format={
#             "type": "json_schema",
#             "json_schema": {
#                 "name": "PingResponse",
#                 "schema": JSON_SCHEMA,
#                 "strict": True
#             }
#         },
#         temperature=0,
#     )
#     return json.loads(response.choices[0].message.content)
#
# def split_api_page(
#     md_text: str,
#     max_words: int = WORDS_PER_CHUNK
# ) -> Tuple[List[Dict], List[Dict]]:
#     """Split a Markdown API page into endpoint and general sections.
#
#     Parameters
#     ----------
#     md_text : str
#         The entire Markdown document.
#     max_words : int, optional
#         Soft limit for each chunk passed to the model (default 2 000 words).
#
#     Returns
#     -------
#     Tuple[List[Dict], List[Dict]]
#         *endpoints*, *general* – each list contains dictionaries of the form
#         ``{"title": str, "content": str}``.
#     """
#     endpoints: List[Dict] = []
#     general:   List[Dict] = []
#
#     pos = 0
#     carry = ""          # tail of the prev chunk
#     pending: List[Dict] = []  # sections, with no "last_line"
#
#     while pos < len(md_text):
#         # 1. берём сырой кусок текста <= max_words слов
#         raw_chunk, next_pos_guess = _slice_by_words(md_text, pos, max_words)
#         prev_carry_len = len(carry)
#         chunk = carry + raw_chunk
#
#         # 2. concatenating the tail of prev chunk and calling model
#         items = pending + _openai_call(chunk)["endpoints"]
#         pending = []
#
#         if not items:
#             pos   = next_pos_guess
#             carry = ""
#             continue
#
#         # 3. looking the "last_line of every section"
#         segment_start = 0
#         search_from   = 0
#         segment_items: List[Dict] = []
#
#         for idx, it in enumerate(items):
#             loc = chunk.find(it["last_line"], search_from)
#             if loc == -1:
#                 # cant find the last line identified by model -> merge with next section from chunk
#                 pending = items[idx:]
#                 carry   = chunk[segment_start:]
#                 break
#
#             segment_items.append(it)
#             end_idx = loc + len(it["last_line"])
#
#             # define type of block (single or merged)
#             types = [s["type"] for s in segment_items]
#             if "endpoint" in types:
#                 target = endpoints
#             elif "general" in types:
#                 target = general
#             else:
#                 target = None
#
#             if target is not None:
#                 content = chunk[segment_start:end_idx]
#                 target.append({"title": segment_items[0]["title"], "content": content})
#
#             segment_items = []
#             segment_start = end_idx
#             search_from   = end_idx
#
#         # segment_items might be empty, if last_line not found
#         if segment_items and not pending:
#             pending = segment_items
#             carry   = chunk[segment_start:]
#
#         # 4. update global pointer
#         unconsumed_from_raw = max(0, len(carry) - prev_carry_len)
#         pos += len(raw_chunk) - unconsumed_from_raw
#
#     return endpoints, general

# ============================= V2

import json
from typing import List, Dict

import openai
from openai import OpenAI
import tiktoken  # token counter used instead of line counts

client = OpenAI()

MODEL_NAME = "gpt-4o"

# Chunk sizing is now based on tokens rather than lines
DEFAULT_CHUNK_TOKENS = 20000
DEFAULT_NEIGHBOURHOOD_TOKENS = 5000

_encoding = tiktoken.encoding_for_model(MODEL_NAME)


def _count_tokens(text: str) -> int:
    """Return the number of tokens `text` would occupy for the chosen model."""
    return len(_encoding.encode(text))


def enumerate_lines(text: str) -> str:
    """Prefix every line with a 1‑based line number padded to 5 digits."""
    lines = text.splitlines()
    return "\n".join(f"{idx}: {line}" for idx, line in enumerate(lines, start=1))


def _build_split_messages(numbered_chunk: str) -> List[Dict[str, str]]:
    """Compose the prompt for the split‑finder model."""
    system_prompt = (
        "You split a Markdown API document into fully self‑contained ENDPOINT sections.\n"
        "A complete endpoint section typically contains:\n"
        " - the HTTP method and URL (endpoint link)\n"
        " - a short textual description\n"
        " - a Parameters/Fields table *or* bullet list\n"
        " - one or more code blocks / examples / jsons etc\n"
        "These elements BELONG TOGETHER and must *not* be treated as separate sections.\n"
        "The user provides a consecutive block of numbered lines.\n"
        "Note that the provided text is only the end of the section and the task it to decide the best place to end the whole chunk. most of the content is not provided, that means the split might be also in the start, if there is the large section, that started in provided text chunk, but is not finished within the context.\n"
        "Return JSON only in the form {\"split_line\": <int>} where <int> is the last "
        "line number (taken from the left margin) that leaves all endpoint sections above it complete."
        # "If the entire block is complete, return the last line number of the block."
    )
    return [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": (
                "Decide where to cut so that no endpoint is left incomplete below the "
                "cut line. Answer JSON ONLY.\n\n" + numbered_chunk
            ),
        },
    ]


def _openai_split_call(numbered_chunk: str) -> int:
    """Query the model for a safe split line and return it as an integer."""
    res = client.chat.completions.create(
        model=MODEL_NAME,
        messages=_build_split_messages(numbered_chunk),
        response_format={"type": "json_object"},
        temperature=0,
    )
    return int(json.loads(res.choices[0].message.content)["split_line"])


def chunk_page(
    page_md: str,
    chunk_tokens: int = DEFAULT_CHUNK_TOKENS,
    context_tokens: int = DEFAULT_NEIGHBOURHOOD_TOKENS,
) -> List[str]:
    """Split a Markdown API page into a list of complete‑endpoint chunks.

    Windowing strategy (token‑based):
      - Build a *hard* window starting at `cursor` so that its token budget is
        at most `chunk_tokens`.
      - Expand the window symmetrically: add up to `context_tokens` worth of
        tokens *before* and *after* the hard window. These extra lines are only
        context for the LLM – they are **not** included in the final chunk.
      - Ask the LLM for the last line that leaves every endpoint above it
        complete (relative to the numbered block).
      - Cut from `cursor` up to the suggested line and repeat until EOF.
    """
    raw_lines = page_md.splitlines()
    total_lines = len(raw_lines)
    logger.debug("Starting chunk_page: total_lines={}", total_lines)

    chunks: List[str] = []
    cursor = 0  # first unprocessed line index

    while cursor < total_lines:
        # Build forward window
        token_fw = 0
        hard_end = cursor
        while hard_end < total_lines and token_fw < chunk_tokens:
            token_fw += _count_tokens(raw_lines[hard_end])
            hard_end += 1
        logger.debug(f"Hard window: cursor={cursor} -> hard_end={hard_end} ({token_fw} tokens)")

        # EOF reached inside hard window → dump rest
        if hard_end >= total_lines:
            logger.debug("EOF hit inside hard window; emitting final chunk")
            chunks.append("\n".join(raw_lines[cursor:]))
            break

        # Build backward context
        token_bw = 0
        back_start = hard_end
        while back_start > 0 and token_bw < context_tokens:
            back_start -= 1
            token_bw += _count_tokens(raw_lines[back_start])

        # Build forward context
        token_ctx_fw = 0
        soft_end = hard_end
        while soft_end < total_lines and token_ctx_fw < context_tokens:
            token_ctx_fw += _count_tokens(raw_lines[soft_end])
            soft_end += 1
        logger.debug(f"Context: back_start={back_start} soft_end={soft_end}")

        # Forward context hits EOF → dump rest
        if soft_end >= total_lines:
            logger.debug("EOF hit while filling forward context; emitting final chunk")
            chunks.append("\n".join(raw_lines[cursor:]))
            break

        # Query model for split point
        numbered_block = enumerate_lines("\n".join(raw_lines[back_start:soft_end]))
        split_line_local = _openai_split_call(numbered_block)
        split_line_global = back_start + split_line_local
        assert cursor < split_line_global <= soft_end, "Invalid split line returned"
        logger.debug(f"Accepted split_line_global={split_line_global}")

        # Emit chunk and advance cursor
        chunks.append("\n".join(raw_lines[cursor:split_line_global]))
        cursor = split_line_global

    logger.debug(f"chunk_page finished: {len(chunks)} chunks produced")
    return chunks



if __name__ == "__main__":
    with open("./source_html/woocommerce.html", encoding="utf-8") as f:
        html = f.read()
        md_content = markdownify(html)
    pieces = chunk_page(md_content)
    print(f"Created {len(pieces)}")


