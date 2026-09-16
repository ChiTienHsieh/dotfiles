---
name: "where-am-i"
description: "回顧專案進度：使用者問上次做到哪裡、目前狀態或如何接續時使用；預設唯讀，整理 Git 與相關 task 的脈絡。"
disable-model-invocation: true
---

# where-am-i

When the user comes back to a project after a while and asks some variant of
"remind me where were we?", give them a fast, accurate recap: what the git
state is, what was being worked on here recently, and what the sensible next
step is. This is the **start-of-session** counterpart to `wrap`
(end-of-session).

Reading a pane is read-only and needs no authorization. If the
current human's progress question explicitly asks the agent to inspect a tmux
pane and then act on it, combine this skill with `tmux-orchestration`:
where-am-i handles the recap, tmux-orchestration handles the pane surface.

Read-only by default. If the user also requests a pull or sync, follow
`tidy-workspace` within that authorization; do not ask for the same approval again.

## When NOT to use

- Ending a session / committing / pushing → the `wrap` skill.

## Step 1 — Git state (read-only)

From the current working directory, gather:

```bash
git rev-parse --is-inside-work-tree 2>/dev/null || echo "(not a git repo)"
git branch --show-current
git log --oneline -10
git status --short
git rev-list --left-right --count HEAD...@{upstream} 2>/dev/null || echo "(no upstream)"
git stash list
```

Interpret: how many commits ahead/behind upstream, whether the tree is dirty,
recent commit trajectory, any stashes left behind.

## Step 2 — This project's recent agent history

Use relevant conversation context or native task summaries first. If those
do not establish where this project left off, use the daily-loop extractor and
filter to the current directory:

```bash
"$HOME/dotfiles/skills/shared/daily-loop/scripts/mine_transcripts.sh" \
  --since 168 --format json \
  | jq --arg cwd "$PWD" '.projects[] | select(.cwd == $cwd)
      | {sessions, user_turns, tools, snippets: (.snippets[0:6])}'
```

If nothing matches `$PWD`, widen the window only when older history is needed;
otherwise report the gap and use Git state. Do not read raw `.jsonl` — use the digest.

## Step 3 — Sync check

If Step 1 shows the branch is **behind** upstream, surface it and offer to catch
up — do not pull silently:

- Clean catch-up (behind only, not diverged) → offer `git pull --ff-only`.
- Diverged (both ahead and behind) → present the divergence and let the user
  pick rebase/merge; do not pull here.

An unrequested pull needs approval; an already-requested sync follows
`tidy-workspace` without a second confirmation.

## Step 4 — Recap + next steps

Present a short recap (in the user's communication style). Keep it scannable:

```
## Where you were: <repo> (<branch>)

- Git: <ahead/behind summary>, <clean|N dirty files>, <stash note if any>
- Last worked on: <1-2 lines from recent commits + recent agent asks>
- Loose ends: <uncommitted work / open threads from the snippets>

### Suggested next step
<one concrete suggestion, e.g. "finish X", "pull then continue Y">
```

Then stop and let the user decide. where-am-i orients; it does not charge ahead.

## Cross-tool note

This SKILL.md is read by both Claude Code and Codex. The git commands and the
extractor both work in either. Where a step would use a Claude-only mechanism,
fall back to a plain numbered question.
