#!/usr/bin/env python3
"""Queue one validated Codex thread-title request for the Stop hook to apply."""

from __future__ import annotations

import argparse
import json
import os
import stat
import sys
import tempfile
from pathlib import Path

from set_thread_title import validate_thread_id, validate_title


REQUEST_ROOT = Path(tempfile.gettempdir()) / f"codex-thread-title-requests-{os.getuid()}"


def request_directory() -> Path:
    REQUEST_ROOT.mkdir(mode=0o700, parents=False, exist_ok=True)
    metadata = REQUEST_ROOT.lstat()
    if not stat.S_ISDIR(metadata.st_mode) or metadata.st_uid != os.getuid():
        raise RuntimeError("thread-title request directory is not owned by this user")
    if stat.S_IMODE(metadata.st_mode) != 0o700:
        REQUEST_ROOT.chmod(0o700)
    return REQUEST_ROOT


def request_path(thread_id: str) -> Path:
    return request_directory() / f"{validate_thread_id(thread_id)}.json"


def clear_title_request(thread_id: str) -> None:
    request_path(thread_id).unlink(missing_ok=True)


def queue_title_request(thread_id: str, title: str) -> None:
    thread_id = validate_thread_id(thread_id)
    title = validate_title(title)
    directory = request_directory()
    destination = directory / f"{thread_id}.json"
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{thread_id}.", dir=directory)
    temporary = Path(temporary_name)
    try:
        os.fchmod(descriptor, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            descriptor = -1
            json.dump({"thread_id": thread_id, "title": title}, stream, ensure_ascii=False)
            stream.write("\n")
        temporary.replace(destination)
    except BaseException:
        if descriptor >= 0:
            os.close(descriptor)
        temporary.unlink(missing_ok=True)
        raise


def take_title_request(thread_id: str) -> tuple[str, str] | None:
    thread_id = validate_thread_id(thread_id)
    path = request_path(thread_id)
    try:
        metadata = path.lstat()
    except FileNotFoundError:
        return None
    if not stat.S_ISREG(metadata.st_mode) or metadata.st_uid != os.getuid():
        raise RuntimeError("thread-title request file is unsafe")

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    finally:
        path.unlink(missing_ok=True)
    if not isinstance(payload, dict):
        raise RuntimeError("thread-title request is invalid")
    queued_thread_id = validate_thread_id(str(payload.get("thread_id") or ""))
    if queued_thread_id != thread_id:
        raise RuntimeError("thread-title request targets another thread")
    title = validate_title(str(payload.get("title") or ""))
    return queued_thread_id, title


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--thread-id", default=os.environ.get("CODEX_THREAD_ID"))
    parser.add_argument("--title", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.thread_id:
        print("Thread title request skipped: no Codex thread id.", file=sys.stderr)
        return 2
    try:
        queue_title_request(args.thread_id, args.title)
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"Thread title request failed: {exc}", file=sys.stderr)
        return 1
    print(f"Thread title requested: {args.title}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
