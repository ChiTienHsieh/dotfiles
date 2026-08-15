---
name: codex-task-return
description: "Reliably return status from delegated Codex App tasks. Use whenever a Codex task creates, forks, or continues another Codex task for delegated work, or when handling its completed, blocked, or needs-attention callback. Coordinates create_thread/fork_thread, wait_threads, fresh read before cross-task send, wake-up messages, idempotent receipts, and restart recovery."
---

# Codex Task Return

Treat delegation as a two-path return protocol:

- The child sends a short status event with `send_message_to_thread`; this is the
  path that actually wakes an idle source task.
- The source holds a bounded `wait_threads` call while it is active and uses
  saved cursors for recovery.

Use `$HOME/.codex/bin/task_delegation_registry.py` only for minimal private
receipts. It never calls App APIs. Do not add a hook, daemon, tmux worker, raw
App database reader, or high-frequency poller.

For the capability evidence, event contract, and failure/recovery table, read
`codex/notes/codex-task-delegation.md` in the dotfiles repo.

## Establish the contract

Before creating the child:

1. Read `CODEX_THREAD_ID` for the source thread id.
2. Use `list_threads` to match that exact id and obtain its current `hostId`.
   Do not infer a host from cwd, title, or an old snapshot.
3. Put the source host/id and this return protocol in the child prompt. The
   allowed event statuses are exactly `completed`, `blocked`, and
   `needs-attention`.

Verify the helper is installed on every participating host. Registries are
host-local and never copied between machines; qualified host/thread pairs stop
cross-host confusion, while the source's `wait_threads` path reconciles remote
child state. If a child host lacks the helper, keep the source wait active and
do not claim durable callback recovery.

After `create_thread` returns a ready `threadId` and `hostId`, register it:

```bash
python3 "$HOME/.codex/bin/task_delegation_registry.py" register \
  --source-host '<source-host>' \
  --child-host '<child-host>' \
  --child-thread '<child-thread>'
```

The source thread id defaults to the current `CODEX_THREAD_ID`. If creation
returns only `clientThreadId`, wait for setup and resolve the real thread/host;
never pass a client id to thread tools or the registry.

Keep title/purpose and expected output in the source conversation, not in the
registry. State stores only qualified ids, status, cursors, sequence, and
receipts.

## Child return path

Before the child ends or pauses for input:

1. Prepare an event. The child thread id defaults to its `CODEX_THREAD_ID`.

   ```bash
   python3 "$HOME/.codex/bin/task_delegation_registry.py" prepare \
     --source-host '<source-host>' \
     --source-thread '<source-thread>' \
     --child-host '<child-host>' \
     --status completed
   ```

2. Read the source with `read_thread` immediately before sending. Use the exact
   source `threadId` and `hostId`. A successful read of `idle` or `notLoaded` is
   sendable; missing, archived, deleted, mismatched, or unreadable is not.
3. Send the returned `message` unchanged with `send_message_to_thread`. It is a
   deterministic wake signal, not the child's result. Do not include the final
   answer or user data in it.
4. Only after send succeeds, record the event:

   ```bash
   python3 "$HOME/.codex/bin/task_delegation_registry.py" mark-sent \
     --event-id '<event-id>'
   ```

5. Leave the actual result in the child's final answer with a short verdict.

Use `blocked` when the work cannot proceed without new authority or external
state. Use `needs-attention` for a question, approval, or other actionable
pause. Do not send progress commentary as an event.

If fresh read or send fails, leave the outbox event `pending` and report the
blocker in the child. Never guess another recipient.

## Source wait and receipt path

Immediately after registration, call one bounded `wait_threads` for one to
eight active children. Pass each saved cursor as `afterCursor`; commentary must
not wake the wait. Reuse the returned cursor:

```bash
python3 "$HOME/.codex/bin/task_delegation_registry.py" set-cursor \
  --source-host '<source-host>' \
  --child-host '<child-host>' \
  --child-thread '<child-thread>' \
  --cursor '<cursor>'
```

When a child callback wakes the source:

1. Validate that its marker names this exact source and a registered child.
2. Fresh-read the child. Treat the callback as a wake signal only; use the
   child's current status/final answer as truth.
3. Act on the result.
4. Acknowledge the event fields only after handling:

   ```bash
   python3 "$HOME/.codex/bin/task_delegation_registry.py" accept \
     --source-host '<source-host>' \
     --child-host '<child-host>' \
     --child-thread '<child-thread>' \
     --status '<status>' \
     --sequence '<sequence>' \
     --event-id '<event-id>'
   ```

If `wait_threads` reports a terminal/attention state before a callback arrives,
fresh-read the child, handle it, then record the observed state with `observe`.
This makes a later copy of the same callback a duplicate.

```bash
python3 "$HOME/.codex/bin/task_delegation_registry.py" observe \
  --source-host '<source-host>' \
  --child-host '<child-host>' \
  --child-thread '<child-thread>' \
  --status '<status>'
```

Never echo a delegation event back to the child. A normal source-to-child
follow-up still requires a fresh child read. When work resumes after an
attention state, both roles record the transition; the next event then gets a
new sequence:

```bash
python3 "$HOME/.codex/bin/task_delegation_registry.py" resume \
  --source-host '<source-host>' \
  --source-thread '<source-thread>' \
  --child-host '<child-host>' \
  --child-thread '<child-thread>' \
  --as-role source
```

Ask the child to run the same command with `--as-role child`.

## Restart and duplicate recovery

On source resume after an App/process crash:

```bash
python3 "$HOME/.codex/bin/task_delegation_registry.py" recover-source \
  --source-host '<source-host>'
```

Use returned `waitTargets` in `wait_threads` with `timeoutMs: 0`, in batches of
at most eight. Fresh-read any changed child, then `observe` it. After the
snapshot, keep one bounded event wait for still-running children; callbacks
cover children outside the active batch.

On child resume:

```bash
python3 "$HOME/.codex/bin/task_delegation_registry.py" recover-child \
  --child-host '<child-host>'
```

For a `pending` event, fresh-read the source. If the exact event marker is
already visible, mark it sent without resending; otherwise send it once and
mark it sent. Do not automatically resend a `sent` event. The source's wait
snapshot is the recovery path for a send/receipt crash window.

Repeated `prepare`, `mark-sent`, and `accept` calls are idempotent. Ignore an
accepted duplicate or older sequence. Never auto-archive or delete either task.

If every command rejects a private registry as malformed or unsupported, use
the explicit repair only after recording the affected task IDs elsewhere:

```bash
python3 "$HOME/.codex/bin/task_delegation_registry.py" repair \
  --confirm-quarantine
```

This keeps the invalid mode-0600 file beside the new empty registry. Rebuild
source registrations from the source conversations and take immediate
`wait_threads` snapshots; do not delete the quarantined copy automatically.

## User-facing behavior

Keep updates short: name the child task while it runs; report its verdict when
it returns; surface only a real blocker or decision. Never ask the user to act
as the message bus.
