#!/usr/bin/env python3
"""Manage one private data-file handoff for a Codex thread-title request."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

from private_temp_state import (
    atomic_write_private,
    ensure_private_directory,
    read_private_text,
)
from set_thread_title import validate_thread_id, validate_title


REQUEST_ROOT = Path(tempfile.gettempdir()) / f"codex-thread-title-requests-{os.getuid()}"
NO_TITLE_REQUEST = "NO_TITLE_REQUEST\n"


def request_directory() -> Path:
    return ensure_private_directory(REQUEST_ROOT)


def request_path(thread_id: str) -> Path:
    return request_directory() / f"{validate_thread_id(thread_id)}.txt"


def prepare_title_request(thread_id: str) -> Path:
    thread_id = validate_thread_id(thread_id)
    directory = request_directory()
    destination = directory / f"{thread_id}.txt"
    atomic_write_private(destination, NO_TITLE_REQUEST)
    return destination


def take_title_request(thread_id: str) -> tuple[str, str] | None:
    thread_id = validate_thread_id(thread_id)
    path = request_path(thread_id)
    try:
        content = read_private_text(path)
    finally:
        path.unlink(missing_ok=True)
    if content is None:
        return None
    if content == NO_TITLE_REQUEST:
        return None
    if content.endswith("\n"):
        content = content[:-1]
    return thread_id, validate_title(content)
