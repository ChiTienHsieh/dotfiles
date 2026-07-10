---
name: "wrap"
description: "Run the `wrap` workflow when the user asks to wrap up, ship the current work, check dirty worktrees, commit, push, save useful memory, and produce a concise zh-tw session summary."
---

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
/usr/bin/python3 "$HOME/dotfiles/codex/hooks/stop_dirty_worktree.py" --dirty-report --cwd "$PWD" 2>/dev/null || echo "(dirty report unavailable)"
```

## Execution Flow

### Step 1: Gather & Assess

Run the Context Commands above and read their output. In parallel, gather:

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
- **本 session touched repos** — 使用 dirty report 盤點 `PostToolUse` 已追蹤到的 git roots；這取代 blocking `Stop` hook，不要重新啟用 `Stop` dirty check。

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
- **Conflicts or diverged state** — surface the divergence and let the user pick rebase/merge/skip
- **Behind remote** — need to pull first, might conflict
- **Ambiguous uncommitted changes** — files that might be WIP vs. ready to ship
- **Multiple repos touched** — confirm which ones to push
- **Sensitive files detected** — .env, credentials, secrets in diff

### Step 3.5: cmux Delegation Cleanup Check

After the normal wrap actions are complete, check whether this session or prior
agent delegation left active cmux worker surfaces behind.

Use:

```bash
"$HOME/dotfiles/skills/shared/wrap/scripts/cmux_delegation_cleanup.sh" list
```

If it lists delegated surfaces, show the surface IDs and ask the user whether
they want to close those delegated surfaces. Do not close them without asking.

If the user agrees, close them peacefully:

```bash
"$HOME/dotfiles/skills/shared/wrap/scripts/cmux_delegation_cleanup.sh" close surface:N
```

or, when the user agrees to close all listed delegated surfaces:

```bash
"$HOME/dotfiles/skills/shared/wrap/scripts/cmux_delegation_cleanup.sh" close-all-active
```

The cleanup helper sends `/quit` to Codex first, sends Enter, waits briefly, and
then runs `cmux close-surface`. Do not use Ctrl-C for this cleanup path unless
`/quit` is unavailable and the user explicitly approves a rougher shutdown.

### Step 4: Report

After executing, present a compact result in zh-tw. Only show sections with content — skip clean sections.

If the repo check in Context Commands printed `(not a git repo ...)`, **omit the Git section entirely**.

```
## Wrap-up：<repo-name>（<branch>）

### 完成
- [x] 已 commit：「<commit message>」（N 個檔案）
- [x] 已 push N 個 commit 到 origin/<branch>
- [x] 已更新 README：<what>
- [x] 已儲存 memory：<what>

### 需要注意
- [ ] 「task description」— 仍在進行中
- [ ] 3 天前的 stash — 要 drop 還是 apply？

### 本次摘要
<用 2-3 句 zh-tw 摘要本次完成的工作>
```

If everything was already clean before wrap: just print the zh-tw summary and "都乾淨，收工。"

### Squash Suggestion

If there are **3+ unpushed commits** before pushing, check if they look squashable (e.g., "fix typo", "wip", "fixup", multiple small changes to same files). If so, offer to squash before pushing — but don't block on it. Frame as: "你有 N 個 unpushed commits，看起來可以 squash，要不要？" with options to squash or push as-is.

## Style

- Be concise. This is a quick wrap-up, not a retrospective.
- Use the project's communication style (zh-tw + English technical terms).
- The wrap-up ending message and final report MUST be in zh-tw by default, including section titles, checklist items, and the clean-ending sentence. Keep commit messages, file paths, branch names, and exact command/config names in English.
- Bias toward action. The user called /wrap because they want to be done — help them be done.
- Checklist format for the report — scannable at a glance.
