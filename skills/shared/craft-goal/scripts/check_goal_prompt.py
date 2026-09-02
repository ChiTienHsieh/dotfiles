#!/usr/bin/env python3
"""Check that a /goal prompt fits the Codex app input limit.

Usage: check_goal_prompt.py [PROMPT_FILE]   (reads stdin when no file is given)
Exit 0 when the prompt is under the limit, 1 otherwise.
"""
import sys
from pathlib import Path

# Mirrors the Codex app `/goal` input limit; update here when the app changes it.
GOAL_PROMPT_CHAR_LIMIT = 4000


def main(argv: list[str]) -> int:
    if len(argv) > 1:
        text = Path(argv[1]).read_text(encoding="utf-8")
    else:
        text = sys.stdin.read()
    count = len(text)
    if count < GOAL_PROMPT_CHAR_LIMIT:
        print(f"OK: {count} characters (limit {GOAL_PROMPT_CHAR_LIMIT})")
        return 0
    print(
        f"TOO LONG: {count} characters (limit {GOAL_PROMPT_CHAR_LIMIT}); "
        "shorten the prompt or move detail into a tracked task spec file"
    )
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
