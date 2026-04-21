# Reviewer tmux Color Fix

## Problem

Reviewer agent badge (`@reviewer`) and pane border displayed as ugly teal/mint-green instead of a warm yellow.

## Root Cause

**Ghostty uses the Dracula theme.** Dracula's ANSI color mapping:

| ANSI Name | Colour # | Dracula Hex | How it looks |
|-----------|----------|-------------|--------------|
| green     | 2        | `#50fa7b`   | mint green   |
| yellow    | 3        | `#f1fa8c`   | lemon yellow |
| magenta   | 5        | `#ff79c6`   | hot pink     |
| cyan      | 6        | `#8be9fd`   | sky blue     |

**But CC's tmux rendering does NOT map color names → ANSI 1:1.**

Empirical evidence from screenshots:
- `color: yellow` (reviewer) → rendered as **teal/mint** (ugly) ← CONFIRMED by user screenshot
- `color: green` (builder)  → rendered as **warm golden amber** (user liked this)

CC's tmux integration appears to shift or remap named colors in a non-obvious way. The `yellow` label ended up mapping to whatever tmux colour produces the teal-green in Dracula.

## Fix Applied

**File:** `~/.claude/agents/reviewer.md`

```
Before: color: yellow
After:  color: magenta
```

Dracula magenta = `#ff79c6` (rose pink). Bold, distinctive, not used by any other agent, looks beautiful on the dark Dracula background. Fits the skeptic/QA role's assertive personality.

## Agent Color Map (Post-Fix)

| Agent         | color    | Dracula expected |
|---------------|----------|-----------------|
| builder       | green    | renders as warm amber (observed) |
| monitor       | red      | `#ff5555` coral red |
| opus-specialist | purple | lavender |
| planner       | blue     | `#bd93f9` lavender/purple (user likes) |
| **reviewer**  | **magenta** | **`#ff79c6` rose pink** |
| uiux-auditor  | orange   | warm orange |
| web-researcher | green   | same as builder (amber) |

## If magenta also looks wrong

Next candidates in order of preference on Dracula dark:
1. `cyan` → `#8be9fd` (sky blue) — clean, readable
2. Leave a note and investigate whether CC supports hex colors in agent definitions

## Ghostty/tmux config changes

**None required.** The fix was in the agent definition only.
