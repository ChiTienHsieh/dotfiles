---
name: headless-agents
description: Delegate tasks to headless AI agents (Codex CLI, Gemini CLI). Use when you need web research with citations, complex multi-file refactoring, or want to parallelize work across multiple AI systems. Codex excels at research (--search), Gemini is faster for quick generation.
allowed-tools: Bash
---

# Headless Agents Delegation

## Overview

Claude Code can delegate tasks to headless AI agents:
- **Codex CLI** (OpenAI) - Strong at research with `--search`, complex refactoring
- **Gemini CLI** (Google) - Fast execution, good for quick generation

## When to Use Which

```
Task Type                           Codex              Gemini
--------------------------------------------------------------------
Web research + analysis             --search flag      Limited
Multi-file refactoring              Best choice        Okay
Quick code generation               Slower             Fast (Flash)
Image/multimodal analysis           -i/--image         Native support
Complex debugging                   Thorough           Surface level
```

## Codex CLI Commands

### Research Task
```bash
OUTPUT_LOG="./ai_chatroom/{topic}/codex_task_log_cdx.jsonl"
codex --search exec --full-auto --json \
  -o "$OUTPUT_LOG" \
  "Task description...

  OUTPUT to ./ai_chatroom/{topic}/:
  - {task}_detail_cdx.md
  - {task}_summary_cdx.txt"
```

### Implementation Task
```bash
# Step 1: Check git status first
git status

# Step 2: Run Codex
OUTPUT_LOG="./ai_chatroom/{topic}/codex_impl_log_cdx.jsonl"
codex exec --full-auto --json \
  -o "$OUTPUT_LOG" \
  "Task description..."

# Step 3: Review changes
git status && git diff
```

### Key Flags
- `--full-auto` = `--sandbox workspace-write -a on-failure`
- `--search` = Enable web search (place BEFORE exec!)
- `--json` = JSONL event output
- `-o <FILE>` = Final message output file
- `-i, --image <FILE>` = Attach image(s)
- `-C <DIR>` = Working directory

### Sandbox Modes
- `read-only`: Cannot modify ANY files
- `workspace-write`: Can write to workspace (use for most tasks)

## Gemini CLI Commands

### Basic Headless
```bash
# Using alias (gmn = gemini --model gemini-3-pro-preview)
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

### Limitation
Gemini CLI cannot write files directly - must redirect stdout.

## File-Based Communication (ai_chatroom)

```
./ai_chatroom/{topic}/
├── codex_research_summary_cdx.txt    # Codex summary
├── codex_research_detail_cdx.md      # Codex details
├── gemini_analysis_gmn.md            # Gemini output
└── README_cld.md                     # CC executive summary
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
- Complex implementation: 10-15 minutes

## Workflow Example

```bash
# 1. Create workspace
mkdir -p ./ai_chatroom/feature-x/

# 2. Delegate research to Codex
codex --search exec --full-auto --json \
  -o "./ai_chatroom/feature-x/research_log_cdx.jsonl" \
  "Research best practices for X. Write to ./ai_chatroom/feature-x/"

# 3. Delegate quick task to Gemini (parallel)
gmn -p "Generate boilerplate for X" --quiet > ./ai_chatroom/feature-x/boilerplate_gmn.md

# 4. Read summaries, synthesize, present to user
```

## Configuration Files

- Codex: `~/.codex/AGENTS.md`
- Gemini: `~/.gemini/AGENTS.md`
- Both know to write to `./ai_chatroom/` with proper suffixes
