---
name: "source-command-wrap"
description: "Run the migrated source command `wrap`."
---

# source-command-wrap

Use this skill when the user asks to run the migrated source command `wrap`.

## Command Template

# wrap — Session Wrap-up & Ship

Wrap up = document properly, then commit + push. Not just a checklist — actually finish the job.

## Context Commands

When this skill runs, gather the current git state with:

```bash
git rev-parse --is-inside-work-tree 2>/dev/null || echo "(not a git repo - skip all git sections below)"
git status --short 2>/dev/null || echo "(n/a)"
git rev-list --left-right --count HEAD...@{upstream} 2>/dev/null || echo "(no upstream tracked)"
git stash list 2>/dev/null || echo "(n/a)"
git log --oneline -5 2>/dev/null || echo "(n/a)"
git branch --show-current 2>/dev/null || echo "(n/a)"
```

## Execution Flow

### Step 1: Gather & Assess

The git state is already pre-loaded above. In parallel, gather:

1. **Tasks**: Use the current task list to check for any incomplete tasks
2. **Memory check**: Reflect on the conversation — was there anything the user said to remember, any feedback given, any decisions made that should be saved to memory?
3. **Docs check**: If this repo has user-facing documentation (README, AGENTS.md, docs/, etc.), consider whether this session's changes warrant a doc update. Examples:
   - New feature added but not reflected in README
   - Config or setup steps changed but docs still show old way
   - New commands/agents/tools added without documentation
   - Architecture changed in a way that affects onboarding
   Skip this check for repos without meaningful docs (e.g., scratch projects, single-script repos).

### Step 2: Fix Docs First

If docs need updating, **do it now** before committing — docs should ship with the code, not as a follow-up.

- Update README, AGENTS.md, or other relevant docs
- Stage the doc changes alongside any pending code changes
- This ensures the commit is complete and self-contained

### Step 2.5: 檢查相關 repo

有些檔案不在目前的 repo 裡，但透過 symlink 被其他 repo 追蹤。**每次 wrap 都要檢查這些 repo 有沒有未 commit 的改動：**

- **`~/dotfiles`** — 追蹤 `~/.codex/AGENTS.md`（symlink）、`~/.zshrc`、`~/.aliases` 等。改了這些檔案就會弄髒這個 repo。

如果有相關改動：
1. `cd` 進去，看 diff
2. Commit + push
3. 寫進 wrap 報告裡

### Step 3: Auto-Execute Safe Actions

**Wrap up is about finishing, not asking permission for obvious things.** Execute these directly without asking:

#### Auto-execute (just do it):
- **Commit uncommitted changes** — draft a good commit message, stage relevant files, commit
- **Push to remote** — if ahead by any number of commits, push
- **Commit + push** — if both uncommitted changes and unpushed commits exist, do both
- **Save memory** — if something worth remembering came up, save it
- **Drop stale stashes** — if stashes are clearly from this session's work that's already committed

#### Stop and ask:
- **Conflicts or diverged state** — run /gsync instead
- **Behind remote** — need to pull first, might conflict
- **Ambiguous uncommitted changes** — files that might be WIP vs. ready to ship
- **Multiple repos touched** — confirm which ones to push
- **Sensitive files detected** — .env, credentials, secrets in diff

### Step 4: Report

After executing, present a compact result. Only show sections with content — skip clean sections.

If `In-git-repo?` pre-loaded as `(not a git repo ...)`, **omit the Git section entirely**.

```
## Wrap-up: <repo-name> (<branch>)

### Done
- [x] Committed: "<commit message>" (N files)
- [x] Pushed N commits to origin/<branch>
- [x] Updated README with <what>
- [x] Saved memory: <what>

### Needs Attention
- [ ] "task description" — still in progress
- [ ] Stash from 3 days ago — drop or apply?

### Session Summary
<2-3 sentence summary of what was accomplished this session>
```

If everything was already clean before wrap: just print the summary and "All clear, 收工!"

### Squash Suggestion

If there are **3+ unpushed commits** before pushing, check if they look squashable (e.g., "fix typo", "wip", "fixup", multiple small changes to same files). If so, offer to squash before pushing — but don't block on it. Frame as: "你有 N 個 unpushed commits，看起來可以 squash，要不要？" with options to squash or push as-is.

## Style

- Be concise. This is a quick wrap-up, not a retrospective.
- Use the project's communication style (zh-tw + English technical terms).
- Bias toward action. The user called /wrap because they want to be done — help them be done.
- Checklist format for the report — scannable at a glance.
