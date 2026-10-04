---
name: fetch-known-url
description: Fetch and parse a supported whitelisted URL into AI-agent-readable artifacts. Use this when the user asks to fetch, read, archive, extract, summarize, or convert a known supported URL into readable files. Supports ChatGPT and claude.ai shared conversation URLs and YouTube transcript artifacts with explicit anti-bot fallback rules; add new URL patterns only after their fetch and parse behavior has been learned.
disable-model-invocation: true
metadata:
  short-description: Fetch a supported URL into readable files
---

# Fetch Known URL

## Supported URLs

- `chatgpt.com/share/...`: fetches the raw HTML, extracts the shared conversation payload, and writes Markdown plus JSON.
- `claude.ai/share/<uuid>`: drives a headed Google Chrome to pass Cloudflare, captures the `/api/chat_snapshots/<id>` JSON, and writes Markdown plus JSON.
- `youtube.com/watch?...`, `youtu.be/...`: fetches transcript artifacts when YouTube permits access and captions are available. Read [references/youtube.md](references/youtube.md) before fetching YouTube because cloud VM IPs are commonly blocked and credential/proxy choices affect reliability and safety.

Do not add unsupported URL patterns casually. When learning a new pattern, first inspect its fetch behavior, identify the stable embedded data or clean content source, then add the parser and update this list.

## Workflow

1. Confirm the URL matches a supported pattern.
2. Use the dedicated workflow for the URL type:
   - ChatGPT shared conversation URLs: `scripts/fetch_chatgpt_share.py`.
   - claude.ai shared conversation URLs: `scripts/fetch_claude_share.py` (see Claude Share Fetch below).
   - YouTube video URLs: read [references/youtube.md](references/youtube.md), then use `scripts/fetch_youtube_transcript.py` when transcript extraction is appropriate.
3. Save outputs under a task-local directory, typically `fetched-chatgpt/`, `fetched-claude/`, or `fetched-youtube/` depending on URL type.
4. Prefer the generated Markdown for agent reading and the JSON for structured follow-up work.
5. For ChatGPT shares, keep raw HTML so future parsers can be improved without refetching.

## Claude Share Fetch

The share page HTML is an empty SPA shell, and `/api/chat_snapshots/<id>` returns a Cloudflare 403 to curl and headless browsers. The script therefore opens a visible Chrome window for a few seconds. It needs `uv`, Google Chrome, and a desktop session; it will not work on a headless VM. Chromium also crashes inside the Claude Code Seatbelt sandbox, so the fetch must run outside the sandbox.

Run:

```bash
uv run "${CLAUDE_SKILL_DIR:-${CODEX_HOME:-$HOME/.codex}/skills/fetch-known-url}/scripts/fetch_claude_share.py" \
  "https://claude.ai/share/SHARE_UUID" \
  --out-dir fetched-claude
```

Outputs:

- `claude-share-<id>.json`: raw snapshot API payload plus normalized messages
- `claude-share-<id>.md`: transcript with tool calls, tool results, and thinking collapsed in `<details>`

Re-render Markdown offline from the saved JSON with `--from-json fetched-claude/claude-share-<id>.json`. A 404 snapshot status means the share is private or deleted; a stuck "Just a moment..." page means the challenge did not pass.

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
