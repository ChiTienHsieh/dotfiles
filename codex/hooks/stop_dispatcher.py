#!/usr/bin/env python3
"""Keep already-running Codex sessions on the dirty-worktree hook."""

from stop_dirty_worktree import main


if __name__ == "__main__":
    raise SystemExit(main())
