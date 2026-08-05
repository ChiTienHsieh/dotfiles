#!/usr/bin/env python3
"""Compose Codex Stop policies into one bounded continuation prompt."""

from __future__ import annotations

import json
import sys
from json import JSONDecodeError

from request_thread_title import prepare_title_request, take_title_request
from set_thread_title import set_thread_title
from stop_dirty_worktree import build_dirty_worktree_followup, track_touched_worktrees


TITLE_CHECKPOINT = """Thread-title checkpoint (Codex CLI):

Classify the current thread by the user's next required action. Update the title only when one of these meaningful states applies:
- ⏸️: blocked by data, permission, CI, deployment, or another prerequisite that needs user help.
- ⏳: waiting only for a simple user choice.
- 🔎: the user needs to understand important context or a trade-off.
- 📦: no unfinished responsibility or important learning remains; the thread is worth archiving.

Never treat agent stop, idle, a final answer, or a local-only commit as enough for 📦. If the agent should keep working and the user does not need to act, do not rename the thread.

When renaming, create concise Traditional Chinese in exactly this format:
<one emoji> <where>｜<user purpose>｜<progress>

Put the repo, project, or smallest recognizable scope in <where>. Keep identifiers and technical proper nouns unchanged. Aim for 24–32 characters; 40 is the hard cap.

If the built-in `apply_patch` tool is available, use it exactly once to replace the complete contents of this prepared data file with only the title and one trailing newline:
{request_path}

The file currently contains `NO_TITLE_REQUEST`. Put the title only in the patch data. Never use Bash, a shell command, or shell redirection to write the title. When this Stop-hook continuation finishes, the hook consumes and validates the private data file, then applies it through only the stable Codex app-server method `thread/name/set`; this is the non-interactive equivalent of the CLI user's `/rename` command.

This automation may set a title only. Never archive, unarchive, delete, or otherwise change thread lifecycle state. 📦 is merely a recommendation that the user may archive later. If `apply_patch` or the prepared file is unavailable, skip quietly. If the one patch attempt fails, mention one concise non-blocking warning. This continuation was already created by the Stop hook; do not request another continuation or retry.
"""


def emit(payload: dict[str, object]) -> int:
    print(json.dumps(payload, ensure_ascii=False))
    return 0


def apply_queued_title(payload: dict[str, object]) -> dict[str, object]:
    thread_id = str(payload.get("session_id") or "")
    try:
        request = take_title_request(thread_id)
        if request:
            set_thread_title(*request)
    except (OSError, ValueError, RuntimeError):
        return {
            "continue": True,
            "systemMessage": "Thread title update failed; continuing without retry.",
        }
    return {"continue": True}


def build_stop_result(payload: dict[str, object]) -> dict[str, object]:
    already_continued_by_stop_hook = payload.get("stop_hook_active") is True
    if already_continued_by_stop_hook:
        return apply_queued_title(payload)

    thread_id = str(payload.get("session_id") or "")
    try:
        request_path = str(prepare_title_request(thread_id))
    except (OSError, ValueError, RuntimeError):
        request_path = "UNAVAILABLE — skip the title update quietly"
    reasons = [
        TITLE_CHECKPOINT.format(request_path=request_path)
    ]
    dirty_reason = build_dirty_worktree_followup(payload)
    if dirty_reason:
        reasons.append(f"Dirty-worktree checkpoint:\n\n{dirty_reason}")

    reasons.append(
        "If the dirty-worktree checkpoint requires user-visible cleanup options, provide only "
        "those options after the title attempt. Otherwise do not repeat or expand the assistant's "
        "previous final answer."
    )
    return {"decision": "block", "reason": "\n\n".join(reasons)}


def handle_payload(payload: dict[str, object]) -> dict[str, object]:
    event_name = payload.get("hook_event_name")
    if event_name == "PostToolUse":
        track_touched_worktrees(payload)
        return {"continue": True}
    if event_name == "Stop":
        return build_stop_result(payload)
    return {"continue": True}


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except JSONDecodeError:
        return emit({"continue": True})
    if not isinstance(payload, dict):
        return emit({"continue": True})
    return emit(handle_payload(payload))


if __name__ == "__main__":
    raise SystemExit(main())
