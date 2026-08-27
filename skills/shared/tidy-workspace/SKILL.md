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
- 若 worktree 內有不屬於目前任務、且負責者不明的變更，先凍結該 worktree
  的檔案、Git index（暫存區）、branch 與 history 寫入，再依
  `references/dirty-worktree-ownership.md` 處理。
- `pull-ff-only`: run `git pull --ff-only`, then rerun the script.
- `review-outgoing`: inspect the full outgoing range and diff, confirm ownership
  and destination, then push through the repo's PR and CI flow when required.
- 遇到 `stop:*`、敏感檔案、範圍不明的工作，或走完變更歸屬流程後仍無法確認
  負責者：停止並詢問使用者。
- Before commit or push, check all relevant diffs for secrets, credentials,
  private keys, non-public personal data, and private machine details. Treat
  unknown repo visibility conservatively.
- Never discard, reset, force-push, run `git clean`, delete untracked files, or
  drop stashes without explicit authorization.

## Terminal cleanup

The creator or current controller must finish cleanup for branches, worktrees,
and PRs it created or explicitly took over. Remove an exact target without
asking only when current evidence establishes all of the following:

- the target is precisely identified, owned or explicitly in scope, and no
  active task, process, or worktree is using it;
- the worktree is clean, and no dirty, untracked, stashed, or unpushed unique
  data would be lost;
- the PR is merged or closed, or the artifact is otherwise no longer needed;
- a remote, PR, merged base, or other verified copy is sufficient to recover
  the work after the planned cleanup;
- the exact cleanup is followed by a readback confirming the target state.

For squash merges, Git ancestry alone is not proof. Use the PR head OID, a
remote copy, patch or diff equivalence, or another simple reliable check. A
merged or closed PR with a clean, fully pushed worktree is a cleanup candidate,
but each deletion still needs the evidence above; deleting a remote copy also
requires another verified recovery copy. If ordinary local branch deletion
fails only because a squash merge broke ancestry, the complete evidence above
permits exact-target `git branch -D`; this deletes a verified redundant ref and
is not history rewriting.

Stop and ask before cleanup when the worktree is dirty, data exists only in an
unpushed commit or local artifact, an active task or agent still owns or uses
the target, ownership is unclear, evidence conflicts, or cleanup needs
force-push, history rewriting, credentials, billing, or access changes. The
current task remaining live for wrap-up or reporting is not target use; do not
defer otherwise-safe cleanup to a future session. Age or staleness alone never
proves deletion is safe. Leave user and other-agent artifacts untouched unless
this task explicitly took control of them, and leave all unrelated work in
place.

## Report

- repos and branches inspected;
- actions, tests, and CI completed;
- terminal cleanup performed and its readback evidence;
- preserved work or decisions still needed.

If everything was already synchronized and clean, say so directly.
