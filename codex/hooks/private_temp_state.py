"""Private, atomic temp-state primitives shared by Codex hooks."""

from __future__ import annotations

import os
import stat
import tempfile
from pathlib import Path


def ensure_private_directory(root: Path) -> Path:
    root.mkdir(mode=0o700, parents=False, exist_ok=True)
    metadata = root.lstat()
    if not stat.S_ISDIR(metadata.st_mode) or metadata.st_uid != os.getuid():
        raise RuntimeError("hook state directory is not owned by this user")
    if stat.S_IMODE(metadata.st_mode) != 0o700:
        root.chmod(0o700)
        metadata = root.lstat()
        if stat.S_IMODE(metadata.st_mode) != 0o700:
            raise RuntimeError("hook state directory is not private")
    return root


def validate_private_file(path: Path) -> os.stat_result:
    metadata = path.lstat()
    if not stat.S_ISREG(metadata.st_mode) or metadata.st_uid != os.getuid():
        raise RuntimeError("hook state file is unsafe")
    if stat.S_IMODE(metadata.st_mode) & 0o077:
        raise RuntimeError("hook state file is not private")
    return metadata


def read_private_text(path: Path) -> str | None:
    ensure_private_directory(path.parent)
    try:
        validate_private_file(path)
    except FileNotFoundError:
        return None
    return path.read_text(encoding="utf-8")


def atomic_write_private(path: Path, text: str) -> None:
    directory = ensure_private_directory(path.parent)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=directory)
    temporary = Path(temporary_name)
    try:
        os.fchmod(descriptor, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            descriptor = -1
            stream.write(text)
        temporary.replace(path)
    except BaseException:
        if descriptor >= 0:
            os.close(descriptor)
        temporary.unlink(missing_ok=True)
        raise
