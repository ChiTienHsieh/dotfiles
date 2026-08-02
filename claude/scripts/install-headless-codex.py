#!/usr/bin/env python3
"""Install the immutable headless Codex launcher and merge its Claude rule."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shlex
import shutil
import stat
import tempfile


ALLOW_RULE = "Bash(~/.local/libexec/dotfiles/run-codex-readonly.sh:*)"
RETIRED_RULES = {
    "Bash(~/.claude/skills/headless-agents/scripts/run-codex-readonly.sh:*)",
}


def executable(name: str, override: str | None) -> Path:
    candidate = override or shutil.which(name)
    if not candidate:
        raise SystemExit(f"required executable not found: {name}")
    resolved = Path(candidate).expanduser().resolve(strict=True)
    mode = resolved.stat().st_mode
    if not stat.S_ISREG(mode) or not os.access(resolved, os.X_OK):
        raise SystemExit(f"not an executable regular file: {resolved}")
    return resolved


def rendered_launcher(template: Path, codex: Path, claude: Path) -> str:
    text = template.read_text()
    replacements = {
        "@CODEX_BIN@": shlex.quote(str(codex)),
        "@CLAUDE_BIN@": shlex.quote(str(claude)),
    }
    for marker, value in replacements.items():
        if text.count(marker) != 1:
            raise SystemExit(f"launcher template must contain exactly one {marker}")
        text = text.replace(marker, value)
    return text


def merged_settings(path: Path) -> str:
    try:
        document = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"cannot parse Claude settings {path}: {exc}") from exc
    if not isinstance(document, dict):
        raise SystemExit("Claude settings root must be a JSON object")

    permissions = document.setdefault("permissions", {})
    if not isinstance(permissions, dict):
        raise SystemExit("Claude settings permissions must be a JSON object")
    allow = permissions.setdefault("allow", [])
    if not isinstance(allow, list) or not all(isinstance(item, str) for item in allow):
        raise SystemExit("Claude settings permissions.allow must be a string array")

    retained = [
        item for item in allow if item != ALLOW_RULE and item not in RETIRED_RULES
    ]
    retained.append(ALLOW_RULE)
    permissions["allow"] = retained
    return json.dumps(document, indent=2, ensure_ascii=False) + "\n"


def atomic_write(path: Path, content: str, mode: int) -> None:
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary_path = Path(temporary)
    try:
        os.fchmod(fd, mode)
        with os.fdopen(fd, "w") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
    finally:
        if temporary_path.exists():
            temporary_path.unlink()


def reject_symlink_ancestors(path: Path, trusted_root: Path) -> None:
    try:
        relative_parent = path.parent.relative_to(trusted_root)
    except ValueError as exc:
        raise SystemExit(
            f"launcher must stay under trusted root {trusted_root}: {path}"
        ) from exc

    cursor = trusted_root
    for component in relative_parent.parts:
        cursor /= component
        if cursor.is_symlink():
            raise SystemExit(f"launcher parent must not be a symlink: {cursor}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--settings", type=Path, required=True)
    parser.add_argument("--template", type=Path, required=True)
    parser.add_argument("--launcher", type=Path, required=True)
    parser.add_argument("--trusted-root", type=Path, required=True)
    parser.add_argument("--codex-bin")
    parser.add_argument("--claude-bin")
    args = parser.parse_args()

    settings = args.settings.expanduser()
    template = args.template.expanduser().resolve(strict=True)
    launcher = args.launcher.expanduser().absolute()
    trusted_root = args.trusted_root.expanduser().absolute()
    codex = executable("codex", args.codex_bin)
    claude = executable("claude", args.claude_bin)

    settings_text = merged_settings(settings)
    launcher_text = rendered_launcher(template, codex, claude)
    settings_mode = stat.S_IMODE(settings.stat().st_mode)

    reject_symlink_ancestors(launcher, trusted_root)
    atomic_write(launcher, launcher_text, 0o700)
    reject_symlink_ancestors(launcher, trusted_root)
    atomic_write(settings, settings_text, settings_mode)

    if launcher.is_symlink() or not launcher.is_file():
        raise SystemExit(f"launcher postcondition failed: {launcher}")
    print(f"  Installed trusted launcher: {launcher}")
    print(f"  Ensured Claude permission: {ALLOW_RULE}")


if __name__ == "__main__":
    main()
