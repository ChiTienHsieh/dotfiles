#!/usr/bin/env python3
"""Prompt Codex to offer cleanup options before ending with a dirty worktree."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import time
from json import JSONDecodeError
from pathlib import Path

TRACK_DIR = Path(tempfile.gettempdir()) / "codex-dirty-worktrees"


def run_git(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(cwd), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        timeout=5,
        check=False,
    )


def git_root_for_path(path: Path) -> Path | None:
    candidates = [path]
    if not path.exists() or path.is_file():
        candidates.append(path.parent)

    for candidate in candidates:
        proc = run_git(candidate, "rev-parse", "--show-toplevel")
        if proc.returncode == 0:
            root = proc.stdout.strip()
            if root:
                return Path(root)
    return None


def session_track_path(session_id: object) -> Path | None:
    if not isinstance(session_id, str) or not session_id:
        return None
    safe_id = re.sub(r"[^A-Za-z0-9_.-]", "_", session_id)
    return TRACK_DIR / f"{safe_id}.json"


def load_tracked_roots(session_id: object) -> set[Path]:
    path = session_track_path(session_id)
    if not path or not path.exists():
        return set()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, JSONDecodeError):
        return set()
    roots = data.get("roots") if isinstance(data, dict) else None
    if not isinstance(roots, list):
        return set()
    return {Path(root) for root in roots if isinstance(root, str) and root}


def save_tracked_roots(session_id: object, roots: set[Path]) -> None:
    path = session_track_path(session_id)
    if not path:
        return
    try:
        TRACK_DIR.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps({"roots": sorted(str(root) for root in roots)}, indent=2) + "\n",
            encoding="utf-8",
        )
    except OSError:
        return


def recent_track_paths(hours: float = 12) -> list[Path]:
    try:
        paths = list(TRACK_DIR.glob("*.json"))
    except OSError:
        return []

    cutoff = time.time() - (hours * 60 * 60)
    recent: list[Path] = []
    for path in paths:
        try:
            if path.stat().st_mtime >= cutoff:
                recent.append(path)
        except OSError:
            continue
    return sorted(recent, key=lambda path: path.stat().st_mtime, reverse=True)


def load_roots_from_track_path(path: Path) -> set[Path]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, JSONDecodeError):
        return set()
    roots = data.get("roots") if isinstance(data, dict) else None
    if not isinstance(roots, list):
        return set()
    return {Path(root) for root in roots if isinstance(root, str) and root}


def dirty_roots_for(roots: set[Path]) -> list[tuple[Path, list[str]]]:
    dirty_roots: list[tuple[Path, list[str]]] = []
    for root in sorted(roots):
        status_proc = run_git(root, "status", "--porcelain=v1", "--untracked-files=normal")
        if status_proc.returncode != 0:
            continue
        status_lines = [line for line in status_proc.stdout.splitlines() if line.strip()]
        if status_lines:
            dirty_roots.append((root, status_lines))
    return dirty_roots


def print_dirty_report(cwd: Path, recent_hours: float = 12) -> int:
    roots: set[Path] = set()
    cwd_root = git_root_for_path(cwd)
    if cwd_root:
        roots.add(cwd_root)

    for path in recent_track_paths(recent_hours):
        roots.update(load_roots_from_track_path(path))

    dirty_roots = dirty_roots_for(roots)
    if not dirty_roots:
        print("Dirty worktree check: clean.")
        return 0

    print("Dirty worktree check: dirty repositories found.")
    for root, status_lines in dirty_roots:
        print(f"\nRepository: {root}")
        for line in status_lines[:30]:
            print(line)
        omitted = len(status_lines) - 30
        if omitted > 0:
            print(f"... and {omitted} more path(s)")
    return 0


def absolute_paths_in(value: object) -> set[Path]:
    try:
        text = json.dumps(value, ensure_ascii=False)
    except TypeError:
        text = str(value)

    paths: set[Path] = set()
    for match in re.finditer(r"/Users/[^\s\"'`<>|;&{}()\[\]]+", text):
        raw = match.group(0).rstrip(",:.")
        paths.add(Path(raw))
    return paths


def track_touched_worktrees(payload: dict[str, object]) -> None:
    roots = load_tracked_roots(payload.get("session_id"))

    cwd = Path(str(payload.get("cwd") or ".")).expanduser()
    cwd_root = git_root_for_path(cwd)
    if cwd_root:
        roots.add(cwd_root)

    for path in absolute_paths_in(payload.get("tool_input")):
        root = git_root_for_path(path)
        if root:
            roots.add(root)

    save_tracked_roots(payload.get("session_id"), roots)


def record_touched_worktrees(payload: dict[str, object]) -> int:
    track_touched_worktrees(payload)
    return emit({"continue": True})


def already_offered_cleanup(message: str | None) -> bool:
    if not message:
        return False

    lowered = message.lower()
    mentions_dirty = any(
        marker in lowered
        for marker in (
            "dirty worktree",
            "dirty working tree",
            "worktree is dirty",
            "working tree is dirty",
            "未提交",
            "未整理",
            "未清",
        )
    )
    offers_escape_hatch = any(
        marker in lowered
        for marker in (
            "keep dirty",
            "ignore for now",
            "leave it dirty",
            "保留 dirty",
            "先保留",
            "暫時保留",
            "先不整理",
        )
    )
    offers_cleanup = any(
        marker in lowered
        for marker in ("commit", "stash", "stage", "整理", "提交", "暫存")
    )
    return mentions_dirty and offers_escape_hatch and offers_cleanup


def looks_like_level_up_checkpoint(message: str | None) -> bool:
    if not message:
        return False

    return (
        "Level " in message
        and "**問題:" in message
        and all(marker in message for marker in ("A)", "B)", "C)", "D)"))
    )


def emit(payload: dict[str, object]) -> int:
    print(json.dumps(payload, ensure_ascii=False))
    return 0


def build_dirty_worktree_followup(payload: dict[str, object]) -> str | None:
    if already_offered_cleanup(payload.get("last_assistant_message")):
        return None

    if looks_like_level_up_checkpoint(payload.get("last_assistant_message")):
        return None

    roots = load_tracked_roots(payload.get("session_id"))
    cwd = Path(str(payload.get("cwd") or ".")).expanduser()
    cwd_root = git_root_for_path(cwd)
    if cwd_root:
        roots.add(cwd_root)

    dirty_roots = dirty_roots_for(roots)
    if not dirty_roots:
        return None

    sections: list[str] = []
    for root, status_lines in dirty_roots[:5]:
        shown = "\n".join(status_lines[:30])
        omitted = len(status_lines) - 30
        if omitted > 0:
            shown += f"\n... and {omitted} more path(s)"
        sections.append(f"Repository: {root}\nCurrent status:\n{shown}")

    if len(dirty_roots) > 5:
        sections.append(f"... and {len(dirty_roots) - 5} more dirty worktree(s)")

    return (
        "One or more git worktrees touched in this session are dirty. Before ending the conversation, "
        "offer the user a concise way to organize it.\n\n"
        + "\n\n".join(sections)
        + "\n\n"
        "Do not automatically commit, stash, revert, or delete anything unless the user "
        "already asked for that. In the final response, offer suitable options such as: "
        "review related changes and commit/push if appropriate; split or stage related "
        "changes; stash or save a patch; discard only with explicit approval; or keep "
        "the worktree dirty / ignore for now if the user intentionally wants that."
    )


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except JSONDecodeError:
        return emit({"continue": True})

    event_name = payload.get("hook_event_name")
    if event_name == "PostToolUse":
        return record_touched_worktrees(payload)

    if event_name != "Stop":
        return emit({"continue": True})

    already_continued_by_stop_hook = payload.get("stop_hook_active") is True
    if already_continued_by_stop_hook:
        return emit({"continue": True})

    reason = build_dirty_worktree_followup(payload)
    if reason is None:
        return emit({"continue": True})

    return emit({"decision": "block", "reason": reason})


if __name__ == "__main__":
    if "--dirty-report" in sys.argv:
        cwd = Path.cwd()
        if "--cwd" in sys.argv:
            try:
                cwd = Path(sys.argv[sys.argv.index("--cwd") + 1]).expanduser()
            except IndexError:
                pass
        recent_hours = 12.0
        if "--recent-hours" in sys.argv:
            try:
                recent_hours = float(sys.argv[sys.argv.index("--recent-hours") + 1])
            except (IndexError, ValueError):
                pass
        raise SystemExit(print_dirty_report(cwd, recent_hours))

    raise SystemExit(main())
