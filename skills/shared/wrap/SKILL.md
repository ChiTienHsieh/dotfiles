---
name: "wrap"
description: "Finish the current session. Use when the user invokes $wrap or asks to wrap up, wrap it up, finish the current work, or ship the session: resolve unfinished work, update necessary docs, delegate Git cleanup to $tidy-workspace, and give a concise zh-TW summary."
---

1. Check the conversation and task state for unfinished requested work. Finish
   safe in-scope items; surface real blockers.
2. Update user-facing docs when this session changed setup, commands,
   architecture, or behavior.
3. Before declaring the session ready to archive, inventory exact external-agent
   targets this session created and owns, plus any additional exact targets the
   user explicitly placed in cleanup scope. Immediately fresh-read each target's
   execution state and latest output; an idle state, title, or old snapshot is
   not completion evidence. Close only targets with accepted completion evidence
   that are no longer needed, following that surface's authorization and cleanup
   SSOT, then verify the exact target is absent. If cleanup is unauthorized or
   unavailable, or the target is user-owned, pre-existing, active, or intentionally
   retained, preserve it and report the reason.
4. Read `../tidy-workspace/SKILL.md` completely and follow it for every repo
   touched this session. Also check `~/dotfiles` when present because edits
   through home-directory symlinks may evade the dirty-worktree tracker. That
   skill is the Git workflow SSOT.
5. Give a concise zh-TW summary of what was completed, verified, committed, and
   pushed, plus any remaining decision or blocker.

If the user only wants Git cleanup or remote synchronization, use
`$tidy-workspace` directly. Keep the dependency one-way: `$wrap` may invoke
`$tidy-workspace`; `$tidy-workspace` must not invoke `$wrap`.
