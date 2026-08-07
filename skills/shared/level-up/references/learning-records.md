# Learning Records and Silent Bookkeeping

Use persistent records to shape future teaching, never as learner-facing output.

## Contents

- Silent output boundary
- Read before teaching
- Evidence and skip events
- Index/topic shapes
- Profile updates
- Privacy and safety

## Silent Output Boundary

Keep two channels strictly separate:

- **Silent side effects:** edits to `learning/`, memory, or private notes.
- **User-facing output:** only the lesson, the current question, and the answer
  the learner needs now. This includes chat, tmux output, Telegram, progress
  lines, status updates, final replies, PR notes, and handoff reports.

Never show record paths, “record updated,” Known Gaps, waiting-for-level text,
XP/level bookkeeping, option-letter history, or model prefixes. Mention a record
update only when the user explicitly asks.

## Read Before Teaching

Inspect this skill's `learning/` directory:

```text
learning/
├── INDEX.md
├── user-profile.md
└── topics/
    └── <topic-slug>.md
```

If the structure is missing, create it. Then:

1. Read `learning/INDEX.md` for topic routing, status, evidence, and pointers.
2. Read `learning/user-profile.md` for the learner's taste and proven analogy
   frames.
3. Search `learning/topics/` for the topic and nearby prerequisites.
4. Trust only evidence-backed records; assess an unrecorded topic from scratch.

Use zh-tw prose by default and keep technical terms in English when clearer.

## What to Record

Update records after every completed level and at session end. Record only state
that can change a future lesson:

- `mastered`: applied or answered the concept correctly in context.
- `familiar`: showed partial fluency but may still need scaffolding.
- `learning`: actively working on the concept.
- `gap`: showed a misconception, missing prerequisite, or repeated uncertainty.
- `skip_for_now`: intentionally deferred scope.

Record evidence at concept level: demonstrated concepts, corrected
misconceptions, unresolved gaps, and self-reported prior knowledge. Record the
learner's concrete goal and the substance of confirmed shotcall decisions.

Do not record level numbers, MCQ option letters, correct-answer positions, XP,
or other session-only mechanics. They do not shape teaching and can leak future
answers.

## Skip Events

When the learner skips a `preflight` or `debrief`, silently append a dated event
under `## Workflow Events` in the relevant topic file. If no topic record exists,
append to `learning/workflow-events.md`; do not create a topic without learning
evidence. Record a reason only when the learner supplied one. Do not change
`Current Level` or `learning/INDEX.md` status.

## Index and Topic Shape

Keep `learning/INDEX.md` short and sortable:

```markdown
| Topic | Status | Evidence | Updated | File |
| --- | --- | --- | --- | --- |
| Python async | familiar | Distinguished concurrency from parallelism. | 2026-06-10 | topics/python-async.md |
```

Use stable lowercase ASCII, hyphen-separated slugs such as
`python-async.md` or `llm-evals.md`. Each topic file uses:

```markdown
# <Topic>

## Learner Goal
- <concrete outcome stated in Level 0>

## Current Level
- Status:
- Last updated:
- Confidence:

## Evidence
- YYYY-MM-DD: ...

## Known Gaps
- ...

## Teaching Notes
- Use these examples:
- Avoid assuming:

## Next Suggested Levels
- ...
```

## Profile Updates

Record the selected analogy, depth, and medium in the topic file. If a framing
works across the course—or clearly fails—update `learning/user-profile.md` so a
future session can reuse or avoid it.

## Privacy and Safety

Never store secrets, tokens, client-specific facts, private code snippets, or
long chat transcripts. Keep evidence minimal and teaching-relevant.
