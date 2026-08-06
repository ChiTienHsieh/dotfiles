#!/usr/bin/env python3
"""Install package release-age policies without linking credential stores."""

from __future__ import annotations

import argparse
import os
import re
import stat
import tempfile
from dataclasses import dataclass
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # Python < 3.11; install.sh also supports older macOS.
    tomllib = None


@dataclass(frozen=True)
class Policy:
    source: str
    destination: str
    kind: str
    key: str
    value: str
    comment: str
    section: str | None = None


POLICIES = (
    Policy(
        source="bun/.bunfig.toml",
        destination=".bunfig.toml",
        kind="toml",
        section="install",
        key="minimumReleaseAge",
        value="604800",
        comment="# Delay new npm package releases for seven days to reduce supply-chain risk.",
    ),
    Policy(
        source="npm/.npmrc",
        destination=".npmrc",
        kind="key-value",
        key="min-release-age",
        value="7",
        comment="# Delay new package releases for seven days to reduce supply-chain risk.",
    ),
    Policy(
        source="pnpm/.config/pnpm/rc",
        destination=".config/pnpm/rc",
        kind="key-value",
        key="minimum-release-age",
        value="10080",
        comment="# pnpm expresses minimumReleaseAge in minutes: 7 days = 10,080 minutes.",
    ),
)


def existing_or_seed_text(destination: Path, source: Path) -> str:
    try:
        metadata = destination.lstat()
    except FileNotFoundError:
        return source.read_text(encoding="utf-8")

    if stat.S_ISLNK(metadata.st_mode):
        if not destination.exists():
            return source.read_text(encoding="utf-8")
        target_metadata = destination.stat()
        if not stat.S_ISREG(target_metadata.st_mode):
            raise RuntimeError(f"package config symlink target is not a file: {destination}")
        return destination.read_text(encoding="utf-8")
    if not stat.S_ISREG(metadata.st_mode):
        raise RuntimeError(f"package config is not a regular file: {destination}")
    return destination.read_text(encoding="utf-8")


def upsert_key_value(text: str, policy: Policy) -> str:
    pattern = re.compile(rf"^\s*{re.escape(policy.key)}\s*=.*$")
    output: list[str] = []
    found = False
    for line in text.splitlines():
        if pattern.match(line):
            if not found:
                output.append(f"{policy.key}={policy.value}")
                found = True
            continue
        output.append(line)

    if not found:
        if output and output[-1].strip():
            output.append("")
        output.extend((policy.comment, f"{policy.key}={policy.value}"))
    return "\n".join(output).rstrip() + "\n"


def upsert_toml(text: str, policy: Policy) -> str:
    if policy.section is None:
        raise RuntimeError("TOML policy requires a section")

    lines = text.splitlines()
    section_name = re.escape(policy.section)
    section_key = rf'(?:{section_name}|"{section_name}"|\'{section_name}\')'
    section_pattern = re.compile(
        rf"^\s*\[\s*{section_key}\s*\]\s*(?:#.*)?$"
    )
    child_pattern = re.compile(rf"^\s*\[\s*{section_key}\s*\.")
    header_pattern = re.compile(r"^\s*\[\[?")
    key_name = re.escape(policy.key)
    key_pattern = re.compile(
        rf'^\s*(?:{key_name}|"{key_name}"|\'{key_name}\')\s*=.*$'
    )

    section_start = next(
        (index for index, line in enumerate(lines) if section_pattern.match(line)),
        None,
    )
    if section_start is None:
        insert_at = next(
            (index for index, line in enumerate(lines) if child_pattern.match(line)),
            len(lines),
        )
        block = [
            f"[{policy.section}]",
            policy.comment,
            f"{policy.key} = {policy.value}",
            "",
        ]
        if insert_at == len(lines) and lines and lines[-1].strip():
            block.insert(0, "")
        lines[insert_at:insert_at] = block
    else:
        section_end = next(
            (
                index
                for index in range(section_start + 1, len(lines))
                if header_pattern.match(lines[index])
            ),
            len(lines),
        )
        found = False
        rewritten: list[str] = []
        for index, line in enumerate(lines):
            if section_start < index < section_end and key_pattern.match(line):
                if not found:
                    rewritten.append(f"{policy.key} = {policy.value}")
                    found = True
                continue
            rewritten.append(line)
        lines = rewritten
        if not found:
            lines[section_start + 1 : section_start + 1] = [
                policy.comment,
                f"{policy.key} = {policy.value}",
            ]

    result = "\n".join(lines).rstrip() + "\n"
    if tomllib is not None:
        tomllib.loads(result)
    return result


def atomic_write_private(destination: Path, text: str) -> None:
    destination.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
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


def configure_package_policies(home: Path, repo_root: Path) -> list[Path]:
    configured: list[Path] = []
    for policy in POLICIES:
        source = repo_root / policy.source
        destination = home / policy.destination
        text = existing_or_seed_text(destination, source)
        if policy.kind == "key-value":
            text = upsert_key_value(text, policy)
        elif policy.kind == "toml":
            text = upsert_toml(text, policy)
        else:
            raise RuntimeError(f"unknown package policy kind: {policy.kind}")
        atomic_write_private(destination, text)
        configured.append(destination)
    return configured


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--home", type=Path, default=Path.home())
    parser.add_argument(
        "--repo-root", type=Path, default=Path(__file__).resolve().parents[1]
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    for path in configure_package_policies(args.home, args.repo_root):
        print(f"  Configured local package policy: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
