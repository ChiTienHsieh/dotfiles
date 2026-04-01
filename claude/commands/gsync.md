---
allowed-tools: [Bash, Agent, AskUserQuestion, Read, Grep, Glob]
---

# gsync — Git Sync Helper

Smart git sync: fetch, analyze, brief, recommend the best action, then execute.

## Arguments

- `$ARGUMENTS` — optional branch name. If empty, use current branch.

## Execution Flow

### Phase 1: Gather Info

Run these git commands (use Bash tool, parallel where possible):

```
git fetch --all --prune
git branch --show-current
git status --short
git stash list
git log --oneline -5 HEAD
git log --oneline -10 @{upstream}..@{u} 2>/dev/null  # incoming commits
git rev-list --left-right --count HEAD...@{upstream} 2>/dev/null  # ahead/behind
git branch -vv  # all local branches + tracking status
git submodule status 2>/dev/null  # submodule state (if any)
```

If `$ARGUMENTS` is provided and differs from current branch, check that branch instead.

### Phase 2: Analyze Diff

If there are incoming remote commits OR local uncommitted changes, spawn a **haiku** subagent (using Agent tool with `model: "haiku"`) to:
- Run `git diff` (unstaged) and `git diff --cached` (staged)
- Run `git log --oneline --stat @{upstream}..HEAD` (outgoing) and `git log --oneline --stat HEAD..@{upstream}` (incoming)
- Provide a concise summary of what changed (both local and remote sides)
- **Flag any concerns**: secrets, debug code, large binary files, TODO/FIXME markers

### Phase 3: Brief the User

Present a structured status report:

```
## Git Sync Status: <repo-name> (<branch>)

**Remote**: <ahead/behind counts>
**Working tree**: <clean / N modified, N untracked, N staged>
**Stash**: <count or "none">
**Submodules**: <status or "none">

### Incoming (from remote)
<summary of remote commits, or "Up to date">

### Outgoing (local, not pushed)
<summary of local commits, or "Nothing to push">

### Local Changes
<diff summary from haiku agent, or "Clean working tree">

### Branches
<any branches with gone remotes, or notable tracking issues — one line each>
```

Less relevant sections (e.g., stash=none, no submodules) should be collapsed to a single line or omitted.

### Phase 4: Recommend & Execute

**Always recommend exactly ONE best action as the first option, marked "(Recommended)".**

Analyze the repo state and pick the single best flow from this decision tree:

#### Decision Logic

1. **Behind remote?** → Always `git pull --rebase` first (stash local changes if needed).
2. **Ahead of remote?** → After pulling, push local commits.
3. **Diverged?** → Pull rebase first, then push.
4. **Only uncommitted local changes, in sync with remote?** → "Just fetch (done)" — user manages their own commits.
5. **Fully clean and in sync?** → "All synced, nothing to do."

#### Pre-push Safety Scan

Before recommending any push action, spawn a **haiku** subagent to quickly scan the staged/committed changes for:
- Hardcoded secrets, API keys, tokens
- Debug code (`console.log`, `debugger`, `print("DEBUG`)
- Large binary files (>1MB)
- Accidental file inclusions (.env, credentials, node_modules)

If issues found: **warn the user explicitly** and do NOT put push as recommended. Instead recommend fixing first.
If clean: proceed with push as part of the recommended flow.

#### Squash Suggestion

If there are **3+ local unpushed commits**, analyze the commit messages:
- If commits look like they could be squashed (e.g., "fix typo", "wip", "fixup", multiple small changes to same files), suggest squash as an option
- Frame it as: "你有 N 個 unpushed commits，看起來可以 squash 成更乾淨的 history，要不要？"
- This should be an additional option, NOT the recommended one (unless commits are clearly WIP noise)

#### AskUserQuestion Format

Use **AskUserQuestion** to present actions. Rules:
- **First option = recommended action** with "(Recommended)" in label
- Only show 2-4 options that make sense for the current state
- Always include a "do nothing" escape hatch

Example options for "behind + ahead" state:
1. "Pull rebase + Push (Recommended)" — sync both directions
2. "Pull rebase only" — get remote changes, push later
3. "No action" — just wanted the status

After the user picks, execute the chosen action. If conflicts arise during rebase, stop and explain the situation — do NOT auto-resolve.

## Style

- Be concise. This is a utility command, not a teaching moment.
- Use the project's communication style (zh-tw + English technical terms).
