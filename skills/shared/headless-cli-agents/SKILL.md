---
name: headless-cli-agents
description: "Use when delegating implementation, research, or review to a headless AI CLI (codex exec, grok -p, claude -p) — read-only or write mode — or when picking which provider's quota to spend on a worker. Covers the sandbox profile that makes write mode safe, the spec contract, and acceptance rules; provider priority itself lives in the worker-routing SSOT."
allowed-tools: Bash
---

# Headless CLI agents

Loaded by Claude Code, Codex, and Grok alike (Grok discovers it through `~/.claude/skills`).

## Workflow

1. Run `scripts/pick-worker` (in Claude Code with `dangerouslyDisableSandbox: true`: codexbar writes its
   cookie cache and fails inside the sandbox). It prints remaining quota, a recommendation with a reason,
   and the matching `runbook/<provider>.md`. `--provider <name>` forces
   one; `--quiet` prints only the recommendation.
2. **If the recommended provider is the runtime you are running in, use your native subagent**
   (Claude Code: `Agent` tool; Codex: built-in subagent; Grok: `spawn_subagent`). Never shell out to
   your own CLI. The CLI lane in each runbook is for callers on a *different* runtime.
3. Write the spec (contract below), dispatch per the runbook, then apply the acceptance rules.

## Three absolute rules

1. **Write mode needs the sandbox profile.** Any headless CLI that may touch files runs under a kernel
   sandbox profile that limits writes to the worktree, denies *reading* credential paths, and turns
   network off where the platform supports it. No profile → read-only only.
2. **Never bypass.** `danger-full-access`, `--dangerously-bypass-*`, `--yolo`, `bypassPermissions` are
   banned in every mode, no exceptions.
3. **A CLI with its own sandbox runs outside Claude Code's Bash sandbox** (`dangerouslyDisableSandbox: true`;
   nested Seatbelt fails with `sandbox initialization failed`) and gets absolute paths — `$TMPDIR`
   differs inside and outside the sandbox.

## Spec contract (six parts, every delegation)

objective · files in scope · interfaces (signatures, schemas, CLI contracts to honor) · constraints ·
verification command · reasoning effort. Put it in a file and pass the absolute path.

## Acceptance

- The controller re-runs the verification command itself; the worker's "tests pass" is a claim, not proof.
- "Done" with an empty diff is a refusal (often the worker's own instructions blocked it), never a success.
- Check quota before delegating (`pick-worker` does it); routing beyond that is `~/dotfiles/codex/notes/worker-routing.md`.
