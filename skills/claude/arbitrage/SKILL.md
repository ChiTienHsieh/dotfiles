---
name: arbitrage
description: "Use in Claude Code when implementation work is being planned or delegated, keeping Claude focused on judgment while routing suitable work to built-in subagents (provider per the worker-routing SSOT)."
---

# Arbitrage

This skill adapts `blader/arbitrage` for this machine's Claude + Codex workflow.
The core idea stays the same: Claude spends attention on judgment, planning,
design intent, verification, diff review, and git ownership; a delegated worker
does the bulk implementation work. Which provider serves as the worker is
decided by `~/dotfiles/codex/notes/worker-routing.md` (the worker-routing
SSOT), not by this skill.

On this machine, implementation is delegated to built-in subagents by default.
A headless CLI worker (Codex, Grok, nested Claude) may mutate files only under
the sandbox profile described in the `headless-cli-agents` skill; without one it
stays read-only. Tmux eligibility follows the human-only activation gate in
`codex/AGENTS.md`.

## When To Use

- Use when Claude Code is planning implementation work that would benefit from a
  separate worker.
- Use when work needs a spec, acceptance criteria, and a separate implementation
  owner.
- Use for frontend implementation when Claude should preserve design intent and
  perform visual validation after worker edits.
- Do not use for tiny one-line edits where delegation overhead is larger than
  the work.
- Do not use inside Codex as a reason for Codex to delegate to itself.

## Routing Table

| Work | Owner | Notes |
| --- | --- | --- |
| Product judgment, scope, architecture, constraints | Claude | Keep the thinking here. |
| Spec writing and acceptance criteria | Claude | Make the worker prompt precise. |
| Bulk code edits and test-driven implementation | Built-in subagent or sandboxed headless CLI worker (per SSOT) | Provider per SSOT when selectable. |
| Frontend visual validation | Claude | Run, inspect, screenshot, and judge. |
| Debugging analysis | Claude first | Delegate the concrete fix after root cause is clear. |
| Diff review, commit, push, PR | Claude | Git ownership stays in the controller session. |
| Small follow-up edits | Claude | Avoid delegation theater. |

## Claude Token Guardrails

Delegate by default when a task is about to burn Claude context on mechanical
iteration, even if each step looks trivial:

- More than ~20 same-shaped tool loops (read/grep/edit cycles, log trawling).
- SSH command batches against remote hosts.
- GitHub sweeps across many issues/PRs/runs.
- Broad web research with many fetches.

Claude keeps the judgment and the verification; the loop itself goes to a
worker.

## Model Allocation

Choose models by task difficulty and output quality requirements. For normal
delegation, cheaper models are fine for mechanical work; stronger or more
tasteful models are better for UI, copy, API design, plan review, and
architecture.

When exact model routing matters, read `references/model-routing.md`.

## Dispatch Protocol

Use Claude Code's built-in `Agent` subagents for delegated implementation and
keep controller-side verification and git ownership in the parent session. A
headless CLI worker may write files only under the `headless-cli-agents`
sandbox profile. If the current human explicitly asks you to use tmux, use
`tmux-orchestration` and follow its complete Delegation Contract instead.

1. Inspect the repo state, dirty files, stop conditions, and relevant docs.
2. Write a worker prompt that follows the Spec Contract below.
3. Dispatch to a built-in subagent with explicit ownership and side-effect boundaries.
4. Verify worker claims and review the diff before committing or pushing.

## Spec Contract

Every delegation prompt follows the six-part spec contract and acceptance
rules defined in the `headless-cli-agents` skill's SKILL.md; this skill does
not restate them.

## Frontend Validation Loop

1. Claude writes design intent and acceptance criteria in the worker prompt.
2. A built-in subagent implements within the assigned ownership boundary.
3. Claude runs the app, inspects the UI, and takes screenshots when useful.
4. Claude writes concrete visual feedback and re-dispatches if needed.
5. Stop when the UI matches intent and verification passes.

## Escape Hatch

Do not predict that the worker will fail. Dispatch first when the work is suitable.
If a worker misses the acceptance criteria twice after concrete corrective
feedback, Claude should stop re-dispatching, keep the useful parts of the diff,
and finish the implementation directly.

## Upstream

Adapted from `blader/arbitrage` at
`ccfd55098cc9e0b9910bc5c0f67a16a2fd61d5bd`.
