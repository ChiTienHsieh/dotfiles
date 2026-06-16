---
name: tmux-orchestration
description: "Use when running, supervising, or delegating work to interactive agents inside tmux, especially Claude Code CLI or Codex CLI sessions that need visible long-running execution, periodic observation, auto-mode setup, fallback from zellij, or safe cleanup after completion."
---

# tmux Orchestration

Use this skill when a task should run in an interactive terminal agent that remains visible and inspectable. Prefer it for Claude Code writer sessions, long-running Codex/Claude work, quota-aware overnight jobs, and any request where the user explicitly asks to use tmux.

## Core Rules

- Use tmux when zellij is unavailable, unreliable, or not requested.
- Keep each substantial worker in its own named tmux session.
- Use descriptive session names, for example `sp229-opus`, `issue424-writer`, or `quota-watch`.
- Start sessions in the intended repo or worktree directory.
- Capture panes instead of assuming a worker is idle.
- If tmux commands fail with sandbox or permission errors, retry with escalation.
- Do not kill unrelated tmux sessions. Only close sessions created for the current task or explicitly named by the user.
- Keep the user updated in short language during long waits.

## Starting Claude Code

For a Claude writer or reviewer session, start Claude Code interactively inside tmux:

```bash
tmux new-session -d -s SESSION_NAME -c /path/to/worktree 'claude --model opus --permission-mode acceptEdits --allowedTools Read,Write,Edit,MultiEdit'
```

Adjust model and allowed tools only when the task requires it. Do not use bypass or danger flags.

After launch, observe the pane:

```bash
tmux capture-pane -pt SESSION_NAME -S -80
```

## Claude Auto Mode

Before sending substantial work to Claude Code in tmux, try to switch Claude Code into auto mode:

1. Send `Shift+Tab` up to three times.
2. Capture the pane after each attempt when possible.
3. Confirm the bottom-left TUI indicator shows auto mode or a similar automatic-running state.
4. If the indicator cannot be confirmed, continue with normal accept-edits mode and mention the limitation in the next update.

Use tmux key sending for this when available:

```bash
tmux send-keys -t SESSION_NAME BTab
```

Some terminals map `Shift+Tab` differently. If `BTab` does not work, proceed without inventing unsafe key sequences.

## Sending Prompts

- Put long prompts in a scratch file.
- Paste or send one concise instruction that tells the worker to read that file.
- Send Enter separately.
- If the prompt appears pasted but not submitted, send Enter again after checking the pane.

Example:

```bash
tmux send-keys -t SESSION_NAME 'Read /tmp/task-prompt.md and complete it. Report when done.'
tmux send-keys -t SESSION_NAME Enter
```

## Observation Cadence

- For short tasks, check every 30-90 seconds.
- For user-requested patient Claude Code work, check every 10 minutes unless there is an obvious prompt/approval wait.
- If the user says the work can take an hour, do not interrupt early just because the TUI is quiet.
- Use pane captures, local file status, and expected artifacts to decide whether progress is real.
- If the worker is waiting for approval, erroring, or stuck at a prompt, intervene.

## Completion

Before accepting a worker's result:

1. Read the files or reports it produced.
2. Run reasonable validation yourself.
3. Check git status and diff.
4. Confirm no secrets, unrelated files, or unsafe changes were introduced.
5. Commit/push only when the task and repo rules allow it.

## Cleanup

When the worker is no longer needed:

```bash
tmux kill-session -t SESSION_NAME
```

If killing a tmux session needs escalation, request it. Do not close other user sessions just to make the tmux list tidy.
