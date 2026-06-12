---
name: fetching-websites
description: Fetch and parse whitelisted website URLs into AI-agent-readable artifacts. Use this when the user asks to fetch, archive, extract, or convert a website into readable files. Currently supports ChatGPT shared conversation URLs on chatgpt.com; add new domains only after their fetch and parse behavior has been learned.
metadata:
  short-description: Fetch whitelisted websites into readable files
---

# Fetching Websites

Use this skill when a user asks to fetch website content and save it for other AI agents to read.

## Supported Domains

- `chatgpt.com/share/...`: fetches the raw HTML, extracts the shared conversation payload, and writes Markdown plus JSON.

Do not add unsupported domains casually. When learning a new domain, first inspect its fetch behavior, identify the stable embedded data or clean content source, then add the parser and update this list.

## Workflow

1. Confirm the URL is on the whitelist.
2. Use `scripts/fetch_chatgpt_share.py` for ChatGPT shared conversation URLs.
3. Save outputs under a task-local directory, typically `fetched-chatgpt/`.
4. Prefer the generated Markdown for agent reading and the JSON for structured follow-up work.
5. Keep raw HTML when possible so future parsers can be improved without refetching.

## ChatGPT Share Fetch

Run:

```bash
python3 "${CLAUDE_SKILL_DIR:-${CODEX_HOME:-$HOME/.codex}/skills/fetching-websites}/scripts/fetch_chatgpt_share.py" \
  "https://chatgpt.com/share/SHARE_ID" \
  --out-dir fetched-chatgpt
```

Outputs:

- `chatgpt-share-<id>.html`: raw fetched HTML
- `chatgpt-share-<id>.json`: structured metadata and messages
- `chatgpt-share-<id>.md`: clean transcript for AI agents

If the sandbox blocks network access, rerun the fetch command with the appropriate network approval.
