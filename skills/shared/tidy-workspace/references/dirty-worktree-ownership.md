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
- Treat timestamps, process IDs, task titles, branch names, previews, and old
  summaries as clues only. None proves ownership.

## 2. Delegate one bounded investigator

When Codex App subagents and thread tools are available, send one read-only
subagent to investigate. Its prompt must include:

- the sender's exact task/thread reply target;
- read-only permission until a recipient is proven and freshly read;
- the exact repo, physical worktree, branch, and dirty paths in scope;
- hard boundaries: no file or Git mutation, no task creation, no broadcast,
  no raw App database access, no tmux workaround, and no destructive advice;
- the requirement to return evidence and unresolved ambiguity to the sender.

If either capability is unavailable, fail closed: preserve the changes and ask
the user rather than guessing. The main agent must not silently replace this
check with weaker attribution.

## 3. Find and prove the responsible task

The investigator uses only Codex App-native thread tools:

1. List recent active tasks to produce a small candidate set.
2. Read each candidate's current thread, not just its title or preview.
3. Require direct evidence tying the candidate to the exact physical worktree
   and at least one dirty path or the work that produced it. A matching repo or
   branch alone is insufficient.
4. Classify the result as `confirmed`, `possible`, or `not found`, and quote or
   summarize the exact evidence. Never attribute user changes to Codex merely
   because another task exists.

Only `confirmed` permits contact. For `possible` or `not found`, send nothing,
return the evidence to the source task, and leave the worktree untouched.

## 4. Negotiate isolation with the confirmed task

Immediately before sending, fresh-read that exact recipient again. If the read
fails, its state changed materially, or the evidence no longer matches, do not
send.

Send one targeted message containing:

- the sender's reply target and the investigator's read-only coordination role;
- the exact shared worktree and conflicting paths;
- a request for the responsible task to confirm ownership and choose a safe
  handoff: finish and checkpoint only its own work, or continue in a dedicated
  Git worktree;
- hard boundaries forbidding reset, restore, clean, default stashing, editing
  another task's paths, or claiming the shared worktree is clean without a
  fresh Git check.

Do not claim that an already-running task can be moved automatically. The
responsible task must first make its own changes transferable—normally as a
focused commit—then create or continue in a dedicated worktree and verify both
locations. Creating a new user-owned Codex task still requires the user's
explicit request; thread tools must not invent one as part of cleanup.

## 5. Verify the result

- Fresh-read the responsible task's reply; a callback is only a wake signal,
  not proof that cleanup finished.
- Rerun the workspace inspector and `git status` in the exact physical
  worktree.
- Continue only when the previously dirty paths are accounted for and the
  current task's intended boundary is clean. Otherwise preserve state and
  report the blocker.
- Never use repeated broad polling or message multiple candidate tasks.

Report the confirmed owner, evidence used, message target, agreed handoff,
fresh Git result, and anything unresolved. Do not expose unrelated thread
content.
