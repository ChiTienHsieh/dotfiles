---
name: worker-prompts
description: Writing delegation prompts that survive handoff to another agent.
type: delegation-lesson
updated: 2026-06-23
---

## Use when
Writing a prompt file for a delegated worker.

## Lessons
- Use fixed nouns "CC" and "user", never 你/我 — a relative pronoun flips referent when
  a different agent reads the prompt.
- Give an explicit completion contract: write output to PATH, end the file with one exact
  MARKER line. The controller polls the marker, not the visual "Working" state.
- State the side-effect boundary up front: READ-ONLY research, or exactly which paths may
  be edited, plus "do not commit/push" when the controller verifies first.
- Put long instructions in the file; keep the send-line a one-liner pointing at it.
