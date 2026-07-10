---
name: "where-am-i"
description: "Catch up after a break: when the user returns to a project and asks 'remind me where were we', 'where am I', 'where did we leave off', 'what was I doing here', or wants to pick up where they left off / sync with remote before resuming. Gathers git state + this project's recent agent history into a short recap with suggested next steps. Read-only by default; never auto-commits or auto-pulls without confirmation."
---

# where-am-i

When the user comes back to a project after a while and asks some variant of
"remind me where were we?", give them a fast, accurate recap: what the git
state is, what was being worked on here recently, and what the sensible next
step is. This is the **start-of-session** counterpart to `wrap`
(end-of-session).

If the progress question mentions a tmux pane, combine this skill with
`tmux-orchestration`: where-am-i handles the recap, tmux-orchestration handles
pane inspection.

Read-only by default. The only action it may take is `git pull`, and
only after the user confirms.

## When to use

- "remind me where were we", "where am I", "where did we leave off", "what was
  I doing in this repo", "catch me up", "pick up where I left off".
- The user returns to a project after a break and wants context before diving in.

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

Reuse the daily-loop extractor (the shared substrate) and filter to the current
directory, so you see what *you and the agents* were actually doing here:

```bash
"$HOME/dotfiles/skills/shared/daily-loop/scripts/mine_transcripts.sh" \
  --since 168 --format json \
  | jq --arg cwd "$PWD" '.projects[] | select(.cwd == $cwd)
      | {sessions, user_turns, tools, snippets: (.snippets[0:6])}'
```

If nothing matches `$PWD` (no recent sessions in this exact dir), widen the
window (`--since 336`) or note that there's no recent agent history here and
lean on the git state alone. Do not read raw `.jsonl` — trust the digest.

## Step 3 — Sync check

If Step 1 shows the branch is **behind** upstream, surface it and offer to catch
up — do not pull silently:

- Clean catch-up (behind only, not diverged) → offer `git pull --ff-only`.
- Diverged (both ahead and behind) → present the divergence and let the user
  pick rebase/merge; do not pull here.

Ask before running any pull.

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
