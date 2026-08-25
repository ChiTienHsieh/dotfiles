# Dirty Worktree Ownership Protocol

Use this protocol only when a shared physical worktree contains staged,
unstaged, or untracked changes that are outside the current task and whose
owner（變更負責者）is unknown. Known current-task or user-owned changes stay in
the normal `review-dirty` flow.

## 1. Freeze the worktree

- Do not stage, commit, stash, restore, reset, clean, switch branches, or edit
  any dirty path.
- Record the exact Git root, physical worktree path, branch, active Git
  operation, and staged, unstaged, and untracked paths.
- Treat indirect metadata and stale snapshots as clues, never proof of
  ownership. Read-only fetches of remote refs remain allowed.

## 2. Delegate one bounded investigator

When Codex App subagents and thread tools are available, send one read-only
subagent to investigate. Its prompt must include:

- the sender's exact task/thread reply target;
- read-only permission and the exact repo, worktree, branch, and dirty paths;
- App-native thread tools only: no raw App database or tmux workaround;
- no file, index, branch, history, or task mutation, and no broadcast;
- the requirement to return evidence and unresolved ambiguity to the sender.

If either capability is unavailable, fail closed: preserve the changes and ask
the user rather than guessing. The main agent must not silently replace this
check with weaker attribution.

## 3. Find and prove the responsible task

The investigator uses only Codex App-native thread tools:

1. List recent active tasks to produce a small candidate set.
2. Read each candidate's current thread, not just its title or preview.
3. Build an ownership map for every dirty path and, when a file is mixed, its
   exact current hunks. Require direct evidence tying each confirmed scope to
   both the physical worktree and current diff content; intended work, a
   matching repo, or a matching branch is insufficient.
4. Mark each path or hunk `confirmed:<task>` or `unconfirmed`, and quote or
   summarize the evidence. Never attribute user changes to Codex merely
   because another task exists.

Contact only a task directly tied to a confirmed scope. Return every
unconfirmed or mixed scope to the source task and preserve it untouched.

## 4. Negotiate isolation with the confirmed task

Apply the global fresh-read-before-send gate to that exact recipient. If the
read fails, its state changed materially, or the evidence no longer matches,
do not send.

Send one targeted message containing:

- the sender's reply target and the investigator's read-only coordination role;
- only the exact confirmed paths or hunks, with unresolved scopes kept separate;
- a request to confirm ownership, current safety state, and whether the
  recipient's existing user authority covers checkpoint or worktree changes;
- hard boundaries: no destructive cleanup, no mutation outside proven
  ownership, and no claim of cleanliness without a fresh Git check.

The first message only establishes ownership and existing authority. A
read-only investigator cannot grant new mutation authority. If the fresh
recipient thread does not already authorize the exact checkpoint and worktree
actions, return to the source task for a user decision.

Do not claim that an already-running task can be moved automatically. When its
existing authority does cover the exact actions, the responsible task must
create a safe transferable checkpoint, continue in a dedicated worktree, and
verify both locations without touching unresolved scopes.

## 5. Verify the result

- Fresh-read the responsible task's reply; a callback is only a wake signal,
  not proof that cleanup finished.
- Rerun the workspace inspector, including a fresh `git status`, in the exact
  physical worktree.
- Continue only when the previously dirty paths are accounted for and the
  current task's intended boundary is clean. Otherwise preserve state and
  report the blocker.

Report the confirmed owner, evidence used, message target, agreed handoff,
fresh Git result, and anything unresolved. Do not expose unrelated thread
content.
