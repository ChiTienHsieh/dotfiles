---
allowed-tools: [Bash, Agent, AskUserQuestion, Read, Grep, Glob, TaskList]
---

# wrap — Session Wrap-up Check

Reflect on the current session and surface anything that should be handled before leaving.

## Pre-loaded Context

In-git-repo?: !`git rev-parse --is-inside-work-tree 2>/dev/null || echo "(not a git repo — skip all git sections below)"`
Git status: !`git status --short 2>/dev/null || echo "(n/a)"`
Ahead/Behind: !`git rev-list --left-right --count HEAD...@{upstream} 2>/dev/null || echo "(no upstream tracked)"`
Stash: !`git stash list 2>/dev/null || echo "(n/a)"`
Recent commits: !`git log --oneline -5 2>/dev/null || echo "(n/a)"`
Branch: !`git branch --show-current 2>/dev/null || echo "(n/a)"`

## Execution Flow

### Step 1: Gather Remaining State

The git state is already pre-loaded above. In parallel, gather:

1. **Tasks**: Use TaskList to check for any incomplete tasks
2. **Memory check**: Reflect on the conversation — was there anything the user said to remember, any feedback given, any decisions made that should be saved to memory?
3. **Docs check**: If this repo has user-facing documentation (README, CLAUDE.md, docs/, etc.), consider whether this session's changes warrant a doc update. Examples:
   - New feature added but not reflected in README
   - Config or setup steps changed but docs still show old way
   - New commands/agents/tools added without documentation
   - Architecture changed in a way that affects onboarding
   Skip this check for repos without meaningful docs (e.g., scratch projects, single-script repos).

### Step 2: Build Checklist

Present a checklist of findings. Only show sections that have actionable items — skip clean sections entirely.

If `In-git-repo?` pre-loaded as `(not a git repo ...)`, **omit the Git section entirely** (no "working tree clean" line — it just doesn't apply). Same for the docs/memory sections if there's nothing meaningful to check.

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

### Docs
- [ ] README/CLAUDE.md should mention <new thing>
- [ ] docs/ needs update for <changed behavior>
- [x] Docs are up to date (or repo has no meaningful docs)

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
  - "Update docs: <specific file>" (if docs need updating)
  - "Run /gsync to sync" (if behind remote or complex state)
  - "All good, 收工" (always include as escape hatch)

**Priority order for recommendation**: docs > commit > push > memory > nothing. Docs come first because they should be included in the same commit as the code changes. Uncommitted changes are the most at-risk (not in git history yet), then unpushed commits.

If everything is clean (working tree clean, in sync with remote, no tasks, no memories): just print the summary and a short "All clear, 收工!" — no AskUserQuestion needed.

## Style

- Be concise. This is a quick pre-exit check, not a retrospective.
- Use the project's communication style (zh-tw + English technical terms).
- Checklist format is key — scannable at a glance.
