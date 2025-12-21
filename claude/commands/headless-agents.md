---
description: Load headless agent delegation strategy for Codex CLI and Gemini CLI
allowed-tools: [Bash]
---

Read the strategy below and apply it when delegating tasks to Codex CLI or Gemini CLI.

<headless-agents-strategy>
# Headless Agents Delegation Strategy (Dec 2025)

## Overview

Claude Code (CC) can delegate tasks to two headless AI agents:
- **Codex CLI** (OpenAI) - Strong at research with `--search`, complex refactoring, multi-file changes
- **Gemini CLI** (Google) - Fast execution, multimodal, good for quick generation tasks

## Role Mental Model

```
User (Junior Engineer)
    ↕️ 討論、學習、提問
Claude Code (Senior Engineer) - Orchestrator
    ↕️ 委派任務、解釋結果
    ├── Codex CLI (Distinguished Engineer) - Research + Implementation
    └── Gemini CLI (Staff Engineer) - Quick tasks + Multimodal
```

## When to Use Which Agent

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Task Type                           Codex CLI              Gemini CLI
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Web research + analysis             ✅ --search flag       ❌ Limited
Multi-file refactoring              ✅ Best choice         ⚠️ Okay
Quick code generation               ⚠️ Slower              ✅ Fast (Flash)
Image/multimodal analysis           ✅ -i/--image flag     ✅ Native support
Complex debugging                   ✅ Thorough            ⚠️ Surface level
Parallel independent tasks          ✅ Both                ✅ Both
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Codex CLI Commands

### Research Task (needs to write output)
```bash
# NOTE: Use workspace-write if task needs to write files (even research output)
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
  "Task description...

  ⚠️ CRITICAL FEEDBACK REQUIRED:
  1. Most critical issue identified
  2. Key trade-off or design decision
  3. One concrete improvement suggestion"

# Step 3: Review changes
git status && git diff
```

### Key Flags (v0.64.0)
- `--full-auto` = `--sandbox workspace-write -a on-failure`
- `--search` = Enable web search (place BEFORE exec!)
- `--json` = JSONL event output
- `-o <FILE>` = Final message output file
- `-i, --image <FILE>...` = Attach image(s) to prompt
- `-C <DIR>` = Working directory
- `--add-dir <PATH>` = Allow writing outside workspace

### ⚠️ REMOVED FLAGS (Dec 2025)
- `--yes` was REMOVED in v0.64.0 - no longer available for automation

### Sandbox Modes
- `read-only`: Cannot modify ANY files (pure research without output)
- `workspace-write`: Can write to workspace (use for most tasks)

**Decision**: Does the task need to write files? → workspace-write

## Gemini CLI Commands

### Basic Headless Execution
```bash
# Using alias (gmn = gemini --model gemini-3-pro-preview)
gmn -p "Task description" --output-format json --quiet > output.json

# Or explicitly
gemini --model gemini-2.5-pro -p "Task" --output-format json --quiet
```

### With File Input
```bash
cat source.py | gmn -p "Analyze this code" --quiet > analysis.md
```

### Key Flags
- `-p, --prompt <TEXT>`: The task/prompt
- `-m, --model <MODEL>`: Model selection (gemini-2.5-pro, gemini-2.5-flash)
- `--output-format <text|json|stream-json>`: Output format
- `--quiet, -q`: Suppress spinners/banners (essential for headless)
- `--yolo`: Auto-approve all actions (DANGEROUS - avoid in production)

### Safety
- Avoid `--yolo` unless in sandboxed environment
- Use `.geminiignore` to protect sensitive files
- Prefer `--approval-mode ask` over auto

## Inter-Agent Collaboration Pattern

### File-Based Communication (ai_chatroom)
```
./ai_chatroom/{topic}/
├── codex_research_summary_cdx.txt    # Codex summary
├── codex_research_detail_cdx.md      # Codex details
├── gemini_analysis_gmn.md            # Gemini output
└── README_cld.md                     # CC executive summary
```

### File Naming Convention
- Codex outputs: `*_cdx.txt`, `*_cdx.md`
- Gemini outputs: `*_gmn.txt`, `*_gmn.md`
- Claude Code outputs: `*_cld.txt`, `*_cld.md`

### Communication Language
- **CC ↔ User**: zh-tw with English technical terms
- **CC ↔ Codex/Gemini**: English (LLM-to-LLM)

### Workflow Example
```bash
# 1. CC creates workspace
mkdir -p ./ai_chatroom/feature-x/

# 2. CC delegates research to Codex
codex --search exec --full-auto --json \
  -o "./ai_chatroom/feature-x/research_log_cdx.jsonl" \
  "Research best practices for X. Write to ./ai_chatroom/feature-x/"

# 3. CC delegates quick task to Gemini (parallel)
gmn -p "Generate boilerplate for X" --quiet > ./ai_chatroom/feature-x/boilerplate_gmn.md

# 4. CC reads summaries, synthesizes, presents to user
```

## Timeout Guidelines
- **Minimum**: 4 minutes (240000ms)
- **Research tasks**: 10+ minutes (600000ms)
- **Complex implementation**: 10-15 minutes

```bash
# In CC's Bash tool, set timeout parameter
timeout: 600000
```

## Quality Comparison Notes (Dec 2025 Testing)

**Codex Strengths**:
- Web search (`--search`) provides citations
- Better for research-heavy tasks
- More stable flag set

**Gemini Strengths**:
- Faster execution (especially Flash model)
- Better self-knowledge of own capabilities
- Native multimodal support

**Recommendation**: Use Codex for research, Gemini for quick generation tasks.

## Configuration Files
- Codex: `~/.codex/AGENTS.md` - collaboration rules
- Gemini: `~/.gemini/AGENTS.md` - collaboration rules
- Both agents know to write to `./ai_chatroom/` and use proper suffixes

## Known Limitations (Dec 2025)

### Gemini CLI
- **No shell/write tools**: Cannot execute commands or write files directly
- **Output capture required**: Use `gmn -p "..." --quiet > output.md` to save results
- **For file-writing tasks**: Use Codex CLI instead

## Shared Instruction File Pattern

For delegating same task to multiple agents:

1. Write `./ai_chatroom/{topic}/TASK_INSTRUCTIONS.md` with agent-specific output folders
2. Launch agents pointing to same file:
   ```bash
   # CC + Codex can read instruction and write outputs
   Task(prompt="Read TASK_INSTRUCTIONS.md, you are CC agent...")
   codex exec --full-auto "Read TASK_INSTRUCTIONS.md, you are Codex..."

   # Gemini: capture stdout since it can't write files
   gmn -p "Read TASK_INSTRUCTIONS.md and analyze..." --quiet > ./ai_chatroom/{topic}/analysis_gmn.md
   ```

**Note**: Gemini cannot write files itself - must redirect stdout to capture output.
</headless-agents-strategy>
