---
name: headless-agents
description: "Delegate one-shot, read-only research or analysis to headless AI agents (Codex CLI, Gemini CLI, Claude CLI). Use when the user explicitly asks for headless, detached, or `claude -p` workers, says 'run codex on this' or「讓 gemini 查」, or requests bounded parallel checks that need neither approval nor live steering. Generic second opinions and all file-mutating work follow worker-routing and tmux-orchestration instead."
allowed-tools: Bash
---

# Headless Agents Delegation

## Overview

Claude Code can delegate tasks to headless AI agents:
- **Codex CLI** (OpenAI) - Strong at read-only research with `--search`
- **Gemini CLI** (Google) - Fast read-only analysis
- **Claude CLI** (Anthropic) - One-shot analysis with `claude -p`

Headless means no interactive terminal UI; the orchestrator still owns process
supervision, logs, review, and integration. The default is **read-only** because
that keeps the blast radius small and matches the repository's observable-worker
policy. Route every file-mutating task through `worker-routing` and
`tmux-orchestration`, even when the user asks to use Claude.

## Mode Awareness (read this first)

- This skill is for **normal Claude Code sessions** doing bounded, read-only,
  one-shot headless work that needs no approval or live steering.
- If running as the **orchestrator persona** (`cldo`), or any time the work
  **writes files** or needs to be watched/interrupted, route it through
  `tmux-orchestration` instead.
- Rule of thumb:
  - read-only + no network → headless is fine (the safe default).
  - read-only + network (`--search`) → headless is OK **only over trusted
    inputs**, accepting the exfil/SSRF risk noted below; send untrusted or heavy
    web work to a tmux surface instead.
  - any mutation → follow `worker-routing` and `tmux-orchestration`, never this
    skill. A Git worktree isolates working files but is not a permission or
    network boundary.

## When to Use Which

```
Task Type                           Codex              Gemini          Claude
----------------------------------------------------------------------------
Read-only repo analysis              Supported          Supported       Supported
Live web research                    `--search`          Provider tool   Use tmux
Image/multimodal analysis            `-i/--image`        Provider tool   Use tmux
File-mutating implementation         Use tmux            Use tmux        Use tmux
```

Choose the provider and model through `codex/notes/worker-routing.md`; this
skill only defines the safe headless mechanics.

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

`claude -p` consumes Claude plan quota or API spend. Keep it read-only. Never
use a bypass-permissions flag; file-mutating work belongs on an observable tmux
surface.

### Pure artifact pass (stdin only)

```bash
claude -p --model fable --effort medium --permission-mode dontAsk \
  --safe-mode --no-chrome --strict-mcp-config \
  --mcp-config '{"mcpServers":{}}' --tools "" --no-session-persistence \
  "Analyze the artifact from stdin and return findings only." < "$INPUT"
```

This form disables built-in tools, customizations, Chrome, and inherited MCP
servers. The shell supplies the artifact through stdin, so the model does not
need file tools.

### Read-only repository pass

```bash
claude -p --model fable --effort medium --permission-mode dontAsk \
  --safe-mode --no-chrome --strict-mcp-config \
  --mcp-config '{"mcpServers":{}}' --tools "Read,Glob,Grep" \
  --no-session-persistence \
  "Inspect only the named repository paths and return findings. Do not edit."
```

Run this only from a trusted repository and give each worker a distinct scope.
`Read`, `Glob`, and `Grep` can send readable repository content to Anthropic;
exclude secrets and untrusted prompt-bearing inputs. If the task needs Bash,
network, writes, approvals, or live steering, use tmux instead.

### Effort and quota

- Use `--effort medium` by default for Fable. It has been sufficient for repo
  archaeology, architecture decisions, implementation, and salvage review.
- Use `--effort max` only for genuinely ambiguous, high-risk reasoning where
  the expected marginal quality justifies much faster quota burn. Do not launch
  several broad max-effort workers before checking live quota.
- Check the `quota` skill before expensive fan-out and after any limit error.
  Keep CodexBar commands, reset handling, and provider routing in their existing
  SSOTs rather than duplicating them here.

## Timeout Guidelines

- Minimum: 4 minutes (240000ms)
- Research tasks: 10+ minutes (600000ms)
- Judge progress by process state and meaningful output, not sparse stdout
  alone. Follow `tmux-orchestration` for observation cadence and intervention;
  do not invent a separate fixed no-progress window here.
- `You've hit your session limit` is quota exhaustion, not a timeout. Preserve
  captured output, check the `quota` skill, then resume or reroute according to
  the user's model intent.

## Configuration Files

- Codex: `~/.codex/AGENTS.md`
- Gemini: `~/.gemini/GEMINI.md`
