---
name: "daily-loop"
description: "Run the daily self-improvement loop: mine the last 24h of Claude Code and Codex transcripts, produce a digest of how the user worked, then propose concrete improvements (a new skill, a CLAUDE.md/AGENTS.md rule, or a helper-script change) for the user to approve. Use when the user asks to run the daily loop, review yesterday's sessions, or find workflow improvements from recent transcripts."
---

# daily-loop

A **closed self-improvement loop**: mine the last 24 hours of agent transcripts,
distill how the user actually worked, then propose a small number of concrete,
high-value improvements. The user is the approval gate — this skill **proposes,
it never silently rewrites** `CLAUDE.md`, `AGENTS.md`, skills, or config.

Inspired by loop engineering: explore → plan → execute → verify → iterate, with
a quality gate so the loop improves things instead of generating noise.

## When to use

- The user asks to run the daily loop / `/daily-loop`, review yesterday, or
  "find what I can improve from how I worked recently".

## When NOT to use (route elsewhere)

- "Remember this / save this guidance" → the `remember` skill.
- "Wrap up this session / commit + push" → the `wrap` skill.
- "Change a permission / settings.json / hook" → route to the owning config or
  skill workflow. daily-loop only *proposes* such changes; it does not apply
  them directly.

## Core principle: closed loop, user is the gate

```
explore (run extractor) → plan (cluster patterns) → propose
   → USER APPROVES → execute (delegate to the right skill) → record (state log)
   → iterate next day
```

Never edit `CLAUDE.md` / `AGENTS.md` / a skill / config before the user approves.

## The shared substrate

All transcript reading is done by one bash helper (works for both Claude Code
and Codex; it is the cross-tool substrate):

```
"$HOME/dotfiles/skills/shared/daily-loop/scripts/mine_transcripts.sh" --since 24
```

It is a **data extractor only**: it aggregates counts and samples truncated
user-message snippets into a compact digest. It never proposes or edits. Do not
read the raw `.jsonl` yourself — that wastes context; trust the digest.

Useful flags: `--since HOURS`, `--format md|json`, `--max-snippets N`,
`--snippet-chars N`, `--source all|claude|codex`, `--debug`. Run
`mine_transcripts.sh --help` for the full list.

## Workflow

### Step 1 — Extract

Run the helper (default `--since 24`, `--format md`) and read its stdout digest.
The digest has three parts: an Overview (session/turn/tool/error totals), a
per-project breakdown (tools, hot shell binaries, representative asks), and
script-computed Cross-cutting signals (high-frequency shell binaries, recurring
ask openers). These signals are raw frequency only — **you** do the judging.

### Step 2 — Read prior state

Read `$HOME/scratch/daily-loop/state.jsonl` (may not exist yet — that's fine).
It is an append-only log of what was already proposed, with status
`accepted | rejected | deferred`. Anything already there is off the table unless
it is clearly, materially recurring again.

### Step 3 — Spot improvement candidates (judgment)

Look for, in priority order:

1. A **recurring multi-step interaction shape** across ≥2 sessions / ≥2 days
   → candidate for a **new skill**. (e.g. a repeated "remind me where we were"
   opener → a resume/catch-up skill.)
2. A **preference or instruction the user keeps re-typing** → candidate for a
   **`CLAUDE.md` / `AGENTS.md` rule** (route via the `remember` skill's layering:
   normative→AGENTS.md, quirk→notes).
3. A **hot manual shell binary** or a repeated permission prompt → candidate for
   a **helper-script change or an allowlist entry** (route to the owning config
   workflow or edit the relevant existing script after approval).
4. **Friction signals**: a project with a high error-ish count or repeated
   retries → worth surfacing even without a clean fix.

### Step 4 — Verify each candidate (quality gate)

Before proposing, each candidate must pass ALL of:

- **Frequency**: seen in ≥2 distinct sessions OR ≥2 days. One-offs are noise.
- **Durability**: it would help a *future* session, not session-specific state.
- **Non-duplication**: not already covered by an existing skill / rule, nor
  already in the state log.
- **Concreteness**: you can name the exact target file and the exact change.

Drop anything that fails. **Prefer proposing 0–2 strong items over 6 weak ones.**
For a high-impact proposal, optionally ask a separate sub-agent / another Codex
to independently sanity-check it (the "separate verification" building block) —
only when the payoff justifies the cost.

### Step 5 — Present proposals (approval gate)

Present a short ranked report. Each proposal must include three things:

- **what and where**: type plus exact target file / workflow owner.
- **why now**: digest-backed evidence and expected payoff.
- **proposed edit**: the exact rule, script change, or skill outline.

Then ask the user which to act on:

- In Claude Code: use `AskUserQuestion` with one option per proposal plus a
  "none" choice.
- In Codex or any tool without `AskUserQuestion`: present a numbered list and
  ask the user to reply with the numbers to act on (e.g. `Y` / `n` / `[1,3]`).

**Do not edit anything before the user approves.**

### Step 6 — Execute approved items (delegate, don't freestyle)

- rule / memory → the `remember` skill (it owns the AGENTS.md/CLAUDE.md/notes
  layering)
- new skill → the owning skill authoring workflow
- settings / permissions / hooks → the relevant config owner
- change to an existing helper script → a normal edit, user-confirmed

daily-loop itself does not write `CLAUDE.md` / `AGENTS.md` / config; it routes.

### Step 7 — Record outcome to the state log

Append one JSON line per proposal to `$HOME/scratch/daily-loop/state.jsonl`
(create the directory if missing):

```json
{"ts":"<ISO8601>","day":"<YYYY-MM-DD>","type":"new-skill|rule|script-change","fingerprint":"<stable-hash>","target_file":"<path>","summary":"<one line>","status":"accepted|rejected|deferred"}
```

The `fingerprint` is a stable identifier for the idea (type + normalized target +
pattern key) so tomorrow's run won't re-propose the same thing. Record rejected
and deferred items too — that is how the loop stops nagging.

## Cross-tool note

This SKILL.md is read by both Claude Code and Codex. The bash extractor is the
shared substrate; everything above it is plain reasoning that works for either.
Where a step names a Claude-Code-only mechanism (`AskUserQuestion`, `/loop`), a
fallback is given for other tools. Do not assume a Claude-only tool exists.

## Token-cost awareness

Run this once per day. Always reason over the digest, never over raw `.jsonl`.
Keep the final proposal set to the top 1–3. The loop is bounded by design.

## State & privacy

State and optional digest archives live in `$HOME/scratch/daily-loop/`
(outside any git repo). Snippets are verbatim user prompts — keep them local;
do not commit `~/scratch/daily-loop/` anywhere.
