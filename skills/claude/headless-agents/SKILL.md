---
name: headless-agents
description: "Delegate read-only research, analysis, or parallel investigation to headless AI agents (Codex CLI, Gemini CLI, Claude CLI). Use when the user says 'run codex on this'、「讓 gemini 查」, wants a second opinion from another model, wants to fan out research across models in parallel, or needs an independent read-only investigation that must not touch the working tree — even without naming a CLI."
allowed-tools: Bash
---

# Headless Agents Delegation

## Overview

Claude Code can delegate tasks to headless AI agents:
- **Codex CLI** (OpenAI) - Strong at read-only research with `--search`
- **Gemini CLI** (Google) - Fast read-only analysis
- **Claude CLI** (Anthropic) - Subscription-backed read-only analysis with `claude -p`

Headless means fire-and-forget: no human watches it run. That is only safe when
the blast radius is near zero, so the default here is **read-only**. Anything
that mutates files belongs in a built-in subagent or the controller session
instead (see Mode Awareness).

## Mode Awareness (read this first)

- This skill is for **normal Claude Code sessions** doing cheap, read-only,
  fire-and-forget headless work.
- If running as the **orchestrator persona** (`cldo`), or any time the work
  **writes files**, use a built-in `Agent` subagent or the controller session.
- Rule of thumb:
  - read-only + no network → headless is fine (the safe default).
  - read-only + network (`--search`) → headless is OK **only over trusted
    inputs**, accepting the exfil/SSRF risk noted below; send untrusted or heavy
    web work to a dedicated built-in research agent or approved web tool.
  - mutating (writes files) → built-in subagent or controller, never this skill.

## When to Use Which

```
Task Type                           Codex              Gemini
--------------------------------------------------------------------
Read-only research                  Thorough           Fast
Image/multimodal analysis           -i/--image         Native support
Debugging analysis (read-only)      Thorough           Surface level
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
  on the machine could have left it. For heavier or less-trusted web work, use a
  dedicated built-in research agent or approved web tool.

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
files goes to a built-in subagent or the controller, not a headless Gemini run.

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
Keep headless Claude read-only; use a built-in subagent for file mutations.

## Timeout Guidelines

- Minimum: 4 minutes (240000ms)
- Research tasks: 10+ minutes (600000ms)

## Configuration Files

- Codex: `~/.codex/AGENTS.md`
- Gemini: `~/.gemini/GEMINI.md`
