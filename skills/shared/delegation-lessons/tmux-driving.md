---
name: tmux-driving
description: Launching and observing delegated Codex/Claude agents in tmux panes.
type: delegation-lesson
updated: 2026-06-23
---

## Use when
Driving an interactive agent in a tmux pane from a controller.

## Lessons
- tmux talks over a Unix socket in /private/tmp; the controller's sandbox blocks it.
  Run tmux commands with the sandbox disabled (same as SSH on this machine).
- Launch a worker with `codex --sandbox workspace-write`. Set cwd to a WRITABLE scratch
  dir (e.g. under /tmp) when the worker must WRITE a report while only READING another
  repo — workspace-write permits cwd writes and read-only access elsewhere. Set cwd to
  the target repo when the worker must EDIT that repo.
- send-keys: send the instruction line, wait ~1s, then send Enter SEPARATELY. Put long
  prompts in a file; the send-line just says "Read PATH and do it."
- Capture panes (`capture-pane -p`) to confirm progress; do not assume idle = done.

## Failure patterns
- `/quit` needs a moment before the next launch command; sleep before relaunching.
- A directory-trust prompt appears on first codex launch in a new dir; answer 1.
