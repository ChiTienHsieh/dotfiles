---
name: headless-agents
description: "Delegate research, analysis, or bounded parallel work to headless AI agents (Codex CLI, Gemini CLI, Claude CLI). Use when the user says 'run codex on this'、「讓 gemini 查」, explicitly requests `claude -p` workers, wants a second opinion from another model, wants to fan out investigation across models, or authorizes isolated-worktree Claude implementation. Default to read-only; mutation requires the explicit isolated-worktree contract in this skill."
allowed-tools: Bash
---

# Headless Agents Delegation

## Overview

Claude Code can delegate tasks to headless AI agents:
- **Codex CLI** (OpenAI) - Strong at read-only research with `--search`
- **Gemini CLI** (Google) - Fast read-only analysis
- **Claude CLI** (Anthropic) - Subscription-backed analysis or explicitly
  authorized isolated-worktree implementation with `claude -p`

Headless means no interactive terminal UI; the orchestrator still owns process
supervision, logs, review, and integration. The default is **read-only** because
that keeps the blast radius near zero. A user may explicitly authorize mutating
Claude workers, but only under the isolated-worktree contract below.

## Mode Awareness (read this first)

- This skill is for **normal Claude Code sessions** doing cheap, read-only,
  detached headless work.
- If running as the **orchestrator persona** (`cldo`), or any time the work
  **writes files** or needs to be watched/interrupted, normally route it through
  `tmux-orchestration` instead.
- Exception: when the user directly asks for mutating `claude -p` workers, each
  worker MUST use its own disposable worktree and branch, own a bounded,
  non-overlapping scope, and have no permission to push, merge, deploy, mutate
  live systems, or edit outside that worktree. The orchestrator reviews and
  cherry-picks the resulting atomic commits.
- Rule of thumb:
  - read-only + no network → headless is fine (the safe default).
  - read-only + network (`--search`) → headless is OK **only over trusted
    inputs**, accepting the exfil/SSRF risk noted below; send untrusted or heavy
    web work to a tmux surface instead.
  - mutating without the explicit exception above → follow
    `tmux-orchestration`, never this skill.

## When to Use Which

```
Task Type                           Codex              Gemini          Claude Fable
---------------------------------------------------------------------------------
Read-only research                  Thorough           Fast            Deep synthesis
Image/multimodal analysis           -i/--image         Native support  Prompt-dependent
Debugging analysis (read-only)      Thorough           Surface level   Strong
Bounded implementation              tmux only          tmux only       Explicit exception
```

## Codex CLI Commands

### Research / debug — read-only, no network (default)

```bash
OUTPUT="${TMPDIR:-/tmp}/codex-research.md"
mkdir -p "$(dirname "$OUTPUT")"   # codex -o does NOT create missing parent dirs
codex exec -s read-only --skip-git-repo-check \
  -o "$OUTPUT" \
  "Task description...
   Summarize findings into your final message (it is captured to the -o file)."
```

- `-s read-only` cannot modify ANY files.
- `-o <FILE>` is written by the Codex harness, not by a model command, so it
  works fine under `read-only` — this is how you capture results without giving
  the agent write access.
- No `--search` here, so the sandbox blocks network. That network-off default is
  the real protection: even if the agent reads something sensitive, it cannot
  exfiltrate it to an arbitrary host.

### Web research — `--search` opt-in (network ON, higher risk)

Only add `--search` when the task genuinely needs the live web:

```bash
# NOTE: --search is a TOP-LEVEL flag — it goes BEFORE the `exec` subcommand.
# `codex exec --search ...` is rejected as an unexpected argument.
OUT="${TMPDIR:-/tmp}/codex-websearch.md"
mkdir -p "$(dirname "$OUT")"   # codex -o does NOT create missing parent dirs
codex --search exec -s read-only --skip-git-repo-check \
  -o "$OUT" \
  "Web research task..."
```

- Network ON turns "can read" into "can exfiltrate to anywhere", and opens
  prompt-injection / SSRF paths if the agent reads untrusted content (random
  repos, web pages, dependencies). See the orchestrator persona's reasoning.
- Use it only over trusted inputs, and treat the result as if anything readable
  on the machine could have left it. For heavier or less-trusted web work, prefer
  an observable tmux surface so a human can watch.

### Key Flags

- `-s, --sandbox <read-only|workspace-write|danger-full-access>` = sandbox policy
- `--search` = enable live web search (turns network ON). Top-level flag: write
  `codex --search exec ...`, NOT `codex exec --search ...`.
- `--json` = JSONL event output
- `-o, --output-last-message <FILE>` = final message output (works under read-only)
- `-i, --image <FILE>` = attach image(s)
- `-C, --cd <DIR>` = working directory root
- `--skip-git-repo-check` = allow running outside a Git repo
- Set the sandbox explicitly with `-s`. Never use `--dangerously-bypass-*`.

## Gemini CLI Commands

Gemini is NOT inherently read-only. Under a permissive approval mode
(`--yolo`, `--approval-mode=auto_edit`/`yolo`) or in a trusted folder, its
edit/write tools can mutate the workspace. To use it safely headless, treat it
like Codex: drive it with a `-p` prompt and capture text via stdout redirect,
and do NOT enable yolo / auto-edit approval modes. Anything that should change
files goes to a tmux surface, not a headless Gemini run.

### Basic Headless (read-only usage)
```bash
# gmn is an alias for `gemini`. Do not pass --yolo / --approval-mode=auto_edit
# for headless read-only work.
gmn -p "Task description" --output-format json --quiet > output.json
```

### With File Input
```bash
cat source.py | gmn -p "Analyze this code" --quiet > analysis.md
```

### Key Flags
- `-p, --prompt <TEXT>`: The task/prompt
- `-m, --model <MODEL>`: Model selection
- `--output-format <text|json>`: Output format
- `--quiet, -q`: Suppress spinners (essential for headless)

## Claude CLI Commands

`claude -p` bills against the user's Claude subscription. For nested
`claude -p` runs, use `--permission-mode auto`; `bypassPermissions` exits 1.
Keep headless Claude read-only unless the task is moved to an observable tmux
surface or the user explicitly authorizes the isolated-worktree exception.

### Read-only Fable pass

```bash
claude -p --model fable --effort medium --permission-mode auto --tools "" \
  "Read the supplied artifacts and return findings only. Do not edit files."
```

### Explicit isolated-worktree implementation

```bash
claude -p --model fable --effort medium --permission-mode auto \
  "Work only in the assigned worktree and named file scope. Run focused tests,
   make atomic commits, and report commit hashes. Do not push, merge, deploy,
   touch live systems, or edit outside the worktree."
```

Give each worker a distinct subsystem and name its forbidden overlaps. Preserve
unfinished worktrees when a worker exits so another agent can salvage the diff.

### Effort and quota

- Use `--effort medium` by default for Fable. It has been sufficient for repo
  archaeology, architecture decisions, implementation, and salvage review.
- Use `--effort max` only for genuinely ambiguous, high-risk reasoning where
  the expected marginal quality justifies much faster quota burn. Do not launch
  several broad max-effort workers before checking live quota.
- Check the `quota` skill before expensive fan-out and after any limit error.
  Keep CodexBar commands, reset handling, and provider routing in their existing
  SSOTs rather than duplicating them here.
- Empirical warning: three broad max-effort Fable workers exhausted one Claude
  five-hour session window in about 20 minutes. Treat that as one observation,
  not a stable plan entitlement or throughput promise.

## Timeout Guidelines

- Minimum: 4 minutes (240000ms)
- Research tasks: 10+ minutes (600000ms)
- Fable implementation workers: do not call a still-running process timed out
  before 60 minutes unless the process exits or emits an explicit fatal signal.
  Sparse output is not a timeout; keep polling without discarding its worktree.
- `You've hit your session limit` is quota exhaustion, not a timeout. Preserve
  partial commits and diffs, check the `quota` skill, then resume or salvage
  with another agent according to the user's model intent.

## Configuration Files

- Codex: `~/.codex/AGENTS.md`
- Gemini: `~/.gemini/GEMINI.md`
