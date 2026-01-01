---
name: yolo-cc
description: Delegate risky autonomous tasks to a containerized Claude Code instance. Use when a task requires many file changes, running unknown commands, or would benefit from Claude operating without permission prompts - but in an isolated Docker sandbox where mistakes can be easily recovered.
allowed-tools: Bash
---

# YOLO-CC: Containerized Claude Code Delegation

## When to Use

Delegate to yolo-cc when:
- Task requires many autonomous file changes ("fix all type errors", "refactor entire module")
- Need to run potentially destructive commands without constant permission prompts
- Want to let Claude experiment freely but contain the blast radius
- Multi-step implementation where interruptions would break flow

Do NOT use for:
- Simple single-file edits (just do it directly)
- Tasks needing host-specific tools not available in the container

## Architecture

```
User <-> Normal CC (safe, asks permissions)
              |
              v
         yolo-cc container
         - --dangerously-skip-permissions enabled
         - .git mounted read-only (always recoverable)
         - workspace mounted read-write
         - Full internet access (not isolated)
         - Disk isolation only (Docker sandbox)
```

## How to Invoke

```bash
# Basic usage
yolo-cc "your detailed prompt here"

# With Python (uv) environment
yolo-cc --uv "create FastAPI server with SQLAlchemy models"

# Specific workspace
yolo-cc -w /path/to/project "refactor auth module"

# Force rebuild images
yolo-cc --build "update dependencies"
```

## Requirements

- CLAUDE_CODE_OAUTH_TOKEN env var must be set
- Docker/OrbStack running
- `yolo-cc` is available in PATH (symlinked to ~/.local/bin)

## Available Flags

```
--uv              Include Python (uv) environment
--npm             Include Node.js environment [TODO]
--playwright      Include Playwright [TODO]
-w, --workspace   Workspace directory (default: cwd)
--build           Force rebuild images
```

## Prompt Guidelines

When delegating to yolo-cc, write detailed prompts:
1. State the goal clearly
2. Mention specific files/directories if known
3. Include constraints or requirements
4. Request a summary of changes at the end

Example prompt:
```
Fix all TypeScript errors in src/.
Run `npm run build` to verify.
At the end, provide a summary of files changed and errors fixed.
```

## Recovery

If yolo-cc makes unwanted changes:
```bash
cd /workspace
git checkout .      # Restore tracked files
git clean -fd       # Remove untracked files
```

## Security Notes

- OAuth token passed via env var (not persisted in container filesystem)
- Token only works with Claude Code, cannot be used for raw API abuse
- Can revoke token anytime at claude.ai/settings/account → Active Connections
- Container deletion clears all runtime state
