---
name: fetch-known-url
description: Fetch and parse a supported whitelisted URL into AI-agent-readable artifacts. Use this when the user asks to fetch, read, archive, extract, summarize, or convert a known supported URL into readable files. Currently supports ChatGPT shared conversation URLs on chatgpt.com; add new URL patterns only after their fetch and parse behavior has been learned.
metadata:
  short-description: Fetch a supported URL into readable files
---

# Fetch Known URL

## Supported URLs

- `chatgpt.com/share/...`: fetches the raw HTML, extracts the shared conversation payload, and writes Markdown plus JSON.

Do not add unsupported URL patterns casually. When learning a new pattern, first inspect its fetch behavior, identify the stable embedded data or clean content source, then add the parser and update this list.

## Workflow

1. Confirm the URL matches a supported pattern.
2. Use `scripts/fetch_chatgpt_share.py` for ChatGPT shared conversation URLs.
3. Save outputs under a task-local directory, typically `fetched-chatgpt/`.
4. Prefer the generated Markdown for agent reading and the JSON for structured follow-up work.
5. Keep raw HTML when possible so future parsers can be improved without refetching.

## ChatGPT Share Fetch

Run:

```bash
python3 "${CLAUDE_SKILL_DIR:-${CODEX_HOME:-$HOME/.codex}/skills/fetch-known-url}/scripts/fetch_chatgpt_share.py" \
  "https://chatgpt.com/share/SHARE_ID" \
  --out-dir fetched-chatgpt
```

Outputs:

- `chatgpt-share-<id>.html`: raw fetched HTML
- `chatgpt-share-<id>.json`: structured metadata and messages
- `chatgpt-share-<id>.md`: clean transcript for AI agents

If the structured parser fails or the transcript looks incomplete, save the HTML and run the heuristic extractor:

```bash
python3 "${CLAUDE_SKILL_DIR:-${CODEX_HOME:-$HOME/.codex}/skills/fetch-known-url}/scripts/extract_chatgpt_share_text.py" \
  fetched-chatgpt/chatgpt-share-SHARE_ID.html
```

Treat heuristic extractor output as orientation notes, not a canonical transcript. If precision matters and extraction is incomplete, say so clearly.

If the sandbox blocks network access, rerun the fetch command with the appropriate network approval.
