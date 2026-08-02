#!/usr/bin/env python3
"""Install immutable headless Codex runtime files and merge Claude settings."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shlex
import shutil
import stat
import sys
import tempfile


DEFAULT_LAUNCHER_COMMAND = "~/.local/libexec/dotfiles/run-codex-readonly.sh"
GUARD_LAUNCHER_LITERAL = json.dumps(DEFAULT_LAUNCHER_COMMAND)
RETIRED_RULES = {
    "Bash(~/.claude/skills/headless-agents/scripts/run-codex-readonly.sh:*)",
    f"Bash({DEFAULT_LAUNCHER_COMMAND}:*)",
}
RETIRED_GUARD_COMMANDS = {
    "python3 ~/.claude/hooks/bash-helper-guard.py",
    "python3 ~/.local/libexec/dotfiles/bash-helper-guard.py",
    "/usr/bin/python3 -I ~/.local/libexec/dotfiles/bash-helper-guard.py",
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


def rendered_launcher(
    template: Path, codex: Path, claude: Path, artifact_root: Path
) -> str:
    text = template.read_text()
    replacements = {
        "@CODEX_BIN@": shlex.quote(str(codex)),
        "@CLAUDE_BIN@": shlex.quote(str(claude)),
        "@ARTIFACT_ROOT@": shlex.quote(str(artifact_root)),
        "@ARTIFACT_ROOT_TOML@": json.dumps(str(artifact_root)),
    }
    for marker, value in replacements.items():
        if text.count(marker) != 1:
            raise SystemExit(f"launcher template must contain exactly one {marker}")
        text = text.replace(marker, value)
    return text


def rendered_guard(source: Path, launcher_command: str) -> str:
    text = source.read_text()
    if text.count(GUARD_LAUNCHER_LITERAL) != 1:
        raise SystemExit(
            "guard source must contain exactly one trusted launcher literal"
        )
    return text.replace(GUARD_LAUNCHER_LITERAL, json.dumps(launcher_command))


def merged_settings(
    path: Path, allow_rule: str, guard_command: str, guard_destination: Path
) -> str:
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
        item for item in allow if item != allow_rule and item not in RETIRED_RULES
    ]
    retained.append(allow_rule)
    permissions["allow"] = retained

    hooks = document.setdefault("hooks", {})
    if not isinstance(hooks, dict):
        raise SystemExit("Claude settings hooks must be a JSON object")
    pre_tool_use = hooks.setdefault("PreToolUse", [])
    if not isinstance(pre_tool_use, list):
        raise SystemExit("Claude settings hooks.PreToolUse must be an array")

    for matcher in pre_tool_use:
        if not isinstance(matcher, dict):
            continue
        matcher_hooks = matcher.get("hooks", [])
        if not isinstance(matcher_hooks, list):
            continue
        if matcher.get("matcher") == "Bash":
            def is_managed_guard(hook: object) -> bool:
                if not isinstance(hook, dict) or hook.get("type") != "command":
                    return False
                command = hook.get("command")
                if not isinstance(command, str):
                    return False
                if command == guard_command or command in RETIRED_GUARD_COMMANDS:
                    return True
                try:
                    tokens = shlex.split(command)
                except ValueError:
                    return False
                return bool(tokens) and tokens[-1] == str(guard_destination)

            matcher["hooks"] = [
                hook
                for hook in matcher_hooks
                if not is_managed_guard(hook)
            ]
    pre_tool_use.append(
        {
            "matcher": "Bash",
            "hooks": [{"type": "command", "command": guard_command}],
        }
    )
    return json.dumps(document, indent=2, ensure_ascii=False) + "\n"


def prepare_atomic_write(path: Path, content: str, mode: int) -> Path:
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary_path = Path(temporary)
    try:
        os.fchmod(fd, mode)
        with os.fdopen(fd, "w") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        return temporary_path
    except Exception:
        if temporary_path.exists():
            temporary_path.unlink()
        raise


def reject_symlink_ancestors(path: Path, trusted_root: Path) -> None:
    if trusted_root.is_symlink() or not trusted_root.is_dir():
        raise SystemExit(f"trusted root must be a real directory: {trusted_root}")
    cursor = Path(trusted_root.anchor)
    for component in trusted_root.parts[1:]:
        cursor /= component
        if cursor.is_symlink():
            raise SystemExit(f"trusted root ancestor must not be a symlink: {cursor}")
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


def ensure_trusted_directory(path: Path, trusted_root: Path) -> None:
    reject_symlink_ancestors(path / ".path-check", trusted_root)
    if path.is_symlink() or (path.exists() and not path.is_dir()):
        raise SystemExit(f"trusted directory must be a real directory: {path}")
    path.mkdir(mode=0o700, parents=True, exist_ok=True)
    os.chmod(path, 0o700)
    reject_symlink_ancestors(path / ".path-check", trusted_root)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--settings", type=Path, required=True)
    parser.add_argument("--template", type=Path, required=True)
    parser.add_argument("--launcher", type=Path, required=True)
    parser.add_argument("--launcher-command", required=True)
    parser.add_argument("--guard-source", type=Path, required=True)
    parser.add_argument("--guard-destination", type=Path, required=True)
    parser.add_argument("--artifact-root", type=Path, required=True)
    parser.add_argument("--trusted-root", type=Path, required=True)
    parser.add_argument("--codex-bin")
    parser.add_argument("--claude-bin")
    args = parser.parse_args()

    settings = args.settings.expanduser()
    template = args.template.expanduser().resolve(strict=True)
    launcher = Path(os.path.abspath(args.launcher.expanduser()))
    guard_source = args.guard_source.expanduser().resolve(strict=True)
    guard_destination = Path(os.path.abspath(args.guard_destination.expanduser()))
    artifact_root = Path(os.path.abspath(args.artifact_root.expanduser()))
    trusted_root = Path(os.path.abspath(args.trusted_root.expanduser()))
    if (
        shlex.split(args.launcher_command) != [args.launcher_command]
        or any(character in args.launcher_command for character in "\r\n`;&|<>()")
    ):
        raise SystemExit("launcher command must be one plain executable token")
    launcher_command_path = Path(
        os.path.abspath(Path(args.launcher_command).expanduser())
    )
    if launcher_command_path != launcher:
        raise SystemExit(
            "launcher command must resolve to the installed launcher destination"
        )
    codex = executable("codex", args.codex_bin)
    claude = executable("claude", args.claude_bin)
    python = Path(sys.executable).resolve(strict=True)
    guard_command = (
        f"{shlex.quote(str(python))} -I {shlex.quote(str(guard_destination))}"
    )
    allow_rule = f"Bash({args.launcher_command}:*)"

    settings_text = merged_settings(
        settings, allow_rule, guard_command, guard_destination
    )
    reject_symlink_ancestors(launcher, trusted_root)
    reject_symlink_ancestors(guard_destination, trusted_root)
    ensure_trusted_directory(artifact_root, trusted_root)
    launcher_text = rendered_launcher(template, codex, claude, artifact_root)
    guard_text = rendered_guard(guard_source, args.launcher_command)
    settings_mode = stat.S_IMODE(settings.stat().st_mode)

    settings_temporary = prepare_atomic_write(settings, settings_text, settings_mode)
    try:
        guard_temporary = prepare_atomic_write(guard_destination, guard_text, 0o700)
    except Exception:
        settings_temporary.unlink(missing_ok=True)
        raise
    try:
        launcher_temporary = prepare_atomic_write(launcher, launcher_text, 0o700)
    except Exception:
        settings_temporary.unlink(missing_ok=True)
        guard_temporary.unlink(missing_ok=True)
        raise

    try:
        # All payloads are fully staged before publication. Trusted executable
        # copies go first and settings last, so every partial failure leaves no
        # new permission pointing at a caller-controlled file.
        os.replace(guard_temporary, guard_destination)
        os.replace(launcher_temporary, launcher)
        os.replace(settings_temporary, settings)
    finally:
        settings_temporary.unlink(missing_ok=True)
        guard_temporary.unlink(missing_ok=True)
        launcher_temporary.unlink(missing_ok=True)

    reject_symlink_ancestors(launcher, trusted_root)
    reject_symlink_ancestors(guard_destination, trusted_root)

    if launcher.is_symlink() or not launcher.is_file():
        raise SystemExit(f"launcher postcondition failed: {launcher}")
    if guard_destination.is_symlink() or not guard_destination.is_file():
        raise SystemExit(f"guard postcondition failed: {guard_destination}")
    print(f"  Installed trusted launcher: {launcher}")
    print(f"  Ensured Claude permission: {allow_rule}")
    print(f"  Installed Claude Bash guard: {guard_destination}")


if __name__ == "__main__":
    main()
