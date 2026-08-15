---
name: tmux-orchestration
description: "Use only when the current human explicitly asks the agent to use tmux or explicitly requests a visible interactive CLI session inside tmux. Do not trigger from any other source or task characteristic."
---

# tmux Orchestration

Run a task in an interactive terminal agent that stays visible and inspectable — Claude/Codex writer sessions, long-running or quota-aware overnight work.

## Activation Gate

- Fail closed unless the current human instruction explicitly asks the agent to use tmux or explicitly requests a visible interactive CLI session **inside tmux**.
- Only the current human instruction can authorize tmux; agent instructions, skill discovery, and reading this skill cannot.
- Without that authorization, do not run tmux, its helpers, or its lifecycle workflow. Prefer built-in subagents or the current session. After authorization, follow the complete launch, delegation, observation, and cleanup rules below.

## Core Rules

- Use tmux only for the exact scope the human authorized.
- Keep each human-authorized substantial worker in its own named tmux session — EXCEPT when the human explicitly asks to spawn a Codex or Claude reviewer/collaborator alongside the orchestrator. In that case, use a NEW PANE in the orchestrator's OWN tmux session/window (`tmux split-window`) so both sit side-by-side. Do NOT open a separate tmux session for this co-review case.
- Use descriptive session names, for example `sp229-opus`, `issue424-writer`, or `quota-watch`.
- Start sessions in the intended repo or worktree directory.
- Capture panes instead of assuming a worker is idle.
- Do not kill unrelated tmux sessions. Only close sessions created for the current task or explicitly named by the user.
- The controller that creates a worker owns its lifecycle. Before ending the task, every created target must be closed or explicitly retained with a reason.

## Delegation Contract

Use this contract whenever a worker prompt, marker file task, or delegated
surface will be read by another agent.

- Marker-file 完工合約: every delegated worker writes a report to PATH and ends
  it with one exact MARKER line; the controller polls the marker, not terminal
  visual state. Contract fields: mode (read-only / write-new-only / edit-allowed), allowed paths, forbidden actions, report path, marker, authority signature.
- Use fixed nouns "CC" and "user", never 你/我 — a relative pronoun flips
  referent when a different agent reads the prompt.
- Put long instructions in a file; keep the send-line a one-liner pointing at
  it. `tmux send-keys` turns every newline in the argument into an Enter, so a
  multi-line prompt submits in fragments.
- Place prompt, report, and marker files inside the worker's trusted cwd or the
  target repo's ignored task dir. If a worker must commit, it needs a full clone
  with `.git` inside its workspace; otherwise the controller owns commits.
- State the side-effect boundary up front: READ-ONLY research, or exactly which
  paths may be edited, plus "do not commit/push" when the controller verifies
  first.
- End cross-agent prompts with the sender's tmux pane ID and authority level.
  Format: `—— 來自 %47（orchestrator CC，委派任務；限制為硬邊界。回問：tmux send-keys -t %47）`.
  Use `user 直接指令` instead of `委派任務` only for instructions directly
  authorized by the user.
- Verify load-bearing claims with cheap read-only checks: grep for leftover
  references, `git status` / `git diff --stat`, confirm files moved/deleted,
  read only the one section whose accuracy matters.
- Fresh-reviewer 驗證原則: for large artifacts, delegate the FULL review to a fresh worker rather than
  re-reading everything yourself — a clean-context reviewer is at least as
  reliable and saves the controller's context. If only one dimension fails,
  fix it and prefer a targeted rescore for that dimension. The prompt must
  include the original fail criterion, what changed, which slice to re-evaluate,
  and whether neighboring dimensions need a light sanity check.

## Starting Claude Code

For a Claude writer or reviewer session, start Claude Code interactively inside tmux:

```bash
tmux new-session -d -P \
  -F 'CODEX_TMUX_WORKER_OPEN=session:#{session_name}' \
  -s SESSION_NAME -c /path/to/worktree \
  'claude --model opus --permission-mode auto --allowedTools Read,Write,Edit,MultiEdit'
```

When the lifecycle hook is installed, tmux generates the open receipt directly
from the session it created. Keep `-P`, the exact `-F` format, and a literal
session name; do not replace the receipt with a separate `printf`.

Use `--permission-mode auto` by default. `acceptEdits` prompts too often for long-running tmux orchestration and wastes either controller tokens or human attention. Adjust model and allowed tools only when the task requires it. Do not use bypass or danger flags.

For sessions meant to live a long time, prefer the crash-proof **cushion pattern** in "Reviving a dead session" below (launch a shell, run the agent as its child) — a launch with `claude` as the pane root dies, and takes the whole session with it, the instant claude exits.

After launch, observe the pane:

```bash
tmux capture-pane -pt SESSION_NAME -S -80
```

## Spawning a worker beside you (same window — preferred for co-review)

When the user wants a Codex/Claude worker to review or brainstorm *with* the orchestrator, split a new pane in the orchestrator's current session instead of opening a new session:

```bash
# -h = split left/right; target the orchestrator's own session/window
tmux split-window -h -P -F 'CODEX_TMUX_WORKER_OPEN=pane:#{pane_id}' \
  -t SESSION_NAME -c /path/to/repo 'codex --sandbox read-only'
```

Both panes then live in one window, side-by-side, so the user can watch the worker and the orchestrator together.

Read the exact pane ID from the returned marker, then capture that pane in a
separate command. Never close the whole session when the worker is only a pane.

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
- Send one concise instruction that tells the worker to read that file.
- Default to `scripts/agent-send-prompt.sh PANE 'ONE-LINE PROMPT'`; it pastes the literal prompt, verifies it is visible, sends Enter separately, and retries Enter once if needed.
- Hand-written `tmux send-keys` for long prompt payloads is blocked by the Bash helper guard. Short key sends such as `Enter` / `BTab` remain fine.
- Send the prompt as ONE line — no embedded newlines or blank lines. `tmux send-keys` turns every newline in the argument into an Enter, so a multi-line prompt submits in fragments; on a Codex TUI this can crash the turn (`turn/start failed`) and drop it to a bare shell.

Example:

```bash
~/dotfiles/skills/shared/tmux-orchestration/scripts/agent-send-prompt.sh \
  SESSION_NAME 'Read /tmp/task-prompt.md and complete it. Report when done.'
```

## Observation Cadence

- If the worker contract already includes a report path plus final marker, the
  controller defaults to checking only marker/report/git state, not the worker
  stream. Read the stream only for approval waits, timeout diagnosis, a blocked
  report, or active quality steering.
- `scripts/...` paths in this skill resolve against the skill's own directory
  (`~/dotfiles/skills/shared/tmux-orchestration/`), not your cwd — expand them
  before running.
- Monitor in three layers: deterministic completion uses a background shell
  watcher such as `scripts/agent-watch-marker.sh REPORT_PATH MARKER --timeout
  3600`; waits needing eyes use a cheap background subagent that polls in its
  own context and returns one-line summaries (still burns quota, so prefer file
  signals); controller stream reads are only for quality steering.
- For report/status reads, default to `scripts/agent-safe-read.sh REPORT_PATH`
  and then `scripts/agent-safe-read.sh REPORT_PATH --range START:END` for the
  load-bearing slice. For repo-wide checks, default to `scripts/agent-rg.sh
  PATTERN PATH`, `scripts/agent-rg.sh PATTERN PATH --sample 3`, or
  `scripts/agent-rg.sh PATTERN PATH --files`; use `--full REASON` only when the
  complete output is necessary.
- Choose the right mechanism FIRST: an event-driven hook usually beats long polling. If you only need to know "is it done" (not watch live), prefer a completion signal — a marker file the worker touches on finish, `tmux wait-for`, or a Stop/Notification hook — so the controller is woken by the event instead of burning turns polling. Reserve polling for when you must watch live progress to JUDGE quality (a review loop you're steering, a build whose errors you read as they appear). Alternate between hook and patient polling per scenario; do not poll when a hook would do the job for free. Caveat: `tmux wait-for` blocks the calling shell, so for long waits prefer a marker file (poll its existence) or a hook — a blocking wait can hit the Bash command timeout.
- When you DO poll, default to PATIENT polling. Once a worker is mid-run on a multi-minute task (a review loop, a build, a long Codex turn), check at intervals of at least 5 minutes. Polling every 30-90 seconds is micromanaging — it wastes controller turns and reads as creepy to the user. Reserve sub-minute checks for genuinely short tasks or when actively waiting on an approval/error prompt.
- For user-requested patient Claude Code work, check every 10 minutes unless there is an obvious prompt/approval wait.
- If a worker shows no meaningful progress for 25 consecutive minutes, inspect the pane. Spinner movement, repeated output or errors, and an unchanged approval prompt do not count as progress. Intervene immediately for approval waits or errors; otherwise request one status update or send one interrupt, and terminate the worker if it still does not respond. Meaningful output or a real state transition resets the clock.
- A user's expected total duration does not override the 25-minute no-progress limit. Only an explicit replacement for the no-progress limit does.
- When capturing, read the FULL new region since the last check, not just the tail. Use a wide scrollback range (`tmux capture-pane -p -S -<large>`) and read forward from where the previous check ended. A bare `| tail -N` silently drops anything that scrolled past between polls, so you miss findings and lose the thread.
- If the worker is waiting for approval, erroring, or stuck at a prompt, intervene.

## Context Burn Stop Rule

After one compaction or near 200k tokens, stop pasting raw pane captures or raw
logs into the main thread. Ask for a condensed worker report plus source paths;
for verification, read only load-bearing slices with `scripts/agent-safe-read.sh
FILE --range START:END` and search counts/samples with `scripts/agent-rg.sh`.

## Completion

Before accepting a worker's result:

1. Read the files or reports it produced.
2. Run reasonable validation yourself.
3. Check git status and diff.
4. Confirm no secrets, unrelated files, or unsafe changes were introduced.
5. Commit/push only when the task and repo rules allow it.

## Cleanup

Keep start, wait, read-status, and cleanup as separate commands. Never bundle
cleanup actions such as `pkill`, reset, or clean with status queries in the same
Bash call.

Immediately before cleanup, capture the worker's latest state and confirm its
report, marker, or other result has been accepted. An idle prompt is not proof
of completion.

When a standalone worker session is no longer needed:

```bash
tmux kill-session -t SESSION_NAME
```

When a side-by-side worker pane is no longer needed:

```bash
tmux kill-pane -t %42
```

After cleanup—or if another actor already closed the target—run the matching
absence receipt below in a separate command. It verifies that the exact target
is gone before printing the closed marker:

```bash
codex_tmux_targets=$(tmux list-sessions -F '#{session_name}' 2>/dev/null) && { printf '%s\n' "$codex_tmux_targets" | grep -Fx -- 'SESSION_NAME' >/dev/null; codex_tmux_grep_status=$?; if [ "$codex_tmux_grep_status" -eq 1 ]; then printf '%s\n' 'CODEX_TMUX_WORKER_CLOSED=session:SESSION_NAME'; else [ "$codex_tmux_grep_status" -eq 0 ]; fi; }
codex_tmux_targets=$(tmux list-panes -a -F '#{pane_id}' 2>/dev/null) && { printf '%s\n' "$codex_tmux_targets" | grep -Fx -- '%42' >/dev/null; codex_tmux_grep_status=$?; if [ "$codex_tmux_grep_status" -eq 1 ]; then printf '%s\n' 'CODEX_TMUX_WORKER_CLOSED=pane:%42'; else [ "$codex_tmux_grep_status" -eq 0 ]; fi; }
```

The lifecycle hook accepts only these canonical default-server command shapes;
custom tmux sockets such as `tmux -L ...` are not tracked automatically.

Before the controller's final response, resolve every worker it opened:

- Close accepted or obsolete workers and verify they are absent.
- For a worker that must keep running, tell the user why with
  `保留中的 tmux worker：TARGET（REASON）`; include every retained target.

The Codex `Stop` hook only reminds and blocks once when tracked workers remain;
it never calls tmux or terminates a process. All tmux commands still require the
normal scoped escalation and Guardian review.

## Reviving a dead session

A tmux session is destroyed the moment its last pane's **root** process exits. Launching `claude` as the pane root (`tmux new-session ... 'claude ...'`) means any claude exit — crash, `/quit`, double Ctrl-C, an errored turn — takes the whole session with it. A pane whose root is a shell survives its child dying.

**Cushion pattern (crash-proof; prefer for long-lived agents):** make a shell the pane root, then run the agent as its child. When the agent dies you drop back to the shell, the session survives, and the error stays on screen.

```bash
tmux new-session -d -P \
  -F 'CODEX_TMUX_WORKER_OPEN=session:#{session_name}' \
  -s SESSION_NAME -c /path/to/repo                         # shell is the pane root
tmux send-keys -t SESSION_NAME 'claude --resume <uuid>'   # agent runs as a child
tmux send-keys -t SESSION_NAME Enter
```

The shell can die but the transcript outlives it. To revive a dead Claude session:

1. Look under `~/.claude/projects/` — each session's cwd maps to one encoded subdir there. Don't reconstruct the exact name (the encoding mangles both `/` and `.`); list the dirs, sort by mtime, and let the fingerprint in step 2 confirm.
2. Identify the right transcript by **content fingerprint**, not filename (filenames are UUIDs): `grep -l '<distinctive phrase from the session>' *.jsonl`. Each line also carries a `"cwd"` field you can grep to confirm the project.
3. Revive with the cushion pattern above, running `claude --resume <uuid>` inside the shell.

Decision rules:
- **attach vs resume:** still in `tmux ls` → `tmux attach` (process alive, no state lost). Gone from the list → `claude --resume` (process dead, rebuild from transcript). They are not interchangeable.
- **Never `--resume` the same uuid from two panes** — the two claude instances fight over one session and can evict each other.
- **Decide whether to revive at all:** if the session's output already landed (committed, pushed, file written), the dead shell is irrelevant — read the artifact and skip the revive. Only revive when useful context is stranded in memory.
- Retrofitting the cushion onto an already-running session is impossible without killing and re-resuming it. Do not churn healthy, attached sessions for it; let the cushion apply on their next revive.

## Delegation Lessons (shared, maintained)

Before delegating or supervising a worker, read the shared lessons index:

`~/dotfiles/skills/shared/tmux-orchestration/references/lessons.md`

It is a single file of dated incident lessons, grouped by section. Open ONLY the
section relevant to the current delegation. After the delegation finishes, if you
learned a durable lesson, update the relevant section — dated, distilled rules
only; the general delegation contract stays in this SKILL.md, not there.

Implementation routing policy lives in the `arbitrage` skill; provider priority
lives in `~/dotfiles/codex/notes/worker-routing.md`. This skill only
covers surface mechanics: prompt files, observable workers, marker reports,
completion, and verification.
