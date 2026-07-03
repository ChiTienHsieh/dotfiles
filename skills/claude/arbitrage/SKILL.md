---
name: arbitrage
description: "Use in Claude Code when implementation work is being planned or delegated, to keep Claude focused on judgment while routing code-writing work to observable Codex sessions through tmux."
---

# Arbitrage

This skill adapts `blader/arbitrage` for this machine's Claude + Codex workflow.
The core idea stays the same: Claude spends attention on judgment, planning,
design intent, verification, diff review, and git ownership; Codex does the
bulk implementation work.

On this machine, implementation is delegated to an observable interactive Codex
surface via `tmux-orchestration`, not file-mutating headless `codex exec`. The
user wants observable Codex TUI sessions that can be watched, interrupted,
nudged, or switched to `/fast` manually. Read-only headless Codex is fine for
the controller's own verification or research.

## When To Use

- Use when Claude Code is planning implementation work that would benefit from a
  separate Codex worker.
- Use when work needs a spec, acceptance criteria, and a visible implementation
  surface.
- Use for frontend implementation when Claude should preserve design intent and
  perform visual validation after Codex edits.
- Do not use for tiny one-line edits where delegation overhead is larger than
  the work.
- Do not use inside Codex as a reason for Codex to delegate to itself.

## Routing Table

| Work | Owner | Notes |
| --- | --- | --- |
| Product judgment, scope, architecture, constraints | Claude | Keep the thinking here. |
| Spec writing and acceptance criteria | Claude | Make the worker prompt precise. |
| Bulk code edits and test-driven implementation | Codex in tmux | Use an observable surface. |
| Frontend visual validation | Claude | Run, inspect, screenshot, and judge. |
| Debugging analysis | Claude first | Delegate the concrete fix after root cause is clear. |
| Diff review, commit, push, PR | Claude | Git ownership stays in the controller session. |
| Small follow-up edits | Claude | Avoid delegation theater. |

## Model Allocation

Choose models by task difficulty and output quality requirements. For normal
delegation, cheaper models are fine for mechanical work; stronger or more
tasteful models are better for UI, copy, API design, plan review, and
architecture.

When exact model routing matters, read `references/model-routing.md`.

## Dispatch Protocol

Use `tmux-orchestration` for delegated implementation and follow its Delegation
Contract for prompt files, observable Codex TUI surfaces, marker reports, and
controller-side verification. Do not delegate file-mutating work via headless
`codex exec`; read-only headless Codex remains allowed for controller-side
verification or research.

1. Inspect the repo state, dirty files, stop conditions, and relevant docs.
2. Write a worker prompt that captures objective, allowed scope, constraints,
   acceptance criteria, verification, and report marker.
3. Dispatch through the `tmux-orchestration` Delegation Contract.
4. Verify worker claims and review the diff before committing or pushing.

## Frontend Validation Loop

1. Claude writes design intent and acceptance criteria in the worker prompt.
2. Codex implements in a visible tmux surface.
3. Claude runs the app, inspects the UI, and takes screenshots when useful.
4. Claude writes concrete visual feedback and re-dispatches if needed.
5. Stop when the UI matches intent and verification passes.

## Escape Hatch

Do not predict that Codex will fail. Dispatch first when the work is suitable.
If a worker misses the acceptance criteria twice after concrete corrective
feedback, Claude should stop re-dispatching, keep the useful parts of the diff,
and finish the implementation directly.

## Upstream

Adapted from `blader/arbitrage` at
`ccfd55098cc9e0b9910bc5c0f67a16a2fd61d5bd`.
