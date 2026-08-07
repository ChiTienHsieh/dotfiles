---
name: tidy-workspace
description: "Tidy and synchronize Git workspaces without ending the session. Use for $tidy-workspace or requests to clean, pull, sync, or reconcile repos, worktrees, stashes, local commits, and remotes."
---

## Inspect

Resolve this skill's directory, then run
`scripts/inspect-workspace.sh [REPO_DIR ...]` with the current repo and every
repo touched this session. It also includes `~/dotfiles`, deduplicates Git
roots, and runs non-interactive `git fetch`; it never runs pull, commit, push,
or delete.
Treat `NEXT=` as a recommendation, not authorization. A non-zero exit is a
blocker.

## Act

- `review-dirty`: inspect staged and unstaged diffs; test and commit in-scope
  changes only, then rerun the script.
- `pull-ff-only`: run `git pull --ff-only`, then rerun the script.
- `review-outgoing`: inspect the full outgoing range and diff, confirm ownership
  and destination, then push through the repo's PR and CI flow when required.
- `stop:*`, sensitive files, ambiguous work, or unclear ownership: stop and ask.
- Before commit or push, check all relevant diffs for secrets, credentials,
  private keys, non-public personal data, and private machine details. Treat
  unknown repo visibility conservatively.
- Never discard, reset, force-push, run `git clean`, delete untracked files,
  drop stashes, remove worktrees, or delete branches or tags without explicit
  authorization. Never disturb another agent's worktree.

Leave unrelated work in place. Temporary, stale, or merged means cleanup
candidate, not authorized deletion.

## Report

- repos and branches inspected;
- actions, tests, and CI completed;
- preserved work or decisions still needed.

If everything was already synchronized and clean, say so directly.
