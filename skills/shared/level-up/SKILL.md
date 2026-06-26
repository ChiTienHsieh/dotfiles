---
name: "level-up"
description: "Run the `level-up` workflow when the user asks for level-up coaching, staged questions, or guided progression through a topic. Uses persistent learning records under this skill's learning/ directory to tailor future teaching."
---

# level-up

Use this skill when the user asks to run `level-up`, wants staged coaching, or wants an AI tutor to teach a topic level by level.

## Core Principle

- Concept difficulty decides the number of levels. Use 3-15+ levels as needed.
- Teach progressively. The user advances only after demonstrating understanding.
- Treat mid-journey questions as signal: answer briefly, then insert or defer them in the learning path.
- Persist only evidence-backed learning state. Record what the user proved, corrected, or said they already know; do not record "covered X" as learned.
- **Engagement is a requirement, not decoration.** The real competitor for the learner's attention is YouTube Shorts / Instagram Reels. If a level reads like documentation, the user switches tabs and abandons learning. Content must be more fun than the feed. See "Engagement-First Teaching" below.

## Engagement-First Teaching (compete with the attention economy)

A level is only useful if the user actually reads it instead of doom-scrolling. Optimize for "I can't stop reading," not "technically complete." This is non-negotiable for users who explicitly ask for it (check learning records / memory).

- **Carry the knowledge ON the analogy, not beside it.** Do NOT write a serious technical explanation and then bolt on a cute metaphor as garnish. Invert it: the analogy *is* the explanation. The learner should absorb the real concept by following the silly story, and only at the end map it back to the technical term in one short line.
- **Silly and vivid beats accurate-but-flat.** A ridiculous, concrete, scene-like metaphor wins over a correct dry paragraph. If a section sounds like a manual, rewrite it as a scene with characters doing something.
- **Minimize "serious mode" blocks.** Keep raw technical prose down to short anchor callouts (one line: "this is called X"). The bulk of each section should be the analogy/story. A good ratio is most-analogy, little-jargon.
- **Use a frame the learner actually lived.** Pick a game / show / hobby the user genuinely knows — verify era and exact terms (web-search if unsure) rather than guessing. A wrong-era or unfamiliar reference kills immersion. Record which framing landed in the user's learning file so the next session reuses it.
- **Reward + momentum.** Lean into game feel (XP bars, level-ups, NPC dialogue, loot) so finishing a level feels like progress, not homework.

### The learner's specific taste lives in their profile, not here

Do not hedge with "some learners prefer X" — tune to the actual person. Their concrete framing (favorite game and era, silliness intensity, what delights/frustrates them) lives in their **USER.md** profile (for Claude Code, imported via CLAUDE.md). The orchestrator reads that profile and bakes the framing into each per-level content spec it hands the rendering agent. Keep the generic engagement principles here; keep the person-specific taste in USER.md.

### Reference example (study this for tone — for the RENDERING agent, not the orchestrator)

`examples/level2-eav.html` in this skill directory is the gold-standard for tone, ratio, and layout. The rendering agent (the side Codex that builds the HTML) should open and study it before rendering a new level so the style stays consistent. The orchestrator does NOT need to read it — that wastes tokens; just point the renderer at it.

### Delegating HTML rendering to a side agent

When a side agent (e.g. Codex) renders the HTML:

- The orchestrator writes the full per-level content spec in zh-tw (orchestrator is better at the user's zh-tw voice); the side agent only renders, never invents lesson content.
- Tell the side agent to **read this `level-up` skill** (for the Engagement-First principles + this user's taste) **and study `examples/level2-eav.html`** before rendering. That way the style standard lives here once, instead of being re-pasted into every delegation prompt — saving the orchestrator's tokens.

## Persistent Learning Records

Before teaching, inspect the learning folder in this skill directory:

```text
learning/
├── INDEX.md
└── topics/
    └── <topic-slug>.md
```

If the folder or files are missing, create them in the same structure. Keep prose zh-tw by default and keep technical terms in English when clearer.

### What to Read First

1. Read `learning/INDEX.md` for the topic map, familiarity levels, and pointers.
2. Search `learning/topics/` for the current topic and nearby prerequisites.
3. Use records only when they include evidence. If a topic is unrecorded, assess from scratch.

### What to Record

Update records after each completed level and at session end. Record only learning state that can shape a future lesson:

- **mastered**: user answered or applied the idea correctly in context.
- **familiar**: user showed partial fluency but may still need scaffolding.
- **learning**: user is actively working on the idea.
- **gap**: user showed a misconception, missing prerequisite, or repeated uncertainty.
- **skip_for_now**: intentionally deferred scope.

Good evidence:

- Correct MCQ answer plus the reason, if the user explained one.
- A corrected misconception and the new phrasing that worked.
- A user statement like "I already know X", marked as self-report.
- A concrete task or scenario where the user applied the concept.

Do not store secrets, client-specific facts, private code snippets, tokens, or long chat transcripts. Summarize at the concept level.

### Index Rules

`learning/INDEX.md` is the routing table. Keep it short and sortable:

```markdown
| Topic | Status | Evidence | Updated | File |
| --- | --- | --- | --- | --- |
| Python async | familiar | Correctly distinguished concurrency vs parallelism in MCQ. | 2026-06-10 | topics/python-async.md |
```

Each `topics/<topic-slug>.md` should contain:

```markdown
# <Topic>

## Learner Goal
- Why the user wants this topic (the concrete outcome they stated in Level 0). Drives level ordering and the per-level lens.

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

Use stable topic slugs, lowercase ASCII, hyphen-separated, for example `python-async.md`, `fastapi-dependencies.md`, `llm-evals.md`.

## Level 0: Analogy & Depth Selection (互動起手式)

Before planning ANY levels, run Level 0. This is a mandatory interactive checkpoint — AI does NOT start teaching until the user chooses.

### The Goal: Build a Strong Mental Model

In the AI era, memorizing facts is worthless — AI can look them up faster. What matters is having a **mental model** that lets you:

- **Predict** what should happen before you see it
- **Transfer** the pattern to new situations AI hasn't told you about
- **Judge** whether AI's output makes sense or is hallucinated garbage

A good analogy isn't decoration — it IS the mental model. When the user finishes, they should be able to reason about the topic using the analogy's intuition, even in scenarios they've never seen.

### Why Level 0 Matters

Picking the wrong analogy = a weak mental model that doesn't transfer. AI must think carefully:

- **Shape of the topic**: Is it dynamic/static? Accumulative/resettable? Coordination/independent? Time-sensitive/permanent?
- **Carrying capacity**: Which analogy can "carry" the ENTIRE topic, not just L1? If an analogy only works for the first 2 levels, it's a bad pick — the mental model will be incomplete.
- **User's proven frames**: Check USER.md for analogies that already landed with this user. Prefer those unless the topic genuinely doesn't fit.

### Elicit the Learner's Goal (motivation lens)

The same topic taught toward different goals should produce different lessons. "Understand WAL" for a DBA, for an SSD-endurance debugger, and for someone trying to look hireable in a GitHub thread are three different courses. Before locking the level map, ask the user **why they want this** — the concrete outcome they're chasing, not just the topic name.

- **Ask, don't assume.** Pose one short open question in the Level 0 prompt, e.g. "順便說一下：你學這個是想達成什麼？(看懂某段對話 / 修某個 bug / 面試 / 純好奇 / 想被某社群看見…)". Offer a few example answers so it's easy to reply, but keep it open-ended.
- **Let the goal reshape the map.** Use the answer to reorder, add, or drop levels, and to pick a recurring **lens** — a per-level callout that ties each concept back to the user's goal (e.g. a "🎯 recruiter view" line showing how this exact technical move signals competence to maintainers).
- **The goal can override defaults.** A stated goal outranks the generic "solid mental model" default — chase what the user actually wants, even if it means going deeper on one branch and skipping another.
- **Record it.** Save the stated goal in the topic's learning file so future sessions stay aimed at it.
- If the user gives no goal or says "just teach me", fall back to the standard mental-model framing — do not block on it.

### Level 0 Output Format

AI presents:

0. **One goal question** (open-ended, with a few example answers) — what outcome the user is chasing. Weave its answer into the level map and the per-level lens.

1. **3 Analogy Options** — each with:
   - A one-line pitch (why this frame fits this topic)
   - "Carrying forecast" — which concepts it handles well, and where it might strain
   - Example mapping: one core concept → one scene from this analogy

2. **Depth Options** — numbered (1/2/3) so user can answer like "A2" or "B1":
   - 1) 輕鬆速成 — core mental model only; enough to predict the happy path and recognize when you're out of scope
   - 2) 紮實打底 — solid mental model; can predict common cases, handle typical edge cases, and know where the model breaks down
   - 3) 深挖細節 — comprehensive mental model; can reason about tricky trade-offs, explain "why not X", and extend the model to new scenarios

Then WAIT for user to choose. Do not assume. Do not proceed.

### Analogy Selection Discipline

- **Prefer proven frames** from user's profile (USER.md) — they're already validated.
- **One topic, one analogy** — never mix two game worlds or two metaphor systems mid-journey.
- **Carry the knowledge ON the analogy** — if you can't explain the concept THROUGH the story (not beside it), the analogy doesn't fit.
- **Verify before using** — if unsure about specific terms (game mechanics, era-specific content), web-search or ask user. Wrong-era references kill immersion.
- **Novelty is OK** — if no existing frame fits, propose a new one, but explain why the user's known frames don't work for this topic.

### After User Chooses

- Confirm the choice briefly
- NOW proceed to "Assess and Plan" — design the level map using the chosen analogy and depth
- Record the chosen analogy in the topic's learning file for future sessions

---

## Teaching Flow

### 1. Assess and Plan

- Read persistent learning records first.
- Identify what can be skipped, accelerated, reviewed, or split smaller.
- Analyze concept complexity and decide the initial level count.
- Immediately use the task plan tool when available:
  - List expected levels.
  - Mark the first level `in_progress`.
  - Mark a completed level as `completed` before moving on.
  - Adjust the plan when questions reveal missing prerequisites.

### 2. Level Structure

```text
Level N: <topic>
├── One short setup in chat
├── Clear explanation or visual-first material when useful
├── Key distinction / common mistake
├── MCQ or tiny application check
└── Learning-record update after the user passes or reveals a gap
```

Prefer one narrow win per level. Avoid dumping the whole map when the user needs one step.

### 3. Visual Material

When the topic benefits from diagrams, comparisons, or interactive reading:

- Put the main explanation in a self-contained HTML file in the current project, usually `explainer/` or `notes/`.
- Keep CSS/JS inline. Do not use external CDN, external fonts, or `<script src>`.
- Use zh-tw plain language and mobile-friendly layout.
- In chat, give only a short intro plus the absolute file path. Ask the user to read it before the MCQ.
- Verify the HTML has no external dependencies before handing it over:

```bash
grep -cE '<script src|href="http|cdn|@import url' <file>
```

If using a side agent to render HTML, give it a complete content spec and tell it to render only, not invent lesson content.

## MCQ Rules

- Use **bold** for the question. Do not use heading syntax.
- Put each option on its own line, without blank lines between options.
- Match difficulty to the current level.

### Anti-Tell Rules (avoid giving the answer away by shape)

The learner should pick the right answer by *reasoning*, not by spotting format tells. Two tells leak constantly — kill both:

- **Position must be genuinely varied.** Do NOT default to A or B. Across a session, spread the correct answer roughly evenly over A/B/C/D. Before finalizing, glance at the previous 2-3 levels' answer positions and deliberately pick a different slot. If your draft keeps landing on B, that is the tell — move it.
- **Length must not signal correctness.** The most common leak: the correct option is the longest, most detailed, most hedged ("...and X, which preserves Y"), while distractors are short. Test-savvy learners just pick the longest. Fix: make every option roughly the same length. Push the full justification into your post-answer explanation, NOT into the option text. The correct option should read as terse as the wrong ones.

### Distractor Design (make wrong answers genuinely tempting)

- **3 of the 4 options must be plausible.** Distractors should be wrong for a *subtle, real* reason — a common misconception, a half-truth, the right idea applied at the wrong layer, or a true statement that does not actually answer the question. Avoid distractors that are obviously absurd or trivially eliminated (those make it a 2-way guess).
- **Tune distractor sharpness to depth.** At depth 1 (輕鬆速成), one clear right answer with softer distractors is fine. At depth 2-3 (紮實打底 / 深挖細節), make distractors close enough that the learner must actually understand the distinction to rule them out — near-misses, not strawmen.
- **Exactly one option may be intentionally, purely dumb — for fun.** Include a single absurd/joke option that nobody would seriously pick, written to make the learner snort (e.g. a wildly wrong cause, a cartoon non-sequitur, a "delete the whole database" energy answer). Never make the funny option accidentally correct.

```markdown
**問題: <question>**

A) <option A>
B) <option B>
C) <option C>
D) <option D>

---
```

## Adaptive Response

### Correct Answer

- Confirm briefly.
- Explain why the answer works.
- Update the learning record for the level.
- Move to the next level and preview it.

### Wrong Answer

- Stay encouraging and stay on the same level.
- Re-explain from a different angle.
- Record the gap if it affects future teaching.
- Ask a new check question.
- After 2-3 misses, ask what part feels unclear.

### Repeated Misses

- 2 misses: use a simpler analogy or narrower example.
- 3 misses: isolate the prerequisite.
- 4+ misses: ask whether to split smaller, pause, or switch to a simpler concept.

## Mid-Journey Questions

Do not derail the lesson. Classify the question:

- **Immediate**: needed for current understanding or answerable in 1-2 sentences.
- **Insert before current level**: reveals missing prerequisite.
- **Defer**: advanced extension better taught later.

Update the task plan accordingly:

```text
done Level 1
done Level 2
todo Level 2-2: <inserted prerequisite>
in_progress Level 3
todo Level 5-2: <deferred question>
```

## Completion

At the end of a session:

1. Summarize what the user demonstrated, not just what was taught.
2. Update `learning/INDEX.md`.
3. Update or create relevant `learning/topics/<topic-slug>.md`.
4. List practical next steps or suggested next levels.
5. Keep celebration proportional. One kaomoji is enough unless the user clearly wants more.
