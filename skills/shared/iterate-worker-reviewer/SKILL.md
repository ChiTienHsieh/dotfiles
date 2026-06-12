---
name: "iterate-worker-reviewer"
description: "Compatibility alias for the legacy `iterate-worker-reviewer` workflow. Use when the user invokes `/iterate-worker-reviewer` or asks for worker/reviewer iteration; delegate to the `file-review-loop` skill."
disable-model-invocation: true
---

# iterate-worker-reviewer

This is a compatibility alias for the old Claude Code command.

Use `file-review-loop` as the authoritative workflow:

1. Read `../file-review-loop/SKILL.md`.
2. Treat the user's arguments as the task, target quality, and optional max iterations.
3. Run the Builder -> Reviewer -> report -> fix loop described there.

Do not maintain separate worker/reviewer rules here; update `file-review-loop` instead.
