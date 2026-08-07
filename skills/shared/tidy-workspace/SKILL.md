---
name: tidy-workspace
description: "Tidy and synchronize a Git workspace. Use when the user invokes $tidy-workspace or asks to tidy, clean, pull, sync, or reconcile a repo, worktree, stash, local commits, and its remote without wrapping the whole session."
---

Preserve unrelated work from the user or other agents.

## Inspect

First confirm the directory is a Git repo; otherwise skip it and inspect repos
touched this session. Run the relevant checks in each repo:

```bash
git rev-parse --is-inside-work-tree
git status
git status --short --branch
git branch --show-current
git rev-list --left-right --count HEAD...@{upstream}
git log --oneline @{upstream}..HEAD
git diff --stat @{upstream}..HEAD
git stash list
git worktree list
/usr/bin/python3 "$HOME/dotfiles/codex/hooks/stop_dirty_worktree.py" --dirty-report --cwd "$PWD"
```

Fetch before deciding whether the branch is ahead, behind, or diverged. Review
the full upstream-to-HEAD outgoing range and diff before changing anything.

## Reconcile

- Clean and behind only: fast-forward with `git pull --ff-only`.
- In-scope dirty changes: review, test as appropriate, commit intentionally,
  then sync and push.
- Ahead only: push only after confirming every outgoing commit belongs to the
  requested scope and the destination is correct. Otherwise preserve it and
  ask. If the remote protects the branch, use its normal PR flow and follow CI.
- No upstream: confirm the intended remote and branch before setting one or
  pushing.
- Detached HEAD or any in-progress Git operation—including merge, rebase,
  cherry-pick, revert, `git am`, or bisect: stop and ask.
- Diverged history, conflicts, ambiguous WIP, sensitive files, or unclear
  ownership: stop and ask instead of guessing.
- Before commit or push, inspect staged, unstaged, and outgoing diffs for
  secrets, credentials, private keys, non-public personal data, and private
  machine details. Treat unknown repo visibility conservatively.
- Never discard, reset, force-push, run `git clean`, delete untracked files,
  drop stashes, remove worktrees, or delete local/remote branches or tags
  without explicit authorization. Never disturb another agent's worktree.

Treat proven temporary, stale, or merged items as cleanup candidates only; that
evidence is not deletion authorization. Leave unrelated changes, commits,
stashes, branches, and worktrees in place and report them.

## Report

Reply in zh-TW with:

- repos and branches inspected;
- commits, pulls, pushes, PRs, or cleanup completed;
- tests or CI results;
- anything deliberately preserved or still needing a decision.

If everything was already synchronized and clean, say so directly.
