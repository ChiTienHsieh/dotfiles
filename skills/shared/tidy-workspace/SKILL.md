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
  drop stashes, or delete tags without explicit authorization. Never disturb
  another agent's worktree.

Leave unrelated work in place. Temporary, stale, or merged means cleanup
candidate, not proof that deletion is safe.

## Clean up branches and worktrees

The agent that creates a branch, worktree, or PR owns it through terminal
cleanup. Do not defer cleanup merely because the session is ending. Autonomous
cleanup is limited to exact resources created by the current agent or assigned
to it through an explicit, verifiable handoff; unclear ownership means ask.
Resolve all targets first, then apply this table. One question may cover a
clearly listed set of targets with the same blocker.

| Evidence | Action |
| --- | --- |
| Owned worktree is clean, no live agent/process or open PR uses it, and its branch has no unique data under the rules below | Remove the worktree without asking, then prune only stale worktree metadata. |
| Owned branch has no worktree or active use, no open PR, and no unique data under the rules below | Delete it without asking when normal non-force deletion succeeds. Delete a matching remote branch only with a server-enforced atomic expected-old-OID guard covering its freshly resolved exact tip; if that capability is unavailable or requires a force option, ask. |
| Dirty worktree; unpushed or otherwise unique data; active PR/live agent; mismatched, unavailable, or contradictory evidence; or any cleanup requiring `--force`, `-D`, reset, discard, or force-push | Preserve it and ask. State the exact target, evidence, and decision required. |

Prove **no unique data** for the exact tip being deleted with one of these
routes using freshly resolved refs and PR state:

1. The tip is reachable from a retained ref (normally the PR target or its
   remote-tracking ref).
2. For a squash or rebase merge, the hosting service reports the PR as merged,
   the PR's recorded head OID equals the exact branch tip being deleted, and
   the provider's recorded merge/result OID is currently reachable from the
   exact retained target ref. Repository and ref identities must also agree.
   This result evidence replaces source-branch ancestry; a merged label, branch
   name, patch similarity, commit-message match, or head OID alone does not.

Do not delete the last retained ref that supplies the applicable evidence.

A closed-but-unmerged PR is not proof that its unique head data may be deleted.
If the branch advanced after the recorded PR head, treat the additional commits
as unique. Refresh refs, PR state, and available Codex task/tmux status
immediately before deletion; an old snapshot is not evidence. Run only
non-force cleanup commands autonomously. If normal deletion rejects a
squash-merged branch because ancestry is absent, the PR evidence may establish
safety, but `git branch -D` still requires authorization.

After cleanup, rerun the inspector plus `git worktree list` and relevant branch
and PR queries. A creator reaches terminal state only when the requested work
and CI are resolved and every owned cleanup target is removed, explicitly
handed off, or preserved with a concrete blocker and required decision.

## Report

- repos and branches inspected;
- actions, tests, and CI completed;
- removed worktrees/branches and the evidence used;
- preserved work or decisions still needed, including the exact blocker.

If everything was already synchronized and clean, say so directly.
