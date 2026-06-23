---
name: cmux-events
description: Event-based completion watching under cmux and when to fall back to marker files.
type: delegation-lesson
updated: 2026-06-23
---

## Use when
Waiting for a delegated cmux worker (e.g. Codex) to finish, without foreground polling.

## Lessons
- Preferred wakeup: background-subscribe to the event stream, then verify the report marker:
  `cmux events --name agent.hook.Stop --no-ack --no-heartbeat --reconnect`
  Filter the NDJSON yourself for `workspace_id`, `source`, and payload `session_id`.
- Real `cmux events` flags: `--name`, `--category`, `--after`, `--after-seq`,
  `--cursor-file`, `--reconnect`, `--limit`, `--no-ack`, `--no-heartbeat`. Without
  `--limit` it blocks/streams; `--limit n` makes it one-shot after n event frames.
- There is NO `--surface-id` / `--workspace-id` CLI filter and NO `turn-complete` /
  `surface-idle` / `agent-idle` event name. Filter JSON fields instead.

## Failure patterns
- `agent.hook.Stop` is workspace-scoped, not surface-scoped. Multiple workers in one
  workspace need `session_id` correlation OR a marker/lease file to tell them apart.
- Notification events can be suppressed (nested/stale sessions); the replay window is
  bounded (~4096 events); slow consumers get disconnected. So keep marker-file polling
  as the final completion contract and fallback. Verified against cmux source (2026-06).
