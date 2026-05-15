#!/usr/bin/env python3
"""Extract readable strings from a ChatGPT shared conversation HTML dump.

This is intentionally heuristic: ChatGPT share pages are rendered from a React
shell plus streamed hydration payloads. The script extracts and scores decoded
string literals so an agent can recover user prompts, final answers, and task
requirements without reading a huge blob by hand.
"""
from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

NOISE_SUBSTRINGS = (
    "/cdn/assets/",
    "sprites-core",
    "alternate\" hrefLang",
    "ChatGPT helps you",
    "Skip to content",
    "New chat",
    "Search chats",
    "Open sidebar",
    "Close sidebar",
    "data-testid",
    "radix-",
    "traceId",
    "traceTime",
    "disablePrefetch",
    "shouldPrefetch",
    "feature_gates",
    "secondary_exposures",
    "statsigEnvironment",
    "sdkInfo",
)

KEYWORD_HINTS = (
    "/goal",
    "Context:",
    "requirements",
    "Validation:",
    "Input timeline",
    "Audio processing",
    "Web app",
    "Deployment",
    "Codex",
    "ffmpeg",
    "librosa",
    "Vercel",
    "iPhone",
    "剪",
    "音訊",
    "編舞",
    "段落",
)


def decode_js_string_literal(raw: str) -> str | None:
    try:
        return json.loads('"' + raw + '"')
    except Exception:
        try:
            return bytes(raw, "utf-8").decode("unicode_escape")
        except Exception:
            return None


def candidate_strings(text: str) -> list[str]:
    decoded: list[str] = []

    # First decode streamController.enqueue("...") chunks, then scan the decoded
    # stream payload for quoted strings.
    chunks = re.findall(r'streamController\.enqueue\("((?:\\.|[^"\\])*)"\)', text)
    haystacks = [text]
    for chunk in chunks:
        value = decode_js_string_literal(chunk)
        if value:
            haystacks.append(value)

    string_re = re.compile(r'"((?:\\.|[^"\\]){8,})"')
    seen: set[str] = set()
    for haystack in haystacks:
        for match in string_re.finditer(haystack):
            value = decode_js_string_literal(match.group(1))
            if not value:
                continue
            value = html.unescape(value).replace("\\n", "\n").strip()
            value = re.sub(r"\n{3,}", "\n\n", value)
            value = re.sub(r"[ \t]{2,}", " ", value)
            if value and value not in seen:
                seen.add(value)
                decoded.append(value)
    return decoded


def useful(value: str) -> bool:
    if len(value) < 35:
        return False
    if any(noise in value for noise in NOISE_SUBSTRINGS):
        return False
    if value.startswith(("http://", "https://")) and "chatgpt.com/share" not in value:
        return False
    if len(value) > 20000 and (value.lstrip().startswith("{") or "feature_gates" in value):
        return False
    if value.count("{") > 30 and value.count("\n") < 5:
        return False
    alphaish = sum(ch.isalpha() or "\u4e00" <= ch <= "\u9fff" for ch in value)
    if alphaish < 15:
        return False
    return True


def score(value: str) -> tuple[int, int]:
    score_value = 0
    score_value += min(len(value) // 200, 8)
    score_value += value.count("\n")
    score_value += sum(5 for hint in KEYWORD_HINTS if hint.lower() in value.lower())
    if "user" in value.lower() or "assistant" in value.lower():
        score_value += 1
    return (score_value, len(value))


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: extract_chatgpt_share_text.py <chatgpt-share.html>", file=sys.stderr)
        return 2

    path = Path(sys.argv[1])
    text = path.read_text(encoding="utf-8", errors="replace")
    candidates = [s for s in candidate_strings(text) if useful(s)]

    # Keep original order for high-signal strings, but suppress exact duplicates and
    # very obvious substrings of longer candidates.
    ranked = sorted(candidates, key=score, reverse=True)
    selected: list[str] = []
    for item in ranked:
        if any(item in kept and len(kept) > len(item) + 80 for kept in selected):
            continue
        selected.append(item)
        if len(selected) >= 40:
            break

    if not selected:
        print("INCOMPLETE_SOURCE: no useful ChatGPT share text extracted", file=sys.stderr)
        return 2

    print("# Extracted ChatGPT Share Text")
    print()
    print(f"Source file: {path}")
    print(f"Candidates: {len(candidates)}; emitted: {len(selected)}")
    print()
    for i, item in enumerate(selected, 1):
        print(f"## Candidate {i}")
        print()
        print(item)
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
