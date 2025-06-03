from markdownify import markdownify
import json

from openai import OpenAI
import tiktoken

DEFAULT_NEIGHBOURHOOD_TOKENS = 2500


def _count_tokens(encoder: tiktoken.Encoding, text: str) -> int:
    """Return the number of tokens `text` would occupy for the chosen model."""
    return len(encoder.encode(text))


def enumerate_lines(text: str) -> str:
    """Prefix every line with a 1‑based line number padded to 5 digits."""
    lines = text.splitlines()
    return "\n".join(f"{idx}: {line}" for idx, line in enumerate(lines, start=1))


def _build_split_messages(numbered_chunk: str) -> list[dict[str, str]]:
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


def _openai_split_call(client: OpenAI, model_name: str, numbered_chunk: str) -> int:
    """Query the model for a safe split line and return it as an integer."""
    res = client.chat.completions.create(
        model=model_name,
        messages=_build_split_messages(numbered_chunk),
        response_format={"type": "json_object"},
        temperature=0,
    )
    return int(json.loads(res.choices[0].message.content)["split_line"])


def chunk_page(
    client: OpenAI,
    model_name: str,
    page_md: str,
    chunk_tokens: int,
    context_tokens: int = DEFAULT_NEIGHBOURHOOD_TOKENS,
) -> list[str]:
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
    encoder = tiktoken.encoding_for_model("gpt-4o")
    chunk_tokens -= context_tokens  # So we're sure not to include and go over actual context window.

    raw_lines = page_md.splitlines()
    total_lines = len(raw_lines)
    # print("Starting chunk_page: total_lines={}", total_lines)

    chunks: list[str] = []
    cursor = 0  # first unprocessed line index

    while cursor < total_lines:
        # Build forward window
        token_fw = 0
        hard_end = cursor
        while hard_end < total_lines and token_fw < chunk_tokens:
            token_fw += _count_tokens(encoder, raw_lines[hard_end])
            hard_end += 1
        # print(f"Hard window: cursor={cursor} -> hard_end={hard_end} ({token_fw} tokens)")

        # EOF reached inside hard window → dump rest
        if hard_end >= total_lines:
            # print("EOF hit inside hard window; emitting final chunk")
            chunks.append("\n".join(raw_lines[cursor:]))
            break

        # Build backward context
        token_bw = 0
        back_start = hard_end
        while back_start > 0 and token_bw < context_tokens:
            back_start -= 1
            token_bw += _count_tokens(encoder, raw_lines[back_start])

        # Build forward context
        token_ctx_fw = 0
        soft_end = hard_end
        while soft_end < total_lines and token_ctx_fw < context_tokens:
            token_ctx_fw += _count_tokens(encoder, raw_lines[soft_end])
            soft_end += 1
        # print(f"Context: back_start={back_start} soft_end={soft_end}")

        # Forward context hits EOF → dump rest
        if soft_end >= total_lines:
            # print("EOF hit while filling forward context; emitting final chunk")
            chunks.append("\n".join(raw_lines[cursor:]))
            break

        # Query model for split point
        numbered_block = enumerate_lines("\n".join(raw_lines[back_start:soft_end]))
        split_line_local = _openai_split_call(client, model_name, numbered_block)
        split_line_global = back_start + split_line_local
        assert cursor < split_line_global <= soft_end, "Invalid split line returned"
        # print(f"Accepted split_line_global={split_line_global}")

        # Emit chunk and advance cursor
        chunks.append("\n".join(raw_lines[cursor:split_line_global]))
        cursor = split_line_global

    # print(f"chunk_page finished: {len(chunks)} chunks produced")
    return chunks



if __name__ == "__main__":
    with open("./source_html/woocommerce.html", encoding="utf-8") as f:
        html = f.read()
        md_content = markdownify(html)
    pieces = chunk_page(md_content)
    print(f"Created {len(pieces)}")


