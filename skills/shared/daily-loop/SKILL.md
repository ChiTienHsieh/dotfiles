---
name: "daily-loop"
description: "Mine recent Claude Code and Codex transcripts, identify durable workflow improvements, and ask the user which proposals to apply. Use for the daily loop, reviews of recent sessions, or requests to find recurring workflow friction."
---

# daily-loop

Mine recent agent work, propose 0–2 durable improvements, and let the user choose
what to apply. Never rewrite rules, skills, scripts, or config before approval.

## Route direct requests elsewhere

- "Remember this / save this guidance" → follow the current memory policy.
- "Wrap up this session / commit + push" → the `wrap` skill.
- A direct config, permission, or hook change → use its owning workflow.

## Extract

Run the helper with checkpointing so the next digest can identify new sessions:

```bash
"$HOME/dotfiles/skills/shared/daily-loop/scripts/mine_transcripts.sh" --since 24 --checkpoint
```

Use its digest, not raw transcript `.jsonl`. Treat script-computed signals as
frequency hints, not conclusions. Run `mine_transcripts.sh --help` for options.

## Workflow

### 1. Read prior proposals

Read the `kind:"proposal"` records in
`$HOME/scratch/daily-loop/state.jsonl`; a missing file is normal. Do not repeat
an idea already recorded unless the digest shows clear material recurrence.

### 2. Find candidates

Look for, in priority order:

1. Recurring multi-step interaction → new skill.
2. Repeatedly retyped preference → rule, routed through the current memory policy.
3. Repeated manual command or permission prompt → helper/config improvement.
4. Repeated errors or retries → friction worth surfacing, even without a fix.

### 3. Apply the quality gate

Every proposal must pass all four checks:

- **Frequency**: seen in ≥2 distinct sessions OR ≥2 days. One-offs are noise.
- **Durability**: helps future sessions, not only the current task.
- **Non-duplication**: absent from existing rules, skills, and prior proposals.
- **Concreteness**: names the exact owner or target and exact change.

Drop any candidate that fails. Return no proposal when none qualifies.

### 4. Present proposals and ask

Rank at most two proposals. For each include:

- **What and where**: type plus exact target or workflow owner.
- **Why now**: digest evidence and expected payoff.
- **Proposed edit**: exact rule, script change, or skill outline.

Ask the user which items to apply. Use the runtime's structured choice mechanism
when available; otherwise use a numbered list with a "none" choice. Stop here
until the user approves specific items.

### 5. Route approved work

- Rule or memory → current memory/SSOT policy.
- New skill → skill authoring workflow.
- Config, permission, or hook → owning workflow.
- Existing helper → normal scoped implementation.

### 6. Record every proposal outcome

Append one `kind:"proposal"` JSON line per item, including rejected and deferred
items, to `$HOME/scratch/daily-loop/state.jsonl`:

```json
{"kind":"proposal","ts":"<ISO8601>","day":"<YYYY-MM-DD>","type":"new-skill|rule|script-change","fingerprint":"<stable-id>","target_file":"<path>","summary":"<one line>","status":"accepted|rejected|deferred"}
```

Build `fingerprint` from type, normalized target, and pattern key. The helper
alone writes `kind:"run"` records and owns their source-prefixed session keys;
do not hand-write run records.

## Privacy

Digest snippets are verbatim user prompts. Keep the digest and state under
`$HOME/scratch/daily-loop/`; never commit that directory.
