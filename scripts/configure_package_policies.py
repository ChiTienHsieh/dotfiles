#!/usr/bin/env python3
"""Install package release-age policies without linking credential stores."""

from __future__ import annotations

import argparse
import os
import re
import stat
import sys
import tempfile
import tomllib
from collections.abc import Callable, Mapping
from dataclasses import dataclass, replace
from pathlib import Path


Destination = Callable[[Path, str, Mapping[str, str]], Path]


def in_home(relative: str) -> Destination:
    return lambda home, _platform, _env: home / relative


def pnpm_config_dir(home: Path, platform: str, env: Mapping[str, str]) -> Path:
    """Mirror pnpm's global config directory on macOS and Linux; no Windows.

    pnpm 10 reads minimum-release-age from rc here; pnpm 11+ reads
    minimumReleaseAge from config.yaml in the same directory. An empty
    XDG_CONFIG_HOME counts as unset, as in pnpm 10 and 11 (pnpm 12 would use
    a relative pnpm/ directory instead).
    """
    if env.get("XDG_CONFIG_HOME"):
        return Path(env["XDG_CONFIG_HOME"]) / "pnpm"
    if platform == "darwin":
        return home / "Library/Preferences/pnpm"
    return home / ".config/pnpm"


def in_pnpm_config_dir(name: str) -> Destination:
    return lambda home, platform, env: pnpm_config_dir(home, platform, env) / name


@dataclass(frozen=True)
class Policy:
    # None: no seed file; a missing destination starts out empty.
    source: str | None
    destination: Destination
    kind: str
    key: str
    value: str
    comment: str
    section: str | None = None


PNPM_RC_POLICY = Policy(
    source="pnpm/.config/pnpm/rc",
    destination=in_pnpm_config_dir("rc"),
    kind="key-value",
    key="minimum-release-age",
    value="10080",
    comment="# pnpm expresses minimumReleaseAge in minutes: 7 days = 10,080 minutes.",
)

POLICIES = (
    Policy(
        source="bun/.bunfig.toml",
        destination=in_home(".bunfig.toml"),
        kind="toml",
        section="install",
        key="minimumReleaseAge",
        value="604800",
        comment="# Delay new npm package releases for seven days to reduce supply-chain risk.",
    ),
    Policy(
        source="npm/.npmrc",
        destination=in_home(".npmrc"),
        kind="key-value",
        key="min-release-age",
        value="7",
        comment="# Delay new package releases for seven days to reduce supply-chain risk.",
    ),
    PNPM_RC_POLICY,
    # pnpm 11+ ignores rc; it reads the same minutes, in camelCase, from config.yaml.
    replace(
        PNPM_RC_POLICY,
        source=None,
        destination=in_pnpm_config_dir("config.yaml"),
        kind="yaml",
        key="minimumReleaseAge",
    ),
)

YAML_SEQUENCE_ENTRY = re.compile(r"^-(?:\s|$)")
YAML_ANCHOR = re.compile(r"(?:^|[\s\[{,])&[^\s\[\]{},]")
YAML_TOP_LEVEL_KEY = re.compile(
    r"""^(?:"[^"]*"|'[^']*'|[^\s#"'\[\]{},&*!|>%@`?:-][^#]*?)\s*:(?:\s|$)"""
)


def seed_text(source: Path | None) -> str:
    return "" if source is None else source.read_text(encoding="utf-8")


def existing_or_seed_text(destination: Path, source: Path | None) -> str:
    try:
        metadata = destination.lstat()
    except FileNotFoundError:
        return seed_text(source)

    if stat.S_ISLNK(metadata.st_mode):
        if not destination.exists():
            return seed_text(source)
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


def upsert_yaml(text: str, policy: Policy) -> str:
    """Set one top-level key in a YAML file without a YAML library.

    Only a block mapping that starts at column 0 is supported: `key: value`
    lines, comments and blank lines. Indented lines and `- item` lines belong
    to the key above them and are dropped along with the old value. Anything
    else, such as `{...}`, `---`, an indented top level or an anchor on the
    old value (an alias elsewhere may point at it), raises ValueError rather
    than risk a broken file. Nested keys with the same name are left
    alone, and the value is written as is, so it must be a plain scalar.
    A leading byte order mark is dropped so that a key on the first line
    still matches.
    """
    text = text.removeprefix("\ufeff")
    key_name = re.escape(policy.key)
    key_pattern = re.compile(
        rf"""^(?:{key_name}|"{key_name}"|'{key_name}')\s*:(?:\s|$)"""
    )
    output: list[str] = []
    found = False
    in_mapping = False
    dropping_value = False
    for line in text.splitlines():
        content = line.lstrip()
        if not content or content.startswith("#"):
            output.append(line)
            continue
        if line[0].isspace() or YAML_SEQUENCE_ENTRY.match(line):
            if not in_mapping:
                raise ValueError("YAML top level is not a block mapping at column 0")
            if not dropping_value:
                output.append(line)
            elif YAML_ANCHOR.search(line):
                raise ValueError(f"the old {policy.key} value defines a YAML anchor")
            continue
        if not YAML_TOP_LEVEL_KEY.match(line):
            raise ValueError("YAML top level has a line that is not a simple key")
        in_mapping = True
        key_match = key_pattern.match(line)
        dropping_value = key_match is not None
        if not dropping_value:
            output.append(line)
            continue
        if YAML_ANCHOR.search(line[key_match.end():]):
            raise ValueError(f"the old {policy.key} value defines a YAML anchor")
        if not found:
            output.append(f"{policy.key}: {policy.value}")
            found = True

    if not found:
        if output and output[-1].strip():
            output.append("")
        output.extend((policy.comment, f"{policy.key}: {policy.value}"))
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


def configure_package_policies(
    home: Path,
    repo_root: Path,
    platform: str = sys.platform,
    env: Mapping[str, str] = os.environ,
) -> list[Path]:
    configured: list[Path] = []
    for policy in POLICIES:
        source = None if policy.source is None else repo_root / policy.source
        destination = policy.destination(home, platform, env)
        text = existing_or_seed_text(destination, source)
        if policy.kind == "key-value":
            text = upsert_key_value(text, policy)
        elif policy.kind == "toml":
            text = upsert_toml(text, policy)
        elif policy.kind == "yaml":
            try:
                text = upsert_yaml(text, policy)
            except ValueError as error:
                raise RuntimeError(
                    f"{error}; set {policy.key}: {policy.value} by hand in {destination}"
                ) from error
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
