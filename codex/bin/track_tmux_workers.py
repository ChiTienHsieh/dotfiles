#!/usr/bin/env python3
"""Track tmux workers owned by one Codex session and guard Stop cleanup."""

from __future__ import annotations

import json
import os
import re
import sys
import tempfile
from json import JSONDecodeError
from pathlib import Path
from typing import Iterator


TRACK_DIR = Path(
    os.environ.get(
        "CODEX_TMUX_WORKER_TRACK_DIR",
        str(Path(os.environ.get("TMPDIR", "/private/tmp")) / "codex-tmux-workers"),
    )
)
MARKER_RE = re.compile(
    r"^CODEX_TMUX_WORKER_(OPEN|CLOSED)=(session|pane):([^\s]+)$",
    flags=re.MULTILINE,
)
SESSION_RE = re.compile(r"^[A-Za-z0-9_.-]+$")
PANE_RE = re.compile(r"^%[0-9]+$")
TMUX_ACTIONS = {
    ("OPEN", "session"): "new-session",
    ("OPEN", "pane"): "split-window",
}


def emit(payload: dict[str, object]) -> int:
    print(json.dumps(payload, ensure_ascii=False))
    return 0


def session_track_path(session_id: object) -> Path | None:
    if not isinstance(session_id, str) or not session_id:
        return None
    safe_id = re.sub(r"[^A-Za-z0-9_.-]", "_", session_id)
    return TRACK_DIR / f"{safe_id}.json"


def valid_worker(kind: str, target: str) -> bool:
    if kind == "session":
        return SESSION_RE.fullmatch(target) is not None
    if kind == "pane":
        return PANE_RE.fullmatch(target) is not None
    return False


def load_workers(session_id: object) -> set[tuple[str, str]]:
    path = session_track_path(session_id)
    if not path or not path.exists():
        return set()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, JSONDecodeError):
        return set()

    raw_workers = data.get("workers") if isinstance(data, dict) else None
    if not isinstance(raw_workers, list):
        return set()

    workers: set[tuple[str, str]] = set()
    for item in raw_workers:
        if not isinstance(item, dict):
            continue
        kind = item.get("kind")
        target = item.get("target")
        if isinstance(kind, str) and isinstance(target, str) and valid_worker(kind, target):
            workers.add((kind, target))
    return workers


def save_workers(session_id: object, workers: set[tuple[str, str]]) -> None:
    path = session_track_path(session_id)
    if not path:
        return

    try:
        if not workers:
            path.unlink(missing_ok=True)
            return
        TRACK_DIR.mkdir(mode=0o700, parents=True, exist_ok=True)
        payload = {
            "workers": [
                {"kind": kind, "target": target}
                for kind, target in sorted(workers)
            ]
        }
        temp_name: str | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", dir=TRACK_DIR, delete=False
            ) as handle:
                temp_name = handle.name
                json.dump(payload, handle, indent=2)
                handle.write("\n")
            os.chmod(temp_name, 0o600)
            os.replace(temp_name, path)
        finally:
            if temp_name:
                Path(temp_name).unlink(missing_ok=True)
    except OSError:
        return


def strings_in(value: object) -> Iterator[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from strings_in(item)
    elif isinstance(value, list):
        for item in value:
            yield from strings_in(item)


def tmux_action_present(tool_input: object, action: str, kind: str) -> bool:
    text = "\n".join(strings_in(tool_input))
    if not re.search(rf"\btmux\s+{re.escape(action)}\b", text):
        return False
    if kind == "session":
        return action in {"new-session", "kill-session", "has-session", "capture-pane"}
    return action in {"split-window", "kill-pane", "display-message", "capture-pane"}


def lifecycle_markers(tool_response: object) -> set[tuple[str, str, str]]:
    markers: set[tuple[str, str, str]] = set()
    for text in strings_in(tool_response):
        for match in MARKER_RE.finditer(text):
            state, kind, target = match.groups()
            if valid_worker(kind, target):
                markers.add((state, kind, target))
    return markers


def marker_matches_command(
    tool_input: object, state: str, kind: str, target: str
) -> bool:
    if state == "OPEN":
        action_present = tmux_action_present(
            tool_input, TMUX_ACTIONS[(state, kind)], kind
        )
        if kind == "pane":
            return action_present
        return action_present and target in "\n".join(strings_in(tool_input))

    closing_actions = (
        ("kill-session", "session"),
        ("has-session", "session"),
        ("kill-pane", "pane"),
        ("display-message", "pane"),
    )
    return target in "\n".join(strings_in(tool_input)) and any(
        candidate_kind == kind and tmux_action_present(tool_input, action, kind)
        for action, candidate_kind in closing_actions
    )


def record_lifecycle(payload: dict[str, object]) -> int:
    workers = load_workers(payload.get("session_id"))
    changed = False

    for state, kind, target in lifecycle_markers(payload.get("tool_response")):
        if not marker_matches_command(payload.get("tool_input"), state, kind, target):
            continue
        worker = (kind, target)
        if state == "OPEN" and worker not in workers:
            workers.add(worker)
            changed = True
        elif state == "CLOSED" and worker in workers:
            workers.remove(worker)
            changed = True

    if changed:
        save_workers(payload.get("session_id"), workers)
    return emit({"continue": True})


def message_retains_all_workers(
    message: object, workers: set[tuple[str, str]]
) -> bool:
    if not isinstance(message, str):
        return False
    return all(
        re.search(
            rf"(?:保留中的 tmux worker：|Retained tmux worker:)\s*"
            rf"{re.escape(target)}\s*[（(][^）)]+[）)]",
            message,
        )
        is not None
        for _, target in workers
    )


def stop_guard(payload: dict[str, object]) -> int:
    workers = load_workers(payload.get("session_id"))
    if not workers or payload.get("stop_hook_active"):
        return emit({"continue": True})
    if message_retains_all_workers(payload.get("last_assistant_message"), workers):
        return emit({"continue": True})

    shown = "\n".join(f"- {kind}: {target}" for kind, target in sorted(workers))
    reason = (
        "This Codex task still owns unresolved tmux workers:\n"
        f"{shown}\n\n"
        "Before ending, read each worker's latest pane state. If its result has been "
        "accepted, close the exact session or pane with an explicit tmux command under "
        "the normal Guardian escalation, emit its CODEX_TMUX_WORKER_CLOSED marker only "
        "after success, and verify it is gone. Never use pkill or a wildcard. If a worker "
        "must intentionally remain active, tell the user why using the exact phrase "
        "'保留中的 tmux worker：<target>（<reason>）'. This hook must not call tmux or "
        "terminate processes itself."
    )
    return emit({"decision": "block", "reason": reason})


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except JSONDecodeError:
        return emit({"continue": True})

    if not isinstance(payload, dict):
        return emit({"continue": True})
    if payload.get("hook_event_name") == "PostToolUse":
        return record_lifecycle(payload)
    if payload.get("hook_event_name") == "Stop":
        return stop_guard(payload)
    return emit({"continue": True})


if __name__ == "__main__":
    raise SystemExit(main())
