---
name: craft-goal
description: Craft a reliable `/goal` handoff prompt for another Codex session. Use when the user wants help writing, shrinking, validating, or preparing a `/goal` prompt, especially when the task needs clarification, research, a task spec file, side-effect boundaries, or a quick smoke test before handoff.
metadata:
  short-description: Craft reliable /goal handoff prompts
---

# Craft Goal

Use this skill to turn a rough task idea into a `/goal` prompt that another Codex can execute without immediately falling over.

## Core Workflow

1. **Clarify the task**
   - Identify the desired outcome, target environment, required tools, and completion criteria.
   - Ask concise questions only when the missing detail changes the work, risk, or naming.
   - Resolve naming and scope decisions before drafting the final `/goal`.

2. **Separate brief from spec**
   - Keep the actual `/goal` prompt under the app limit, currently 4000 characters.
   - If the task is complex, write a tracked task spec file in the relevant repo, then make `/goal` reference that file.
   - Use an ignored temp file only for scratch drafts; use a tracked file when the next Codex must read it reliably.

3. **Define side effects**
   - State what local files may be read or edited.
   - State what external systems may be changed, such as VM config, Telegram, GitHub, Vercel, or browser state.
   - Explicitly forbid destructive, permission-sensitive, billing, credential, or broad-scope changes unless the user approves them.
   - Include whether the next Codex may commit or push.

4. **Do a quick feasibility check**
   - Inspect repo paths, relevant docs, commands, installed tools, or existing config enough to avoid a first-step failure.
   - If the prompt references a file, verify the file exists and is tracked when appropriate.
   - If the next Codex needs a local working tree, check `git status` and mention expected cleanliness or dirty state.
   - Do not run expensive, destructive, or high-risk checks just to make the prompt look complete.

5. **Draft the output**
   - Provide a short zh-tw brief for the user when helpful.
   - Provide the final `/goal` prompt in a code block.
   - Prefer imperative instructions, exact names, exact paths, and a concrete deliverable checklist.
   - Remove vague words such as "maybe" after decisions are made.

## `/goal` Prompt Shape

Use this structure when possible:

```text
Use <tools/capabilities>.

Follow <tracked task spec path> if present.

Goal:
<one concrete outcome>

Context:
- <only the context the next Codex needs>

Instructions:
1. Inspect current state first.
2. Make only the allowed changes.
3. Ask before <risky actions>.
4. Verify with <specific smoke test>.
5. Report <specific deliverables>.

Local side effects:
- May edit: <paths>
- Must not edit: <paths>
- Do not commit/push unless explicitly asked.
```

## Task Spec File Guidance

Create a task spec file when:

- The `/goal` prompt would exceed 4000 characters.
- The task has many steps, safety rules, or external systems.
- The next Codex needs exact config snippets, topic lists, command formats, or verification criteria.
- The task should be auditable later.

Choose the file location by repo convention:

- `runbook/` for operational setup, VM changes, config changes, and incident-style handoff.
- `studies/` for conceptual research or analysis.
- Existing project docs/spec folders when the repo already has a clear convention.
- Do not invent new top-level directories when the repo has explicit structure rules.

## Smoke Test Examples

- Check `git status --short`.
- Confirm referenced files exist with `test -f` or `rg --files`.
- Confirm a command exists with `command -v`.
- Run a narrow syntax check or targeted test if it is fast and safe.
- For external systems, inspect current state before writing instructions that assume names, IDs, branches, or resources.

## Final Response Checklist

Before handing the prompt to the user, make sure it includes:

- The chosen task name/scope.
- The short `/goal` prompt, under 4000 characters.
- Any tracked task spec path, if used.
- Local side effects and external side effects.
- Ask-first boundaries.
- Verification steps.
- Final report expectations.
