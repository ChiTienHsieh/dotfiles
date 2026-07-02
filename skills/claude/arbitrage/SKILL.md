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

Use `tmux-orchestration` for delegated implementation. The contract is a prompt
file, an observable Codex TUI surface, a marker-file report, and controller-side
verification. Do not delegate file-mutating work via headless `codex exec`.

Read-only headless Codex is allowed for the controller's own verification or
research, such as `codex review` or `codex exec --sandbox read-only`.

1. Inspect the repo state, dirty files, stop conditions, and relevant docs.
2. Write a worker prompt file in an ignored scratch directory. Include:
   - objective;
   - exact files or areas the worker may touch;
   - constraints and non-goals;
   - acceptance criteria;
   - required verification commands;
   - report path and final marker line.
3. Start or reuse the appropriate tmux surface with interactive Codex.
4. Send a one-line instruction that points Codex at the prompt file and report
   path.
5. Observe the surface when useful. The user may manually intervene, tweak the
   prompt, approve actions, or enable `/fast`.
6. Wait for the marker-file report, then verify worker claims from the
   controller session.
7. Review the diff before committing or pushing.

## Delegation Surface Rules

- Follow the `tmux-orchestration` skill with tmux send-keys.
- Keep long prompts in files; do not paste large prompts directly into the TUI.
- Poll a marker file for completion instead of trusting terminal visual state.
- Never use YOLO, bypass, or danger flags.
- Never ask a worker to weaken sandboxing, disable approvals, touch secrets, or
  bypass guardrails.
- Use one Codex surface per coherent unit of work. Split at API or ownership
  boundaries, not in the middle of a tightly coupled change.

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
