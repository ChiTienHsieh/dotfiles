---
name: "gu-log"
description: "Locate and route work across gu-log, gu-log-api, and gu-log-ios. Use for tasks involving any of those repos or the blog."
---

# gu-log

This skill only locates the repos and routes cross-repo work. Project workflows
belong in each repo.

1. Read `paths.local` in this skill directory to locate `gu-log`, `gu-log-api`,
   and `gu-log-ios`.
2. If it is missing, ask the user to copy `paths.local.example` to
   `paths.local` and fill in the checkout paths.
3. Choose the repo that owns the task. Once inside, read its root `AGENTS.md`
   when present and follow its bootstrap and topic routing. Otherwise inspect
   the repo-local instructions before acting.
4. Read sibling-repo context only when the task crosses repo boundaries.

Never copy machine-specific paths into tracked files or public artifacts.
