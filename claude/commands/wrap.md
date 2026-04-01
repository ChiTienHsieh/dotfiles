---
allowed-tools: [Bash, Agent, AskUserQuestion, Read, Grep, Glob, TaskList]
---

# wrap — Session Wrap-up Check

Reflect on the current session and surface anything that should be handled before leaving.

## Pre-loaded Context

Git status: !`git status --short`
Ahead/Behind: !`git rev-list --left-right --count HEAD...@{upstream} 2>/dev/null`
Stash: !`git stash list`
Recent commits: !`git log --oneline -5`
Branch: !`git branch --show-current`

## Execution Flow

### Step 1: Gather Remaining State

The git state is already pre-loaded above. In parallel, gather:

1. **Tasks**: Use TaskList to check for any incomplete tasks
2. **Memory check**: Reflect on the conversation — was there anything the user said to remember, any feedback given, any decisions made that should be saved to memory?

### Step 2: Build Checklist

Present a checklist of findings. Only show sections that have actionable items — skip clean sections entirely.

```
## Wrap-up: <repo-name> (<branch>)

### Git
- [ ] N uncommitted changes (list files)
- [ ] N unpushed commits — `git push` needed
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

**IMPORTANT**: Unpushed commits are an actionable item. If ahead of remote by any number of commits, surface it clearly.

### Step 3: Offer Actions

If there are actionable items, use **AskUserQuestion** to offer:

- First option = the single most useful action, marked "(Recommended)"
- Options should be concrete, e.g.:
  - "Push N commits to remote" (if ahead — this is almost always the recommended action at wrap-up)
  - "Commit + push 這些 changes" (if uncommitted + unpushed)
  - "Commit changes (don't push yet)" (if uncommitted, in sync with remote)
  - "Save memory: <specific thing>" (if something worth remembering)
  - "Run /gsync to sync" (if behind remote or complex state)
  - "All good, 收工" (always include as escape hatch)

**Priority order for recommendation**: commit > push > memory > nothing. Uncommitted changes are the most at-risk (not in git history yet), then unpushed commits.

If everything is clean (working tree clean, in sync with remote, no tasks, no memories): just print the summary and a short "All clear, 收工!" — no AskUserQuestion needed.

## Style

- Be concise. This is a quick pre-exit check, not a retrospective.
- Use the project's communication style (zh-tw + English technical terms).
- Checklist format is key — scannable at a glance.
