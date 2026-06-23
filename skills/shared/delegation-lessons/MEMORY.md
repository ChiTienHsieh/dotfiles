# Delegation Lessons — shared index

Shared, agent-maintained lessons for the `tmux-orchestration` and
`cmux-orchestration` skills. Goal: read THIS small index every turn, then open only
the ONE relevant topic file. Never read every topic file each turn.

## How to maintain (read before editing)
- After a delegation, if you learned something durable, open the ONE relevant topic
  file and add or refine a concise lesson. Ensure this index has a one-line entry.
- Distill, don't accumulate: merge duplicates; delete incident-only wording once a
  general rule exists. If a topic file passes ~120 lines, compress it.
- Keep reusable commands; drop raw logs and one-off evidence.

## Topics
- [tmux driving](tmux-driving.md) — launching/observing Codex in tmux panes; sandbox/socket gotchas; send-keys hygiene
- [cmux events](cmux-events.md) — event-based completion watching; real `cmux events` flags; marker-file fallback
- [worker prompts](worker-prompts.md) — handoff-proof delegation prompts: fixed nouns, file+marker contract, read-only framing
- [verification](verification.md) — how the controller verifies worker output without redoing it
