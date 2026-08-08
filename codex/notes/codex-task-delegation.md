# Codex App delegated-task return contract

Verified 2026-08-09 with ChatGPT desktop app `26.803.41515` and
`codex-cli 0.147.0`.

## Capability boundary and root cause

The missing completion message is not a `Stop` hook bug. Codex hooks observe a
single conversation's agent loop:

- The official [Hooks documentation](https://learn.chatgpt.com/docs/hooks)
  lists `Stop` and `SubagentStop` as turn/subagent events. `Stop` can continue
  the same turn; it has no child App task lifecycle payload.
- `SessionEnd` runs when a main conversation is archived/deleted, Codex closes,
  or an unopened conversation has been idle for 30 minutes. It is advisory and
  is not another task's completion event.
- The installed hook payloads and repo `codex/hooks.json` therefore cannot know
  that an independently created App task finished. Expanding the global Stop
  hook would only create a heuristic UX hook with false positives.

The App has the correct coordination primitives. Installed tool schemas in
desktop app `26.803.41515` establish that:

- `create_thread` is asynchronous and returns a ready `threadId`/`hostId` or a
  setup-only `clientThreadId`.
- `wait_threads` waits for the first of up to eight tasks to complete or need
  attention, supports per-task cursors, does not wake on commentary, and can do
  an immediate recovery snapshot with `timeoutMs: 0`.
- `read_thread` performs a non-resuming fresh read.
- `send_message_to_thread` sends a follow-up prompt in the background. Unlike a
  sidebar status change, this input starts/wakes the source task.

The official [App Server documentation](https://learn.chatgpt.com/docs/app-server)
also exposes `turn/completed` and `thread/status/changed` on an actively read
transport stream. Building another transport listener would require a
long-lived client and still need a supported way to wake the existing App task.
That is more complex than the App's injected `wait_threads` and message tools,
so this workflow does not create a daemon or call App Server directly.

## Event contract

One delegation binds two qualified endpoints:

| Field | Meaning |
| --- | --- |
| `source.host` + `source.thread` | Task that owns follow-up |
| `child.host` + `child.thread` | Delegated task; cannot equal source |
| `status` | `running`, `completed`, `blocked`, or `needs-attention` |
| `cursor` | Latest opaque `wait_threads` cursor for this child |
| `sequence` | Monotonic child event occurrence |
| `eventId` | Digest of both qualified endpoints, status, and sequence |
| `delivery` | Child outbox state: `pending` or `sent` |
| `receipt` | Source state: `none`, `unacknowledged`, or `acknowledged` |

The callback message contains only this envelope and a fixed instruction. It
does not contain prompts, final answers, browser data, tokens, or personal data.
The source always fresh-reads the child because the callback is only a wake
signal.

`eventId` is an idempotency key, not an authentication token. Fresh-read is an
agent-enforced App-tool ordering rule; the registry cannot independently prove
that a read happened because it deliberately has no App API access.

## Delivery and recovery semantics

The protocol is at-least-once wake delivery with idempotent handling:

1. Source registers the ready child, then waits with `wait_threads`.
2. Child atomically records a pending event.
3. Child fresh-reads the exact source immediately before sending.
4. `send_message_to_thread` wakes the source; child records `sent` only after
   success.
5. Source fresh-reads the child, handles the result, then acknowledges the
   deterministic event.

Failure behavior is conservative:

| Failure | Recovery |
| --- | --- |
| Source missing/archived/unreadable | Do not send; keep child event pending |
| Crash before send | Child `recover-child` finds pending outbox |
| Crash after send but before `mark-sent` | Fresh source read finds the same marker; mark without resending |
| Callback absent or child lacks tools | Source `wait_threads` returns the child state |
| Source/App restart | `recover-source` rebuilds wait targets; use `timeoutMs: 0` snapshot |
| Duplicate callback | Same event/sequence is acknowledged once; later copies are ignored |
| Older delayed event | Lower accepted sequence is stale and ignored |
| Multiple children | Registry keeps independent qualified records; wait in batches of eight |
| Same thread or conflicting source | Registry rejects self-notification and rebinding |
| Malformed or unsupported private registry | Explicit `repair --confirm-quarantine` preserves the invalid mode-0600 file, starts empty, then sources rebuild registrations and snapshot children |

`notLoaded` is a normal runtime state, not an unavailable source: a successful
fresh read permits the child to send and wake it. A read error, missing exact
host/thread, or archived/deleted task does not.

## Private state

`codex/bin/task_delegation_registry.py` writes only to
`${CODEX_HOME:-~/.codex}/state/task-delegations/`:

- directory mode `0700`; registry and lock files mode `0600`;
- same-user, regular-file, non-symlink validation;
- locked read/modify/write and atomic replace with `fsync`;
- no prompt, final answer, browser data, token, credential, or personal data.

State is host-local, not synchronized. Both endpoints are host-qualified, and
each participating host needs the helper installed. For a remote child, its
outbox survives on that host while the source registry and `wait_threads`
snapshot independently reconcile the child from the source host.

The registry currently retains settled delegation and outbox metadata so old
receipts remain auditable; there is no automatic prune. Repair never deletes its
quarantined input, and no workflow should remove it without an explicit cleanup
decision.

The helper does not call App APIs, poll, archive, delete, or send messages. The
`codex-task-return` skill owns the App-tool sequence and the always-loaded
`codex/AGENTS.md` routes every Codex task delegation through it.

An isolated projectless source/child smoke on 2026-08-09 also verified the live
App path: the child fresh-read and messaged an idle source, the source started a
new turn, fresh-read the child's final answer, and accepted the receipt. The
reproducible fake-tool E2E remains in `codex/tests/test_task_delegation_registry.py`
for completion, attention states, duplicates, unavailable source, and restart.
