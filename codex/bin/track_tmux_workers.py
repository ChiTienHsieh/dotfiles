#!/usr/bin/env python3
"""Track tmux workers owned by one Codex session and guard Stop cleanup."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shlex
import stat
import sys
import tempfile
from contextlib import contextmanager
from fcntl import LOCK_EX, LOCK_UN, flock
from json import JSONDecodeError
from pathlib import Path
from typing import Iterator

HOOKS_DIR = Path(__file__).resolve().parents[1] / "hooks"
sys.path.insert(0, str(HOOKS_DIR))

from private_temp_state import (  # noqa: E402
    atomic_write_private,
    ensure_private_directory,
    read_private_text,
    validate_private_file,
)


DEFAULT_TRACK_DIR = Path(tempfile.gettempdir()) / f"codex-tmux-workers-{os.getuid()}"
TRACK_DIR = Path(
    os.environ.get(
        "CODEX_TMUX_WORKER_TRACK_DIR",
        str(DEFAULT_TRACK_DIR),
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
SESSION_CLOSED_MARKER_RE = re.compile(
    r"'CODEX_TMUX_WORKER_CLOSED=session:(?P<target>[A-Za-z0-9_.-]+)'"
)
PANE_CLOSED_MARKER_RE = re.compile(
    r"'CODEX_TMUX_WORKER_CLOSED=pane:(?P<target>%[0-9]+)'"
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

    descriptor = -1
    try:
        ensure_private_directory(TRACK_DIR)
        lock_path = path.with_suffix(".lock")
        flags = os.O_RDWR | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0)
        descriptor = os.open(lock_path, flags, 0o600)
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode) or metadata.st_uid != os.getuid():
            raise RuntimeError("tmux worker lock file is unsafe")
        os.fchmod(descriptor, 0o600)
        with os.fdopen(descriptor, "a+", encoding="utf-8") as handle:
            descriptor = -1
            flock(handle.fileno(), LOCK_EX)
            try:
                yield
            finally:
                flock(handle.fileno(), LOCK_UN)
    except (OSError, RuntimeError) as exc:
        raise LedgerError(f"cannot lock tmux worker ledger {path}: {exc}") from exc
    finally:
        if descriptor >= 0:
            os.close(descriptor)


def valid_worker(kind: str, target: str) -> bool:
    if kind == "session":
        return SESSION_RE.fullmatch(target) is not None
    if kind == "pane":
        return PANE_RE.fullmatch(target) is not None
    return False


def load_workers(session_id: object) -> set[tuple[str, str]]:
    path = session_track_path(session_id)
    if not path:
        return set()
    try:
        content = read_private_text(path)
        if content is None:
            return set()
        data = json.loads(content)
    except (OSError, RuntimeError, JSONDecodeError) as exc:
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
            try:
                validate_private_file(path)
            except FileNotFoundError:
                return
            path.unlink(missing_ok=True)
            return
        payload = {
            "workers": [
                {"kind": kind, "target": target}
                for kind, target in sorted(workers)
            ]
        }
        atomic_write_private(path, json.dumps(payload, indent=2) + "\n")
    except (OSError, RuntimeError) as exc:
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
    if tool_input.get("shell") is not None:
        return None
    command = tool_input.get("command")
    return command if isinstance(command, str) else None


def canonical_open_targets(command: str | None, kind: str) -> set[str]:
    action = "new-session" if kind == "session" else "split-window"
    targets: set[str] = set()
    if command is None:
        return targets
    command = re.sub(r"\\\r?\n", "", command)
    if re.search(r"[&|;<>\r\n]|`|\$\(", command):
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
    if command is None:
        return set()
    marker_re = SESSION_CLOSED_MARKER_RE if kind == "session" else PANE_CLOSED_MARKER_RE
    match = marker_re.search(command)
    if not match:
        return set()
    target = match.group("target")
    expected = (
        session_closed_receipt_command(target)
        if kind == "session"
        else pane_closed_receipt_command(target)
    )
    return {target} if command == expected else set()


def _closed_receipt_command(
    *, list_args: str, format_field: str, target: str, marker: str
) -> str:
    return (
        f"codex_tmux_targets=$(tmux {list_args} -F '#{{{format_field}}}' 2>/dev/null) && {{ "
        "printf '%s\\n' \"$codex_tmux_targets\" | "
        f"grep -Fx -- '{target}' >/dev/null; codex_tmux_grep_status=$?; "
        "if [ \"$codex_tmux_grep_status\" -eq 1 ]; then "
        f"printf '%s\\n' '{marker}'; "
        "else [ \"$codex_tmux_grep_status\" -eq 0 ]; fi; }"
    )


def session_closed_receipt_command(target: str) -> str:
    if not SESSION_RE.fullmatch(target):
        raise ValueError("invalid tmux session target")
    return _closed_receipt_command(
        list_args="list-sessions",
        format_field="session_name",
        target=target,
        marker=f"CODEX_TMUX_WORKER_CLOSED=session:{target}",
    )


def pane_closed_receipt_command(target: str) -> str:
    if not PANE_RE.fullmatch(target):
        raise ValueError("invalid tmux pane target")
    return _closed_receipt_command(
        list_args="list-panes -a",
        format_field="pane_id",
        target=target,
        marker=f"CODEX_TMUX_WORKER_CLOSED=pane:{target}",
    )


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
            rf"保留中的 tmux worker：\s*{re.escape(target)}\s*[（(][^）)]+[）)]",
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
                    session_closed_receipt_command(target),
                ]
            )
        else:
            cleanup_commands.extend(
                [
                    f"tmux kill-pane -t {target}",
                    pane_closed_receipt_command(target),
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
