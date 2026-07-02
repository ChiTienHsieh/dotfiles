---
name: headless-agents
description: "Use to delegate research, refactors, generation, or parallel work to headless AI agents such as Codex CLI or Gemini CLI."
allowed-tools: Bash
---

# Headless Agents Delegation

## Overview

Claude Code can delegate tasks to headless AI agents:
- **Codex CLI** (OpenAI) - Strong at research with `--search`, complex refactoring
- **Gemini CLI** (Google) - Fast execution, good for quick generation

Headless means fire-and-forget: no human watches it run. That is only safe when
the blast radius is near zero, so the default here is **read-only**. Anything
that mutates files headlessly is the risky part — route it to an observable
surface instead (see Mode Awareness).

## Mode Awareness (read this first)

- This skill is for **normal Claude Code sessions** doing cheap, read-only,
  fire-and-forget headless work.
- If running as the **orchestrator persona** (`cldo`), or any time the work
  **writes files** or needs to be watched/interrupted, do NOT delegate it
  headlessly here. Route it to an observable interactive surface, picking the
  `tmux-orchestration` skill.
- Rule of thumb:
  - read-only + no network → headless is fine (the safe default).
  - read-only + network (`--search`) → headless is OK **only over trusted
    inputs**, accepting the exfil/SSRF risk noted below; send untrusted or heavy
    web work to a tmux surface instead.
  - mutating (writes files) → **always** an observable tmux surface, never
    headless.

## When to Use Which

```
Task Type                           Codex              Gemini
--------------------------------------------------------------------
Web research + analysis             --search flag      Limited
Multi-file refactoring              tmux surface       tmux surface
Quick code generation               Slower             Fast (Flash)
Image/multimodal analysis           -i/--image         Native support
Complex debugging (read-only)       Thorough           Surface level
```

## Codex CLI Commands (codex 0.141 syntax)

### Research / debug — read-only, no network (default)

```bash
OUTPUT="./ai_chatroom/{topic}/research_cdx.md"
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
OUT="./ai_chatroom/{topic}/websearch_cdx.md"
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

### Implementation / multi-file edits (mutating) — do NOT do headlessly

Mutating work must run where a human can watch and interrupt. Do not run
`codex exec -s workspace-write` (or higher) from this skill. Instead use the
`tmux-orchestration` skill.

### Key Flags (0.141)

- `-s, --sandbox <read-only|workspace-write|danger-full-access>` = sandbox policy
- `--search` = enable live web search (turns network ON). Top-level flag: write
  `codex --search exec ...`, NOT `codex exec --search ...`.
- `--json` = JSONL event output
- `-o, --output-last-message <FILE>` = final message output (works under read-only)
- `-i, --image <FILE>` = attach image(s)
- `-C, --cd <DIR>` = working directory root
- `--skip-git-repo-check` = allow running outside a Git repo
- Removed in 0.141: `--full-auto` (old alias for workspace-write). Set the
  sandbox explicitly with `-s` instead. Never use `--dangerously-bypass-*`.

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

## File-Based Communication (ai_chatroom)

```
./ai_chatroom/{topic}/
├── research_cdx.md         # Codex research output (via -o)
├── gemini_analysis_gmn.md  # Gemini output
└── README_cld.md           # CC executive summary
```

### File Naming Convention
- Codex: `*_cdx.txt`, `*_cdx.md`
- Gemini: `*_gmn.txt`, `*_gmn.md`
- Claude Code: `*_cld.txt`, `*_cld.md`

### Communication Language
- CC <-> User: zh-tw with English technical terms
- CC <-> Codex/Gemini: English (LLM-to-LLM)

## Timeout Guidelines

- Minimum: 4 minutes (240000ms)
- Research tasks: 10+ minutes (600000ms)

## Configuration Files

- Codex: `~/.codex/AGENTS.md`
- Gemini: `~/.gemini/AGENTS.md`
- Both know to write to `./ai_chatroom/` with proper suffixes
