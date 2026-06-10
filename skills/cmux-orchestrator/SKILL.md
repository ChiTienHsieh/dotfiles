---
name: cmux-orchestrator
description: "Use when orchestrating or delegating work to multiple Codex agents through cmux surfaces, especially when a Claude Code or Codex controller needs safe multi-agent coordination, marker-file completion detection, or the drive_codex.sh helper."
---

# cmux Orchestrator

Use this skill to run a controller agent that coordinates one or more interactive Codex agents in separate cmux surfaces. Keep the controller focused on task design, read-only inspection, verification, and small fixes; delegate implementation, cross-file edits, and debugging to Codex surfaces.

## When To Use

- Use for multi-agent orchestration, parallel research, implementation handoff, or review loops where each worker should remain visible in cmux.
- Use when a Claude Code or Codex controller needs to start, observe, or resume multiple Codex agents without using headless `codex exec`.
- Use when task completion should be detected by marker files instead of terminal visual state.
- Do not use for a small single-agent edit where normal Codex work in the current session is enough.

## Safety Rules

- Use cmux surfaces plus interactive Codex CLI with normal approvals or auto-review.
- Never delegate with `codex exec`.
- Never use YOLO, bypass, or danger flags, including `--dangerously-bypass-approvals-and-sandbox`.
- Do not ask workers to weaken sandboxing, disable approvals, edit secrets, or bypass guardrails.
- Keep long prompts in files and send one-line instructions that point Codex at those files.
- Verify worker claims with read-only checks before accepting results.
- Store task prompts, logs, and handoff reports in an ignored scratch directory unless the user explicitly asks for tracked artifacts.

## Controller Workflow

1. Inspect the task, repo state, allowed edit paths, and stop conditions.
2. Split work into independent prompts with exact deliverables, allowed paths, verification commands, and a marker-file completion contract.
3. Start one cmux surface per worker or reuse an existing surface when appropriate.
4. Send each worker a one-line prompt that tells it to read its prompt file.
5. Poll the marker file, not the cmux visual "Working" state.
6. Read each worker report, verify important claims, resolve conflicts, and produce the final synthesis.

## cmux Commands

```bash
cmux tree --all
cmux list-pane-surfaces
cmux read-screen --surface surface:N --lines 30
cmux send --surface surface:N -- "text"
cmux send --surface surface:N "\n"
cmux new-surface --type terminal
```

In the cmux app, use the left sidebar to inspect worker surfaces directly.

## drive_codex.sh

Use the bundled `drive_codex.sh` helper to drive one interactive Codex surface and wait for a marker file:

```bash
./drive_codex.sh SURFACE PROMPTFILE MARKER OUTFILE TIMEOUT NEWSURF
```

- `SURFACE`: existing cmux surface, for example `surface:3`.
- `PROMPTFILE`: file containing the worker prompt.
- `MARKER`: completion marker expected in `OUTFILE`, for example `INSTALL_DONE`.
- `OUTFILE`: worker report file to poll.
- `TIMEOUT`: timeout in seconds; defaults to 420 when omitted.
- `NEWSURF`: any non-empty value creates a new cmux terminal surface and starts interactive `codex`.

The helper sends the prompt as one line, sends Enter separately, polls `OUTFILE` for `MARKER`, and prints the report tail when complete.

## Marker-File Convention

Do not infer completion from a surface no longer showing "Working"; approval pauses and waiting states can look idle. Require every worker to write a report file and end the file with a single marker line:

```text
WORKER_DONE
```

Use distinct markers for distinct workers when multiple agents run in parallel. If the marker does not appear before timeout, inspect the relevant cmux surface manually; the worker may be waiting for approval or blocked.
