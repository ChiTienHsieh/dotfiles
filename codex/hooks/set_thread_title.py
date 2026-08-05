#!/usr/bin/env python3
"""Set a persisted Codex CLI thread title through the app-server protocol."""

from __future__ import annotations

import argparse
import json
import os
import re
import select
import shutil
import subprocess
import sys
import time
from typing import BinaryIO


TITLE_PATTERN = re.compile(
    r"^(?:⏸️|⏳|🔎|📦) [^｜\r\n]+｜[^｜\r\n]+｜[^｜\r\n]+$"
)
THREAD_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{8,128}$")
HARD_TITLE_LIMIT = 40


def validate_thread_id(thread_id: str) -> str:
    if not THREAD_ID_PATTERN.fullmatch(thread_id):
        raise ValueError("invalid Codex thread id")
    return thread_id


def validate_title(title: str) -> str:
    if len(title) > HARD_TITLE_LIMIT:
        raise ValueError(f"title exceeds the {HARD_TITLE_LIMIT}-character hard cap")
    if not TITLE_PATTERN.fullmatch(title):
        raise ValueError(
            "title must match: <⏸️|⏳|🔎|📦> <where>｜<user purpose>｜<progress>"
        )
    return title


def protocol_request_messages(thread_id: str, title: str) -> list[dict[str, object]]:
    return [
        {
            "method": "initialize",
            "id": 0,
            "params": {
                "clientInfo": {
                    "name": "codex_thread_title_hook",
                    "title": "Codex thread title hook",
                    "version": "1.0.0",
                }
            },
        },
        {"method": "initialized", "params": {}},
        {
            "method": "thread/name/set",
            "id": 1,
            "params": {"threadId": thread_id, "name": title},
        },
    ]


def protocol_messages(thread_id: str, title: str) -> str:
    messages = protocol_request_messages(thread_id, title)
    return "".join(json.dumps(message, ensure_ascii=False) + "\n" for message in messages)


def send_message(stream: BinaryIO, message: dict[str, object]) -> None:
    encoded = (json.dumps(message, ensure_ascii=False) + "\n").encode("utf-8")
    stream.write(encoded)
    stream.flush()


def wait_for_response(
    stream: BinaryIO,
    request_id: int,
    pending: bytearray,
    deadline: float,
) -> dict[str, object]:
    file_descriptor = stream.fileno()
    while True:
        while b"\n" in pending:
            raw_line, _, remainder = pending.partition(b"\n")
            pending[:] = remainder
            try:
                message = json.loads(raw_line.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                continue
            if isinstance(message, dict) and message.get("id") == request_id:
                return message

        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise RuntimeError("Codex app-server title update timed out")
        readable, _, _ = select.select([file_descriptor], [], [], remaining)
        if not readable:
            raise RuntimeError("Codex app-server title update timed out")
        chunk = os.read(file_descriptor, 4096)
        if not chunk:
            raise RuntimeError("Codex app-server closed before replying")
        pending.extend(chunk)


def response_error(response: dict[str, object]) -> str | None:
    if "result" in response:
        return None
    error = response.get("error")
    if isinstance(error, dict):
        message = error.get("message")
        return str(message or "Codex rejected the request")
    return "Codex app-server returned an invalid response"


def set_thread_title(thread_id: str, title: str, timeout: float = 15.0) -> None:
    codex = shutil.which("codex")
    if not codex:
        raise RuntimeError("codex executable is unavailable")

    try:
        process = subprocess.Popen(
            [codex, "app-server", "--stdio"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=0,
        )
    except OSError as exc:
        raise RuntimeError("failed to start Codex app-server") from exc
    if process.stdin is None or process.stdout is None:
        process.kill()
        raise RuntimeError("Codex app-server pipes are unavailable")

    messages = protocol_request_messages(thread_id, title)
    pending = bytearray()
    deadline = time.monotonic() + timeout
    failure: RuntimeError | None = None
    rename_response: dict[str, object] | None = None
    try:
        send_message(process.stdin, messages[0])
        initialize_response = wait_for_response(process.stdout, 0, pending, deadline)
        initialize_error = response_error(initialize_response)
        if initialize_error:
            raise RuntimeError(initialize_error)

        send_message(process.stdin, messages[1])
        send_message(process.stdin, messages[2])
        rename_response = wait_for_response(process.stdout, 1, pending, deadline)
    except (BrokenPipeError, OSError, RuntimeError) as exc:
        failure = RuntimeError(str(exc))
    finally:
        process.stdin.close()
        if process.poll() is None:
            process.terminate()
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=2)

    stderr = b""
    if process.stderr is not None:
        stderr = process.stderr.read()
        process.stderr.close()
    process.stdout.close()

    if failure:
        detail = stderr.decode("utf-8", errors="replace").strip().splitlines()
        suffix = f": {detail[-1]}" if detail else ""
        raise RuntimeError(f"{failure}{suffix}")
    if rename_response is None:
        raise RuntimeError("Codex app-server returned no title-update response")
    rename_error = response_error(rename_response)
    if rename_error:
        raise RuntimeError(rename_error)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--thread-id", default=os.environ.get("CODEX_THREAD_ID"))
    parser.add_argument("--title", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.thread_id:
        print("Thread title update skipped: no Codex thread id.", file=sys.stderr)
        return 2

    try:
        thread_id = validate_thread_id(args.thread_id)
        title = validate_title(args.title)
        set_thread_title(thread_id, title)
    except (ValueError, RuntimeError) as exc:
        print(f"Thread title update failed: {exc}", file=sys.stderr)
        return 1

    print(f"Thread title updated: {title}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
