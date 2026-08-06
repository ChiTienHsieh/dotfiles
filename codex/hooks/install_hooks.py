#!/usr/bin/env python3
"""Merge dotfiles-owned Codex hooks into the live hooks.json safely."""

from __future__ import annotations

import json
import os
import stat
import sys
import tempfile
from json import JSONDecodeError
from pathlib import Path


MANAGED_COMMAND = '/usr/bin/python3 "$HOME/.codex/bin/track_tmux_workers.py"'
HANDLER_TYPES = {"command", "prompt", "agent"}
TOP_LEVEL_FIELDS = {"description", "hooks"}
STRING_HANDLER_FIELDS = {"commandWindows", "command_windows", "statusMessage"}
INTEGER_HANDLER_FIELDS = {"timeout", "additionalContextLimit"}


class HookConfigError(ValueError):
    pass


def load_json(path: Path, *, missing_ok: bool = False) -> dict[str, object]:
    if missing_ok and not path.exists():
        return {"hooks": {}}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise HookConfigError(f"hook config not found: {path}") from exc
    except JSONDecodeError as exc:
        raise HookConfigError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(data, dict) or not isinstance(data.get("hooks"), dict):
        raise HookConfigError(f"expected a top-level hooks object in {path}")
    return data


def validate_hook_structure(config: dict[str, object], label: str) -> None:
    unknown_top_level = set(config) - TOP_LEVEL_FIELDS
    if unknown_top_level:
        raise HookConfigError(
            f"unsupported top-level fields in {label}: {sorted(unknown_top_level)}"
        )
    description = config.get("description")
    if description is not None and not isinstance(description, str):
        raise HookConfigError(f"hook description in {label} must be a string")
    hooks = config.get("hooks")
    if not isinstance(hooks, dict):
        raise HookConfigError(f"expected a top-level hooks object in {label}")
    for event, groups in hooks.items():
        if not isinstance(event, str) or not isinstance(groups, list):
            raise HookConfigError(f"hook event {event!r} in {label} must be a list")
        for group in groups:
            if not isinstance(group, dict) or not isinstance(group.get("hooks"), list):
                raise HookConfigError(f"hook groups for {event!r} in {label} are malformed")
            matcher = group.get("matcher")
            if matcher is not None and not isinstance(matcher, str):
                raise HookConfigError(f"hook matcher for {event!r} in {label} must be a string")
            for item in group["hooks"]:
                if not isinstance(item, dict) or item.get("type") not in HANDLER_TYPES:
                    raise HookConfigError(f"hook handler for {event!r} in {label} is malformed")
                if item["type"] == "command" and not isinstance(item.get("command"), str):
                    raise HookConfigError(
                        f"command hook for {event!r} in {label} has no command string"
                    )
                for field in STRING_HANDLER_FIELDS:
                    value = item.get(field)
                    if value is not None and not isinstance(value, str):
                        raise HookConfigError(
                            f"{field} for {event!r} in {label} must be a string"
                        )
                for field in INTEGER_HANDLER_FIELDS:
                    value = item.get(field)
                    if value is not None and (
                        isinstance(value, bool)
                        or not isinstance(value, int)
                        or value < 0
                    ):
                        raise HookConfigError(
                            f"{field} for {event!r} in {label} must be a non-negative integer"
                        )
                async_value = item.get("async")
                if async_value is not None and not isinstance(async_value, bool):
                    raise HookConfigError(
                        f"async for {event!r} in {label} must be a boolean"
                    )


def is_managed_hook(item: object) -> bool:
    return (
        isinstance(item, dict)
        and item.get("type") == "command"
        and item.get("command") == MANAGED_COMMAND
    )


def strip_managed_groups(config: dict[str, object]) -> None:
    hooks = config["hooks"]
    assert isinstance(hooks, dict)
    for event, raw_groups in list(hooks.items()):
        if not isinstance(raw_groups, list):
            continue
        kept_groups: list[object] = []
        for raw_group in raw_groups:
            if not isinstance(raw_group, dict):
                kept_groups.append(raw_group)
                continue
            raw_items = raw_group.get("hooks")
            if not isinstance(raw_items, list):
                kept_groups.append(raw_group)
                continue
            group = dict(raw_group)
            group["hooks"] = [item for item in raw_items if not is_managed_hook(item)]
            if group["hooks"]:
                kept_groups.append(group)
        if kept_groups:
            hooks[event] = kept_groups
        else:
            hooks.pop(event, None)


def validate_manifest(manifest: dict[str, object]) -> None:
    validate_hook_structure(manifest, "managed hook manifest")
    hooks = manifest["hooks"]
    assert isinstance(hooks, dict)
    managed_count = 0
    for raw_groups in hooks.values():
        if not isinstance(raw_groups, list):
            raise HookConfigError("manifest hook events must contain group lists")
        for raw_group in raw_groups:
            if not isinstance(raw_group, dict) or not isinstance(raw_group.get("hooks"), list):
                raise HookConfigError("manifest hook groups must contain hook lists")
            for item in raw_group["hooks"]:
                if not is_managed_hook(item):
                    raise HookConfigError("manifest contains an unmanaged hook command")
                managed_count += 1
    if managed_count == 0:
        raise HookConfigError("manifest contains no managed hooks")


def merge_hooks(
    live: dict[str, object], manifest: dict[str, object]
) -> dict[str, object]:
    validate_hook_structure(live, "live hooks config")
    validate_manifest(manifest)
    merged = json.loads(json.dumps(live))
    strip_managed_groups(merged)

    merged_hooks = merged["hooks"]
    manifest_hooks = manifest["hooks"]
    assert isinstance(merged_hooks, dict)
    assert isinstance(manifest_hooks, dict)
    for event, groups in manifest_hooks.items():
        assert isinstance(groups, list)
        merged_hooks.setdefault(event, [])
        if not isinstance(merged_hooks[event], list):
            raise HookConfigError(f"live hook event {event!r} is not a list")
        merged_hooks[event].extend(json.loads(json.dumps(groups)))
    return merged


def write_atomic(path: Path, config: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = stat.S_IMODE(path.stat().st_mode) if path.exists() else 0o600
    temp_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent, delete=False
        ) as handle:
            temp_name = handle.name
            json.dump(config, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
        os.chmod(temp_name, mode)
        os.replace(temp_name, path)
    finally:
        if temp_name:
            try:
                Path(temp_name).unlink(missing_ok=True)
            except OSError:
                pass


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(f"usage: {argv[0]} MANIFEST LIVE_HOOKS_JSON", file=sys.stderr)
        return 2
    manifest_path = Path(argv[1]).expanduser()
    live_path = Path(argv[2]).expanduser()
    try:
        manifest = load_json(manifest_path)
        live = load_json(live_path, missing_ok=True)
        merged = merge_hooks(live, manifest)
        if merged == live:
            print(f"  Codex hooks already current: {live_path}")
            return 0
        write_atomic(live_path, merged)
    except (HookConfigError, OSError) as exc:
        print(f"install_hooks.py: {exc}", file=sys.stderr)
        return 1
    print(f"  Configured Codex hooks: {live_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
