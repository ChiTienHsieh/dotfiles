#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["playwright"]
# ///
"""Fetch a claude.ai shared conversation and export Markdown/JSON artifacts.

The share page HTML is an empty SPA shell; the conversation comes from
/api/chat_snapshots/<id>, which Cloudflare guards with a JS challenge. Plain
HTTP clients and headless browsers get a 403, so this drives a real, headed
Google Chrome via Playwright and captures the snapshot response the page
itself requests.

Runtime example:
  uv run fetch_claude_share.py URL --out-dir fetched-claude

Re-render a previously saved snapshot without network access:
  python3 fetch_claude_share.py --from-json fetched-claude/claude-share-<id>.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

SNAPSHOT_PATH = "/api/chat_snapshots/"


def validate_claude_share_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("Only http/https URLs are supported")
    if parsed.netloc != "claude.ai":
        raise ValueError("Only claude.ai is currently whitelisted")
    match = re.match(r"^/share/([0-9a-fA-F-]{36})/?$", parsed.path)
    if not match:
        raise ValueError("Only claude.ai/share/<uuid> URLs are supported")
    return match.group(1)


def fetch_snapshot(url: str, share_id: str, channel: str, headless: bool, timeout_s: int) -> dict[str, Any]:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise RuntimeError("playwright is not installed; run this script with `uv run`") from exc

    captured: dict[str, Any] = {}

    def on_response(response: Any) -> None:
        # The challenge flow reloads the page, so the body must be read in the
        # handler before the next navigation discards it.
        if f"{SNAPSHOT_PATH}{share_id}" not in response.url or "body" in captured:
            return
        captured["last_status"] = response.status
        if response.status == 200:
            captured["body"] = response.body()

    with sync_playwright() as p:
        browser = p.chromium.launch(
            channel=channel or None,
            headless=headless,
            args=["--disable-blink-features=AutomationControlled"],
        )
        try:
            page = browser.new_page()
            page.on("response", on_response)
            page.goto(url, wait_until="domcontentloaded")
            for _ in range(timeout_s * 2):
                if "body" in captured:
                    break
                page.wait_for_timeout(500)
            final_url, title = page.url, page.title()
        finally:
            browser.close()

    if "body" not in captured:
        raise RuntimeError(
            "Did not receive the snapshot JSON "
            f"(last snapshot status: {captured.get('last_status')}, page: {title!r} at {final_url}). "
            "A 'Just a moment...' title means the Cloudflare challenge did not pass; "
            "a 404 status means the share is private or deleted."
        )
    return json.loads(captured["body"])


def render_tool_result(block: dict[str, Any]) -> str:
    parts: list[str] = []
    for item in block.get("content") or []:
        kind = item.get("type")
        if kind == "text":
            parts.append(item.get("text", ""))
        elif kind == "knowledge":
            parts.append(f"- [{item.get('title', '')}]({item.get('url', '')})")
        else:
            parts.append("```json\n" + json.dumps(item, ensure_ascii=False, indent=2) + "\n```")
    return "\n".join(p for p in parts if p).strip()


def render_block(block: dict[str, Any]) -> str:
    kind = block.get("type")
    if kind == "text":
        return block.get("text", "").strip()
    if kind == "thinking":
        return f"<details><summary>Thinking</summary>\n\n{block.get('thinking', '').strip()}\n\n</details>"
    if kind == "tool_use":
        payload = json.dumps(block.get("input"), ensure_ascii=False, indent=2)
        return f"<details><summary>Tool call: {block.get('name')}</summary>\n\n```json\n{payload}\n```\n\n</details>"
    if kind == "tool_result":
        body = render_tool_result(block)
        if not body:
            return ""
        error = " (error)" if block.get("is_error") else ""
        return f"<details><summary>Tool result: {block.get('name')}{error}</summary>\n\n{body}\n\n</details>"
    payload = json.dumps(block, ensure_ascii=False, indent=2)
    return f"<details><summary>Unrecognized block: {kind}</summary>\n\n```json\n{payload}\n```\n\n</details>"


def normalize_messages(snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    messages = []
    for message in sorted(snapshot.get("chat_messages") or [], key=lambda m: m.get("index", 0)):
        blocks = message.get("content") or []
        if not blocks and message.get("text"):
            blocks = [{"type": "text", "text": message["text"]}]
        messages.append(
            {
                "role": message.get("sender"),
                "created_at": message.get("created_at"),
                "text": "\n\n".join(b.get("text", "") for b in blocks if b.get("type") == "text").strip(),
                "attachments": [a.get("file_name") for a in message.get("attachments") or []]
                + [f.get("file_name") for f in message.get("files") or []],
                "blocks": blocks,
            }
        )
    return messages


def to_markdown(meta: dict[str, Any], messages: list[dict[str, Any]]) -> str:
    lines = [
        f"# {meta['title'] or 'Claude shared conversation'}",
        "",
        f"- Source: {meta['source_url']}",
        f"- Shared by: {meta['creator'] or 'unknown'}",
        f"- Snapshot created: {meta['created_at']}",
        f"- Fetched: {meta['fetched_at']}",
        f"- Messages: {len(messages)}",
        "",
    ]
    for message in messages:
        heading = "User" if message["role"] == "human" else "Claude"
        lines += ["---", "", f"## {heading}", ""]
        if message["attachments"]:
            lines += ["Attachments: " + ", ".join(filter(None, message["attachments"])), ""]
        for block in message["blocks"]:
            rendered = render_block(block)
            if rendered:
                lines += [rendered, ""]
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("url", nargs="?", help="https://claude.ai/share/<uuid>")
    parser.add_argument("--out-dir", default="fetched-claude", type=Path)
    parser.add_argument("--from-json", type=Path, help="re-render a saved claude-share-<id>.json instead of fetching")
    parser.add_argument("--channel", default="chrome", help="Playwright browser channel; '' uses bundled Chromium")
    parser.add_argument("--headless", action="store_true", help="usually blocked by Cloudflare; headed is the default")
    parser.add_argument("--timeout", type=int, default=45, help="seconds to wait for the snapshot response")
    args = parser.parse_args()

    if args.from_json:
        saved = json.loads(args.from_json.read_text(encoding="utf-8"))
        snapshot, source_url = saved["snapshot"], saved["metadata"]["source_url"]
        share_id = validate_claude_share_url(source_url)
        out_dir = args.from_json.parent
    elif args.url:
        share_id = validate_claude_share_url(args.url)
        source_url = f"https://claude.ai/share/{share_id}"
        snapshot = fetch_snapshot(source_url, share_id, args.channel, args.headless, args.timeout)
        out_dir = args.out_dir
    else:
        parser.error("provide a URL or --from-json")

    messages = normalize_messages(snapshot)
    meta = {
        "source_url": source_url,
        "share_id": share_id,
        "title": snapshot.get("snapshot_name"),
        "creator": (snapshot.get("creator") or {}).get("full_name"),
        "created_at": snapshot.get("created_at"),
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    stem = out_dir / f"claude-share-{share_id}"
    if not args.from_json:
        # Keep the raw API payload so future renderers can improve without refetching.
        payload = {"metadata": meta, "snapshot": snapshot, "messages": [{k: v for k, v in m.items() if k != "blocks"} for m in messages]}
        stem.with_suffix(".json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    stem.with_suffix(".md").write_text(to_markdown(meta, messages), encoding="utf-8")

    print(f"Wrote {stem.with_suffix('.md')} ({len(messages)} messages)")
    if not args.from_json:
        print(f"Wrote {stem.with_suffix('.json')}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
