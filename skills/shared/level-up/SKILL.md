---
name: "level-up"
description: "Run guided, staged teaching when the user asks for level-up coaching, staged questions, or progression through a topic. Also use for implementation preflight, debrief, merge-readiness quizzes, and decision-focused coaching: run preflight on your own for non-trivial or unfamiliar tasks and for changes to data models, architecture, user-facing behavior, or guardrail/SSOT files (see references/implementation-understanding-loop.md), and offer the post-implementation quiz before push; skip the ritual for small, safe edits. Uses persistent learning records to tailor future teaching."
---

# level-up

## Core Contract

- Let concept difficulty set the number of levels; use 3–15+ when needed.
- Advance only after the learner demonstrates understanding or makes the required decision.
- Keep the learner's stated goal as the course lens; it may reorder, add, or remove levels.
- Make teaching vivid and engaging when the learner profile calls for it; dry documentation is not a lesson.

## Reference Router

Load only the references needed for the current turn. Every reference is linked
directly here; do not depend on one reference to route to another.

- **Every level-up session:** read
  [`references/learning-records.md`](references/learning-records.md) before
  teaching and before any record update. It owns silent bookkeeping, evidence,
  user-goal persistence, skip events, topic/index structure, privacy, and safety.
- **Before a course starts or choices are not yet locked:** read
  [`references/level-0.md`](references/level-0.md). It owns the mandatory user
  checkpoint for goal, analogy, depth, and medium; do not teach before the user
  chooses.
- **When planning or teaching levels, handling mid-course questions, or
  finishing a course:** read
  [`references/teaching-engagement.md`](references/teaching-engagement.md). It
  owns engagement, pacing, level structure, task-plan use, and completion.
- **Before writing any quiz or shotcall, and before responding to its answer:**
  read [`references/mcq-and-response.md`](references/mcq-and-response.md). It
  owns one-question-at-a-time, anti-tell, distractor, shotcall, and retry rules.
- **When medium `h` is selected, an adaptive course may switch to HTML, or a
  renderer is delegated:** read
  [`references/html-presentation.md`](references/html-presentation.md). It owns
  artifact presentation, theme, renderer handoff, and the chat/HTML boundary.
- **For implementation planning, decision review, or understanding work:** read
  [`references/implementation-understanding-loop.md`](references/implementation-understanding-loop.md)
  for the risk-triggered pre/during/post model.
- **For “preflight” or pre-implementation coaching:** also read
  [`references/pre-implementation.md`](references/pre-implementation.md).
- **For “debrief,” post-implementation understanding, or a merge/push readiness
  quiz:** also read
  [`references/post-implementation.md`](references/post-implementation.md).

## Run the Session

1. Read the learning index, learner profile, and relevant topic evidence.
2. Select implementation references when the request is preflight/debrief work;
   otherwise use normal teaching mode.
3. Run Level 0 before locking the course. Wait for analogy, depth, and medium;
   use the stated goal when provided, otherwise use the standard mental-model
   lens.
4. Build or update the task plan when the tool exists. Start with one narrow
   level and adapt when answers reveal gaps or prerequisites.
5. Teach one concept or decision through the selected analogy and medium.
6. Ask exactly one authoritative question in chat: a quiz for understanding or
   a shotcall for a real decision. Wait for the answer before advancing.
7. Adapt to the answer on the same level, or advance and preview the next level.
8. Silently update learning records after each completed level and at session
   end. Never narrate bookkeeping unless the user explicitly asks.
9. Finish by summarizing what the learner demonstrated and offering practical
   next steps; keep celebration proportional.

## Non-Negotiable Guardrails

- Keep all bookkeeping off every user-visible surface, including progress and
  status messages. Never expose record paths or updates, `Known Gaps`, level
  bookkeeping, stored option-letter history, or model tags.
- Ask one substantive MCQ or shotcall at a time. A batch of questions is not a
  level-up interaction.
- The chat question is the sole authority for progression. Any quiz embedded in
  HTML is practice only and cannot advance the learner.
- Never override or silently change the learner's analogy, depth, medium, or
  stated goal. Ask at the Level 0 checkpoint or before an adaptive medium switch.
- Record only minimal, abstract evidence that can improve future teaching.
  Never store secrets, identifying or sensitive personal details,
  client-specific facts, private code, tokens, or long transcripts.
- For a skipped preflight/debrief, record only the silent workflow event; do not
  alter topic mastery or index status.
