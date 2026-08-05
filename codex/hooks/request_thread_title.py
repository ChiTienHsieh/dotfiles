#!/usr/bin/env python3
"""Manage one private data-file handoff for a Codex thread-title request."""

from __future__ import annotations

import os
import stat
import tempfile
from pathlib import Path

from set_thread_title import validate_thread_id, validate_title


REQUEST_ROOT = Path(tempfile.gettempdir()) / f"codex-thread-title-requests-{os.getuid()}"
NO_TITLE_REQUEST = "NO_TITLE_REQUEST\n"


def request_directory() -> Path:
    REQUEST_ROOT.mkdir(mode=0o700, parents=False, exist_ok=True)
    metadata = REQUEST_ROOT.lstat()
    if not stat.S_ISDIR(metadata.st_mode) or metadata.st_uid != os.getuid():
        raise RuntimeError("thread-title request directory is not owned by this user")
    if stat.S_IMODE(metadata.st_mode) != 0o700:
        REQUEST_ROOT.chmod(0o700)
    return REQUEST_ROOT


def request_path(thread_id: str) -> Path:
    return request_directory() / f"{validate_thread_id(thread_id)}.txt"


def prepare_title_request(thread_id: str) -> Path:
    thread_id = validate_thread_id(thread_id)
    directory = request_directory()
    destination = directory / f"{thread_id}.txt"
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{thread_id}.", dir=directory)
    temporary = Path(temporary_name)
    try:
        os.fchmod(descriptor, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            descriptor = -1
            stream.write(NO_TITLE_REQUEST)
        temporary.replace(destination)
    except BaseException:
        if descriptor >= 0:
            os.close(descriptor)
        temporary.unlink(missing_ok=True)
        raise
    return destination


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
        content = path.read_text(encoding="utf-8")
    finally:
        path.unlink(missing_ok=True)
    if content == NO_TITLE_REQUEST:
        return None
    if content.endswith("\n"):
        content = content[:-1]
    return thread_id, validate_title(content)
