---
name: tmux-orchestration
description: "Use when running, supervising, or delegating work to interactive agents inside tmux, especially Claude Code CLI or Codex CLI sessions that need visible long-running execution, periodic observation, auto-mode setup, fallback from zellij, or safe cleanup after completion."
---

# tmux Orchestration

Use this skill when a task should run in an interactive terminal agent that remains visible and inspectable. Prefer it for Claude Code writer sessions, long-running Codex/Claude work, quota-aware overnight jobs, and any request where the user explicitly asks to use tmux.

## Core Rules

- Use tmux when zellij is unavailable, unreliable, or not requested.
- Keep each substantial worker in its own named tmux session — EXCEPT when spawning a worker (Codex or Claude) to review/collaborate *alongside* the orchestrator. In that case the user's preference is a NEW PANE in the orchestrator's OWN tmux session/window (`tmux split-window`), so both sit side-by-side in one window for live observation. Do NOT open a separate tmux session, and do NOT start a new cmux session, for this co-review case.
- Use descriptive session names, for example `sp229-opus`, `issue424-writer`, or `quota-watch`.
- Start sessions in the intended repo or worktree directory.
- Capture panes instead of assuming a worker is idle.
- If tmux commands fail with sandbox or permission errors, retry with escalation.
- Do not kill unrelated tmux sessions. Only close sessions created for the current task or explicitly named by the user.
- Keep the user updated in short language during long waits.

## Starting Claude Code

For a Claude writer or reviewer session, start Claude Code interactively inside tmux:

```bash
tmux new-session -d -s SESSION_NAME -c /path/to/worktree 'claude --model opus --permission-mode auto --allowedTools Read,Write,Edit,MultiEdit'
```

Use `--permission-mode auto` by default. `acceptEdits` prompts too often for long-running tmux orchestration and wastes either controller tokens or human attention. Adjust model and allowed tools only when the task requires it. Do not use bypass or danger flags.

After launch, observe the pane:

```bash
tmux capture-pane -pt SESSION_NAME -S -80
```

## Spawning a worker beside you (same window — preferred for co-review)

When the user wants a Codex/Claude worker to review or brainstorm *with* the orchestrator, split a new pane in the orchestrator's current session instead of opening a new session:

```bash
# -h = split left/right; target the orchestrator's own session/window
worker_pane="$(tmux split-window -h -P -F '#{pane_id}' -t SESSION_NAME -c /path/to/repo 'codex --sandbox read-only')"
tmux capture-pane -pt "$worker_pane" -S -80
```

Both panes then live in one window, side-by-side, so the user can watch the worker and the orchestrator together. Do not open a separate tmux session or a new cmux session for this co-review case.

## Claude Auto Mode

Before sending substantial work to Claude Code in tmux, confirm Claude Code is in auto mode:

1. Prefer launching with `--permission-mode auto`.
2. Capture the pane and check the bottom-left TUI indicator.
3. If it is not in auto mode, send `Shift+Tab` up to three times.
4. Capture the pane after each attempt when possible.
5. If auto mode still cannot be confirmed, continue only if the task remains safe and mention the limitation in the next update.

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

- Default to PATIENT polling. Once a worker is mid-run on a multi-minute task (a review loop, a build, a long Codex turn), check at intervals of at least 5 minutes. Polling every 30-90 seconds is micromanaging — it wastes controller turns and reads as creepy to the user. Reserve sub-minute checks for genuinely short tasks or when actively waiting on an approval/error prompt.
- For user-requested patient Claude Code work, check every 10 minutes unless there is an obvious prompt/approval wait.
- If the user says the work can take an hour, do not interrupt early just because the TUI is quiet.
- When capturing, read the FULL new region since the last check, not just the tail. Use a wide scrollback range (`tmux capture-pane -p -S -<large>`) and read forward from where the previous check ended. A bare `| tail -N` silently drops anything that scrolled past between polls, so you miss findings and lose the thread.
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

## Delegation Lessons (shared, maintained)

Before delegating or supervising a worker, read the shared lessons index:

`~/dotfiles/skills/shared/delegation-lessons/MEMORY.md`

It is a small index. Open ONLY the topic file relevant to the current delegation;
do not read every topic each turn. After the delegation finishes, if you learned a
durable lesson, update the relevant topic file and ensure the index has a one-line
entry. Distill into reusable rules — do not append raw logs or one-off incident detail.
