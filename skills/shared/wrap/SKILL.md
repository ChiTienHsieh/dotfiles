---
name: "wrap"
description: "Finish the current session. Use when the user invokes $wrap or asks to wrap up, wrap it up, finish the current work, or ship the session: resolve unfinished work, update necessary docs, delegate Git cleanup to $tidy-workspace, and give a concise zh-TW summary."
---

1. Check the conversation and task state for unfinished requested work. Finish
   safe in-scope items; surface real blockers.
2. Update user-facing docs when this session changed setup, commands,
   architecture, or behavior.
3. Read `../tidy-workspace/SKILL.md` completely and follow it for every repo
   touched this session. Also check `~/dotfiles` when present because edits
   through home-directory symlinks may evade the dirty-worktree tracker. That
   skill is the Git workflow SSOT.
4. Give a concise zh-TW summary of what was completed, verified, committed, and
   pushed, plus any remaining decision or blocker.

If the user only wants Git cleanup or remote synchronization, use
`$tidy-workspace` directly. Keep the dependency one-way: `$wrap` may invoke
`$tidy-workspace`; `$tidy-workspace` must not invoke `$wrap`.
