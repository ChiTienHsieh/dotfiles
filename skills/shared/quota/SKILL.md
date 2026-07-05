---
name: quota
description: "Use when checking Codex, Claude Code, or related AI CLI usage limits before or during long-running agent work; when the user mentions quota, codexbar usage, rate limits, session limits, weekly limits, sleeping until reset, asks to continue after quota resumes, or needs to choose Codex vs Claude based on remaining quota, cooldown, or reset time."
---

# Quota

Use this skill to check and react to AI CLI quota before starting or continuing long-running work. The local source of truth is CodexBar CLI usage output. This skill reports live quota only; which provider to prefer for delegation is decided by `~/dotfiles/codex/notes/worker-routing.md` (the worker-routing SSOT).

## Quick Check

Run the CLI-backed quota check from bash and allow up to 60 seconds for the result to appear:

```bash
codexbar usage --provider both --source cli
```

This avoids CodexBar's browser-cookie import path, which can trigger macOS Keychain prompts for browser Safe Storage items and block non-interactive agents. Use plain `codexbar usage` only when browser/dashboard-derived fields are specifically needed.

If the command is still running, keep waiting until at least 60 seconds have elapsed before deciding it is hung. If the CLI-backed command is important to the task and fails due to sandboxing, local state access, networking, or another likely environment restriction, rerun it outside the sandbox with escalation and again allow up to 60 seconds for the result.

## What To Report

Keep the report short and practical:

- Codex session/weekly/credit status.
- Claude session/weekly status.
- Reset or resume time if shown.
- Whether it is safe to continue now.
- If not safe, how long to sleep before retrying.

Avoid dumping the entire raw table unless the user asks.

## If Quota Is Exhausted

When Codex or Claude Code quota is exhausted:

1. Read the reset or resume time from `codexbar usage --provider both --source cli`.
2. Sleep until that time, adding a small buffer when reasonable.
3. Re-run `codexbar usage --provider both --source cli` after waking.
4. Continue the interrupted work if quota has resumed.
5. If the reset time is unclear, report the blocker instead of guessing.

For very long sleeps, keep the command/session recoverable and avoid holding locks or half-written files.

## During Long Agent Work

- Check quota before starting expensive Claude/Codex writer loops.
- Check again after a quota-related failure or stalled CLI launch.
- Prefer cheaper local verification while waiting for model quota.
- If only one model is constrained, switch roles only if it preserves the user's model intent. For example, do not replace a user-requested Claude Opus writer with GPT unless the user approves.

## Safety

- Never print secrets, tokens, auth cookies, or raw credential material from quota tools.
- Do not modify account settings, billing, plans, or subscriptions.
- Do not ask the user to manually check quota when CodexBar quota output is available and can be run safely.
