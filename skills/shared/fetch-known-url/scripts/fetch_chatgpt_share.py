#!/usr/bin/env python3
"""Fetch a ChatGPT shared conversation and export Markdown/JSON artifacts."""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


STREAM_RE = re.compile(
    r"window\.__reactRouterContext\.streamController\.enqueue\((\"(?:\\.|[^\"\\])*\")\)"
)


def validate_chatgpt_share_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("Only http/https URLs are supported")
    if parsed.netloc != "chatgpt.com":
        raise ValueError("Only chatgpt.com is currently whitelisted")
    match = re.match(r"^/share/([a-zA-Z0-9-]+)", parsed.path)
    if not match:
        raise ValueError("Only chatgpt.com/share/<id> URLs are supported")
    return match.group(1)


def fetch_html(url: str) -> str:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125 Safari/537.36"
            )
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset, errors="replace")


class ReactRouterPayload:
    def __init__(self, values: list[Any]) -> None:
        self.values = values

    def resolve_ref(self, value: Any) -> Any:
        if isinstance(value, int):
            if value < 0:
                return None
            if value < len(self.values):
                return self.resolve_ref(self.values[value])
            return value
        if isinstance(value, list):
            return [self.resolve_ref(item) for item in value]
        if isinstance(value, dict):
            return {
                str(self.resolve_ref(int(key[1:]) if key.startswith("_") else key)): self.resolve_ref(val)
                for key, val in value.items()
            }
        return value

    def resolve_scalar(self, value: Any) -> Any:
        seen: set[int] = set()
        while isinstance(value, int) and 0 <= value < len(self.values):
            if value in seen:
                return None
            seen.add(value)
            value = self.values[value]
            if isinstance(value, (dict, list)):
                return None
        resolved = self.resolve_ref(value)
        if isinstance(resolved, (dict, list)):
            return None
        return resolved

    def resolve_message(self, message_ref: int | None) -> dict[str, Any] | None:
        if message_ref is None:
            return None
        raw = self.values[message_ref] if 0 <= message_ref < len(self.values) else None
        if not isinstance(raw, dict):
            return None

        message: dict[str, Any] = {}
        for encoded_key, encoded_value in raw.items():
            key = self.key_name(encoded_key)
            if key in {"id", "create_time", "status", "end_turn", "recipient", "channel"}:
                message[key] = self.resolve_scalar(encoded_value)
            elif key == "author":
                message[key] = self.resolve_ref(encoded_value)
            elif key == "content":
                content = self.resolve_ref(encoded_value)
                if isinstance(content, dict):
                    message[key] = {
                        "content_type": content.get("content_type"),
                        "parts": content.get("parts") or [],
                    }
            elif key == "metadata":
                raw_metadata = (
                    self.values[encoded_value]
                    if isinstance(encoded_value, int) and 0 <= encoded_value < len(self.values)
                    else encoded_value
                )
                if isinstance(raw_metadata, dict):
                    metadata: dict[str, Any] = {}
                    wanted = {"model_slug", "request_id", "message_type", "turn_exchange_id"}
                    for meta_key, meta_value in raw_metadata.items():
                        resolved_key = self.key_name(meta_key)
                        if resolved_key in wanted:
                            metadata[resolved_key] = self.resolve_ref(meta_value)
                    message[key] = metadata
        return message

    def key_name(self, encoded_key: str) -> str:
        if encoded_key.startswith("_"):
            resolved = self.resolve_ref(int(encoded_key[1:]))
            return str(resolved)
        return encoded_key


def extract_payload(html: str) -> ReactRouterPayload:
    chunks = STREAM_RE.findall(html)
    if not chunks:
        raise ValueError("No React Router stream payload found")

    first_chunk = ast.literal_eval(chunks[0])
    values = json.loads(first_chunk)
    if not isinstance(values, list):
        raise ValueError("Unexpected ChatGPT payload shape")
    return ReactRouterPayload(values)


def extract_title(html: str, payload: ReactRouterPayload) -> str:
    title_match = re.search(r"<title>(.*?)</title>", html, flags=re.S)
    if title_match:
        return re.sub(r"\s+", " ", title_match.group(1)).strip()

    for item in payload.values:
        if isinstance(item, str) and item.startswith("ChatGPT - "):
            return item
    return "ChatGPT shared conversation"


def extract_messages(payload: ReactRouterPayload) -> list[dict[str, Any]]:
    mapping_ref = None
    current_node = None

    for idx, value in enumerate(payload.values):
        if value == "mapping":
            mapping_ref = payload.values[idx + 1] if idx + 1 < len(payload.values) else None
        if value == "current_node":
            current_node = payload.values[idx + 1] if idx + 1 < len(payload.values) else None

    if mapping_ref is None:
        raise ValueError("Conversation mapping not found")

    mapping_raw = payload.values[mapping_ref] if isinstance(mapping_ref, int) else mapping_ref
    if not isinstance(mapping_raw, dict):
        raise ValueError("Conversation mapping has unexpected shape")

    nodes: dict[str, dict[str, Any]] = {}
    for encoded_id, node_ref in mapping_raw.items():
        node_id = payload.key_name(encoded_id)
        node_raw = payload.values[node_ref] if isinstance(node_ref, int) else node_ref
        if not isinstance(node_raw, dict):
            continue

        node: dict[str, Any] = {"id": node_id}
        for encoded_key, encoded_value in node_raw.items():
            key = payload.key_name(encoded_key)
            if key == "message":
                node[key] = payload.resolve_message(encoded_value if isinstance(encoded_value, int) else None)
            else:
                node[key] = payload.resolve_ref(encoded_value)
        nodes[node_id] = node

    ordered_ids: list[str] = []
    cursor = payload.resolve_ref(current_node) if isinstance(current_node, int) else current_node
    while isinstance(cursor, str) and cursor in nodes:
        ordered_ids.append(cursor)
        cursor = nodes[cursor].get("parent")

    ordered_ids.reverse()
    if not ordered_ids:
        ordered_ids = list(reversed(list(nodes.keys())))

    messages: list[dict[str, Any]] = []
    for node_id in ordered_ids:
        message = nodes[node_id].get("message")
        if not isinstance(message, dict):
            continue

        author = message.get("author") or {}
        content = message.get("content") or {}
        parts = content.get("parts") or []
        text_parts = [part for part in parts if isinstance(part, str) and part.strip()]
        if not text_parts:
            continue

        messages.append(
            {
                "id": message.get("id", node_id),
                "role": author.get("role", "unknown") if isinstance(author, dict) else "unknown",
                "create_time": message.get("create_time"),
                "content_type": content.get("content_type"),
                "text": "\n\n".join(text_parts).strip(),
                "metadata": message.get("metadata", {}),
            }
        )
    return messages


def write_markdown(path: Path, url: str, title: str, messages: list[dict[str, Any]]) -> None:
    lines = [
        f"# {title}",
        "",
        f"- Source URL: {url}",
        f"- Fetched at: {datetime.now(timezone.utc).isoformat()}",
        f"- Messages: {len(messages)}",
        "",
    ]

    for index, message in enumerate(messages, start=1):
        role = str(message.get("role", "unknown")).upper()
        created = message.get("create_time")
        created_text = ""
        if isinstance(created, (int, float)):
            created_text = " - " + datetime.fromtimestamp(created, tz=timezone.utc).isoformat()
        lines.extend([f"## {index}. {role}{created_text}", "", message["text"], ""])

    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    parser.add_argument("--out-dir", default="fetched-chatgpt")
    parser.add_argument("--html-file", help="Use an already fetched HTML file instead of network fetch")
    args = parser.parse_args()

    share_id = validate_chatgpt_share_url(args.url)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    stem = f"chatgpt-share-{share_id}"
    html_path = out_dir / f"{stem}.html"
    json_path = out_dir / f"{stem}.json"
    md_path = out_dir / f"{stem}.md"

    if args.html_file:
        html = Path(args.html_file).read_text(encoding="utf-8")
    else:
        html = fetch_html(args.url)
        html_path.write_text(html, encoding="utf-8")

    payload = extract_payload(html)
    title = extract_title(html, payload)
    messages = extract_messages(payload)
    if not messages:
        raise ValueError("No readable conversation messages were extracted")

    data = {
        "source_url": args.url,
        "share_id": share_id,
        "title": title,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "message_count": len(messages),
        "messages": messages,
    }
    json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(md_path, args.url, title, messages)

    print(md_path)
    print(json_path)
    print(html_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
