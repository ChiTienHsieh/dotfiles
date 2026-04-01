---
allowed-tools: [Bash, Agent, AskUserQuestion, Read, Grep, Glob, TaskList]
---

# wrap — Session Wrap-up Check

Reflect on the current session and surface anything that should be handled before leaving.

## Execution Flow

### Step 1: Gather State (parallel)

Run all of these in parallel:

1. **Git status**: `git status --short && git rev-list --left-right --count HEAD...@{upstream} 2>/dev/null && git stash list`
2. **Tasks**: Use TaskList to check for any incomplete tasks
3. **Memory check**: Reflect on the conversation — was there anything the user said to remember, any feedback given, any decisions made that should be saved to memory?

### Step 2: Build Checklist

Present a checklist of findings. Only show sections that have actionable items — skip clean sections entirely.

```
## Wrap-up: <repo-name> (<branch>)

### Git
- [ ] N uncommitted changes (list files)
- [ ] N unpushed commits
- [ ] N stashes sitting around
- [x] Working tree clean ← only if actually clean, as a reassurance

### Tasks
- [ ] "task description" — still in progress
- [ ] "task description" — not started
- [x] All tasks completed ← only if true

### Memory
- [ ] Consider saving: <thing learned this session>
- [x] Nothing notable to remember

### Session Summary
<2-3 sentence summary of what was accomplished this session>
```

### Step 3: Offer Actions

If there are actionable items, use **AskUserQuestion** to offer:

- First option = the single most useful action, marked "(Recommended)"
- Options should be concrete, e.g.:
  - "Commit + push 這些 changes" (if uncommitted/unpushed)
  - "Save memory: <specific thing>" (if something worth remembering)
  - "Run /gsync to sync" (if git needs syncing)
  - "All good, 收工" (always include as escape hatch)

If everything is clean: just print the summary and a short "All clear, 收工!" — no AskUserQuestion needed.

## Style

- Be concise. This is a quick pre-exit check, not a retrospective.
- Use the project's communication style (zh-tw + English technical terms).
- Checklist format is key — scannable at a glance.
