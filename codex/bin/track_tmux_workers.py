#!/usr/bin/env python3
"""Track tmux workers owned by one Codex session and guard Stop cleanup."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shlex
import sys
import tempfile
from contextlib import contextmanager
from fcntl import LOCK_EX, LOCK_UN, flock
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
OPEN_FORMATS = {
    "session": "CODEX_TMUX_WORKER_OPEN=session:#{session_name}",
    "pane": "CODEX_TMUX_WORKER_OPEN=pane:#{pane_id}",
}
SESSION_CLOSED_RECEIPT_RE = re.compile(
    r"^\s*tmux\s+has-session\s+-t\s+(?P<target>[A-Za-z0-9_.-]+)"
    r"\s+2>/dev/null\s+\|\|\s+printf\s+'%s\\n'\s+"
    r"'CODEX_TMUX_WORKER_CLOSED=session:(?P<marker>[A-Za-z0-9_.-]+)'\s*$"
)
PANE_CLOSED_RECEIPT_RE = re.compile(
    r"^\s*tmux\s+display-message\s+-p\s+-t\s+(?P<target>%[0-9]+)"
    r"\s+'#\{pane_id\}'\s+>/dev/null\s+2>&1\s+\|\|\s+printf\s+'%s\\n'\s+"
    r"'CODEX_TMUX_WORKER_CLOSED=pane:(?P<marker>%[0-9]+)'\s*$"
)


class LedgerError(RuntimeError):
    pass


def emit(payload: dict[str, object]) -> int:
    print(json.dumps(payload, ensure_ascii=False))
    return 0


def session_track_path(session_id: object) -> Path | None:
    if not isinstance(session_id, str) or not session_id:
        return None
    digest = hashlib.sha256(session_id.encode("utf-8")).hexdigest()
    return TRACK_DIR / f"{digest}.json"


@contextmanager
def ledger_lock(session_id: object) -> Iterator[None]:
    path = session_track_path(session_id)
    if not path:
        yield
        return

    try:
        TRACK_DIR.mkdir(mode=0o700, parents=True, exist_ok=True)
        lock_path = path.with_suffix(".lock")
        with lock_path.open("a+", encoding="utf-8") as handle:
            os.chmod(lock_path, 0o600)
            flock(handle.fileno(), LOCK_EX)
            try:
                yield
            finally:
                flock(handle.fileno(), LOCK_UN)
    except OSError as exc:
        raise LedgerError(f"cannot lock tmux worker ledger {path}: {exc}") from exc


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
    except (OSError, JSONDecodeError) as exc:
        raise LedgerError(f"cannot read tmux worker ledger {path}: {exc}") from exc

    raw_workers = data.get("workers") if isinstance(data, dict) else None
    if not isinstance(raw_workers, list):
        raise LedgerError(f"invalid tmux worker ledger structure: {path}")

    workers: set[tuple[str, str]] = set()
    for item in raw_workers:
        if not isinstance(item, dict):
            raise LedgerError(f"invalid tmux worker entry in {path}")
        kind = item.get("kind")
        target = item.get("target")
        if not (
            isinstance(kind, str)
            and isinstance(target, str)
            and valid_worker(kind, target)
        ):
            raise LedgerError(f"invalid tmux worker entry in {path}")
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
    except OSError as exc:
        raise LedgerError(f"cannot write tmux worker ledger {path}: {exc}") from exc


def post_tool_tracking_error(message: str) -> int:
    return emit(
        {
            "continue": True,
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": (
                    f"tmux worker lifecycle tracking failed: {message}. Do not assume "
                    "the Stop guard will clean up this worker; inspect and resolve its "
                    "exact tmux target before ending the task."
                ),
            },
        }
    )


def strings_in(value: object) -> Iterator[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from strings_in(item)
    elif isinstance(value, list):
        for item in value:
            yield from strings_in(item)


def option_value(tokens: list[str], option: str) -> str | None:
    if tokens.count(option) != 1:
        return None
    index = tokens.index(option)
    if index + 1 >= len(tokens):
        return None
    return tokens[index + 1]


def bash_command(tool_input: object) -> str | None:
    if not isinstance(tool_input, dict):
        return None
    command = tool_input.get("command")
    return command if isinstance(command, str) else None


def canonical_open_targets(command: str | None, kind: str) -> set[str]:
    action = "new-session" if kind == "session" else "split-window"
    targets: set[str] = set()
    if command is None or re.search(r"[&|;<>\r\n]|`|\$\(", command):
        return targets
    try:
        tokens = shlex.split(command)
    except ValueError:
        return targets
    if len(tokens) < 2 or tokens[0] != "tmux" or tokens[1] != action:
        return targets
    if "-P" not in tokens or option_value(tokens, "-F") != OPEN_FORMATS[kind]:
        return targets
    if kind == "pane":
        targets.add("*")
        return targets
    target = option_value(tokens, "-s")
    if target and valid_worker(kind, target):
        targets.add(target)
    return targets


def canonical_closed_targets(command: str | None, kind: str) -> set[str]:
    receipt_re = (
        SESSION_CLOSED_RECEIPT_RE if kind == "session" else PANE_CLOSED_RECEIPT_RE
    )
    if command is None:
        return set()
    match = receipt_re.fullmatch(command)
    if match and match.group("target") == match.group("marker"):
        return {match.group("target")}
    return set()


def lifecycle_markers(tool_response: object) -> set[tuple[str, str, str]]:
    markers: set[tuple[str, str, str]] = set()
    for text in strings_in(tool_response):
        for match in MARKER_RE.finditer(text):
            state, kind, target = match.groups()
            if valid_worker(kind, target):
                markers.add((state, kind, target))
    return markers


def marker_matches_command(tool_input: object, state: str, kind: str, target: str) -> bool:
    command = bash_command(tool_input)
    if state == "OPEN":
        open_targets = canonical_open_targets(command, kind)
        return "*" in open_targets or target in open_targets
    return target in canonical_closed_targets(command, kind)


def record_lifecycle(payload: dict[str, object]) -> int:
    markers = {
        marker
        for marker in lifecycle_markers(payload.get("tool_response"))
        if marker_matches_command(payload.get("tool_input"), *marker)
    }
    if not markers:
        return emit({"continue": True})

    try:
        with ledger_lock(payload.get("session_id")):
            workers = load_workers(payload.get("session_id"))
            changed = False

            for state, kind, target in markers:
                worker = (kind, target)
                if state == "OPEN" and worker not in workers:
                    workers.add(worker)
                    changed = True
                elif state == "CLOSED" and worker in workers:
                    workers.remove(worker)
                    changed = True

            if changed:
                save_workers(payload.get("session_id"), workers)
    except LedgerError as exc:
        return post_tool_tracking_error(str(exc))
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
    if payload.get("stop_hook_active"):
        return emit({"continue": True})
    try:
        with ledger_lock(payload.get("session_id")):
            workers = load_workers(payload.get("session_id"))
    except LedgerError as exc:
        return emit(
            {
                "decision": "block",
                "reason": (
                    f"The tmux worker ledger is unreadable: {exc}. Do not assume workers "
                    "were cleaned up. Inspect the exact tmux targets created by this task, "
                    "resolve or explicitly retain them, then repair or remove only this "
                    "temporary ledger after confirming its contents are unrecoverable."
                ),
            }
        )
    if not workers:
        return emit({"continue": True})
    if message_retains_all_workers(payload.get("last_assistant_message"), workers):
        return emit({"continue": True})

    shown = "\n".join(f"- {kind}: {target}" for kind, target in sorted(workers))
    cleanup_commands: list[str] = []
    for kind, target in sorted(workers):
        if kind == "session":
            cleanup_commands.extend(
                [
                    f"tmux kill-session -t {target}",
                    f"tmux has-session -t {target} 2>/dev/null || printf '%s\\n' "
                    f"'CODEX_TMUX_WORKER_CLOSED=session:{target}'",
                ]
            )
        else:
            cleanup_commands.extend(
                [
                    f"tmux kill-pane -t {target}",
                    f"tmux display-message -p -t {target} '#{{pane_id}}' >/dev/null "
                    f"2>&1 || printf '%s\\n' "
                    f"'CODEX_TMUX_WORKER_CLOSED=pane:{target}'",
                ]
            )
    cleanup = "\n".join(cleanup_commands)
    reason = (
        "This Codex task still owns unresolved tmux workers:\n"
        f"{shown}\n\n"
        "Before ending, read each worker's latest pane state. If its result has been "
        "accepted, close the exact session or pane with an explicit tmux command under "
        "the normal Guardian escalation, then run its matching canonical absence receipt "
        "as a separate command. Use these exact commands for the tracked targets:\n"
        f"{cleanup}\n\n"
        "Never use pkill or a wildcard. If a worker "
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
