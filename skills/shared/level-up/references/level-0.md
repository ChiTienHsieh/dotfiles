# Level 0: Goal, Analogy, Depth, and Medium

Run Level 0 before locking or teaching a course. This is a mandatory user-choice
checkpoint: privately sketch only enough level shapes to make a recommendation,
then wait. Do not start the lesson.

## Ask for the Learner's Goal

Ask one short open question about the concrete outcome, not just the topic.
Offer examples without constraining the answer, such as understanding a
conversation, fixing a bug, preparing for an interview, or pure curiosity.

The goal outranks the generic mental-model default. Use it to reorder, add, or
drop levels and to choose a recurring per-level lens. If the learner says “just
teach me” or gives no goal, use the standard mental-model course and do not
block.

## Select Analogies by Carrying Capacity

A useful analogy lets the learner predict unseen behavior, transfer the pattern,
and judge whether an AI explanation is coherent. Inspect the topic's shape:
dynamic/static, accumulative/resettable, coordination/independent, and
time-sensitive/permanent.

- Prefer a proven frame from `learning/user-profile.md` when it fits.
- If no proven frame fits, propose a new one and say why the known ones fail.
- Use one analogy world for the whole course; never mix metaphor systems.
- Reject a frame that carries only the first few levels.
- Teach knowledge through the scene, then map back to the technical term in one
  short line; do not bolt a metaphor onto dry prose.
- Verify uncertain game mechanics, era-specific facts, or exact terms with web
  research or the learner before using them.

## Present the Choice

Present all four parts in one Level 0 prompt:

0. **One goal question** — open-ended, with a few example outcomes.
1. **Three analogy options (A/B/C)** — each gets a one-line pitch, a carrying
   forecast, and one verified concept-to-scene mapping.
2. **One depth choice:**
   - `1` 輕鬆速成 — predict the happy path and recognize out-of-scope cases.
   - `2` 紮實打底 — handle common cases, typical edges, and model limits.
   - `3` 深挖細節 — reason through tricky tradeoffs and extend the model.
3. **One medium choice:**
   - `m` Chat Markdown — lesson and authoritative MCQ stay in chat.
   - `h` Self-contained HTML — lesson lives in HTML; chat keeps the short intro,
     absolute path, and authoritative MCQ.
   - `a` Adaptive — start in chat and ask before any later HTML switch.

Inspect the likely levels and mark one medium with ★. Explain the recommendation
in one sentence using the lesson's actual visual structure, interaction,
navigation, comparison density, code/diff readability, and switching cost. The
profile is an input, not an automatic reason to choose HTML.

Ask for uppercase analogy + depth number + lowercase medium, such as `A2m`,
`B1h`, or `C3a`. The recommendation is advisory. Never override the selection or
silently switch medium.

## Wait and Continue

Wait until the learner gives all three choices. Use a concrete goal when they
provide one; otherwise use the standard mental-model lens without blocking.
Then confirm briefly, record the lens and choices silently, and build the course
map around them. If an adaptive course would later benefit from HTML, explain
the concrete benefit and ask before switching.
