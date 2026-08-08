#!/usr/bin/env python3
"""Merge portable settings into Codex's runtime-owned user config."""

from __future__ import annotations

import argparse
import os
import re
import stat
import tempfile
import tomllib
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path


ASSIGNMENT = re.compile(r"^\s*(?P<key>[A-Za-z0-9_-]+)\s*=\s*.+$")
TABLE_HEADER = re.compile(r"^\s*\[(?!\[).+\]\s*(?:#.*)?$")
ARRAY_TABLE_HEADER = re.compile(r"^\s*\[\[.+\]\]\s*(?:#.*)?$")
MARKER = "__codex_portable_config_marker_7f42d7a3__"


@dataclass(frozen=True)
class Setting:
    section: tuple[str, ...]
    header: str | None
    key: str
    line: str


@dataclass(frozen=True)
class Header:
    index: int
    section: tuple[str, ...]
    is_array: bool


def _find_marker(value: object, path: tuple[str, ...] = ()) -> tuple[str, ...] | None:
    if isinstance(value, dict):
        for key, child in value.items():
            if key == MARKER:
                return path
            found = _find_marker(child, (*path, key))
            if found is not None:
                return found
    elif isinstance(value, list):
        for child in value:
            found = _find_marker(child, path)
            if found is not None:
                return found
    return None


def _header_section(line: str) -> tuple[str, ...]:
    parsed = tomllib.loads(f"{line}\n{MARKER} = true\n")
    section = _find_marker(parsed)
    if section is None:
        raise ValueError(f"could not parse TOML table header: {line}")
    return section


def parse_portable_settings(text: str) -> list[Setting]:
    """Parse the deliberately small, one-assignment-per-line overlay format."""
    tomllib.loads(text)
    settings: list[Setting] = []
    section: tuple[str, ...] = ()
    header: str | None = None

    for line_number, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if ARRAY_TABLE_HEADER.match(line):
            raise ValueError(
                f"portable config does not support array tables (line {line_number})"
            )
        if TABLE_HEADER.match(line):
            section = _header_section(line)
            header = stripped
            continue

        match = ASSIGNMENT.match(line)
        if match is None:
            raise ValueError(
                "portable config requires one bare-key assignment per line "
                f"(line {line_number})"
            )
        settings.append(
            Setting(
                section=section,
                header=header,
                key=match.group("key"),
                line=stripped,
            )
        )

    if not settings:
        raise ValueError("portable config does not contain any settings")
    return settings


def _scan_headers(lines: list[str]) -> list[Header]:
    headers: list[Header] = []
    for index, line in enumerate(lines):
        is_array = bool(ARRAY_TABLE_HEADER.match(line))
        if not is_array and not TABLE_HEADER.match(line):
            continue
        try:
            section = _header_section(line)
        except tomllib.TOMLDecodeError:
            # A line inside a multiline value can resemble a table header. It
            # is unrelated to the sections managed by this overlay.
            continue
        headers.append(Header(index=index, section=section, is_array=is_array))
    return headers


def _section_bounds(
    lines: list[str], section: tuple[str, ...]
) -> tuple[int, int] | None:
    headers = _scan_headers(lines)
    if not section:
        return 0, headers[0].index if headers else len(lines)

    for position, header in enumerate(headers):
        if not header.is_array and header.section == section:
            end = headers[position + 1].index if position + 1 < len(headers) else len(lines)
            return header.index + 1, end
    return None


def _upsert_section(
    lines: list[str], section: tuple[str, ...], settings: list[Setting]
) -> list[str]:
    bounds = _section_bounds(lines, section)
    if bounds is None:
        header = settings[0].header
        if header is None:
            raise ValueError("non-root portable setting is missing its table header")
        if lines and lines[-1].strip():
            lines.append("")
        lines.extend([header, *(setting.line for setting in settings)])
        return lines

    start, end = bounds
    missing: list[Setting] = []
    for setting in settings:
        key_pattern = re.compile(rf"^\s*{re.escape(setting.key)}\s*=")
        matches = [
            index for index in range(start, end) if key_pattern.match(lines[index])
        ]
        if len(matches) > 1:
            raise ValueError(
                f"destination contains duplicate {'.'.join((*section, setting.key))}"
            )
        if matches:
            lines[matches[0]] = setting.line
        else:
            missing.append(setting)

    if missing:
        insert_at = end
        while insert_at > start and not lines[insert_at - 1].strip():
            insert_at -= 1
        lines[insert_at:insert_at] = [setting.line for setting in missing]
    return lines


def merge_text(destination_text: str, portable_text: str) -> str:
    tomllib.loads(destination_text)
    grouped: dict[tuple[str, ...], list[Setting]] = defaultdict(list)
    order: list[tuple[str, ...]] = []
    for setting in parse_portable_settings(portable_text):
        if setting.section not in grouped:
            order.append(setting.section)
        grouped[setting.section].append(setting)

    lines = destination_text.splitlines()
    for section in order:
        lines = _upsert_section(lines, section, grouped[section])

    merged = "\n".join(lines).rstrip() + "\n"
    tomllib.loads(merged)
    return merged


def _atomic_write_private(destination: Path, text: str) -> None:
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{destination.name}.", dir=destination.parent
    )
    temporary = Path(temporary_name)
    try:
        os.fchmod(descriptor, 0o600)
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            descriptor = -1
            stream.write(text)
        temporary.replace(destination)
    except BaseException:
        if descriptor >= 0:
            os.close(descriptor)
        temporary.unlink(missing_ok=True)
        raise


def merge_portable_config(portable: Path, destination: Path) -> bool:
    metadata = destination.lstat()
    if not stat.S_ISREG(metadata.st_mode):
        raise RuntimeError(f"Codex config is not a regular file: {destination}")

    destination_text = destination.read_text(encoding="utf-8")
    portable_text = portable.read_text(encoding="utf-8")
    merged = merge_text(destination_text, portable_text)
    if merged == destination_text:
        destination.chmod(0o600)
        return False

    _atomic_write_private(destination, merged)
    return True


def parse_args() -> argparse.Namespace:
    repo_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--portable",
        type=Path,
        default=repo_root / "codex/config.portable.toml",
    )
    parser.add_argument(
        "--destination",
        type=Path,
        default=Path.home() / ".codex/config.toml",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    changed = merge_portable_config(args.portable, args.destination)
    state = "Updated" if changed else "Already current"
    print(f"  {state}: {args.destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
