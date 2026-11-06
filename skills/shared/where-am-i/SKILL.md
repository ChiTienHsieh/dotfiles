---
name: "where-am-i"
description: "休息一段時間後接回來：使用者回到某個專案，問上次做到哪、之前在這裡做什麼（例如 'remind me where were we'），或想先跟遠端同步再繼續時使用。收集 git 狀態加這個專案最近的 agent 紀錄，整理成一段短回顧，附建議的下一步。預設唯讀；沒確認絕不自動 commit 或自動 pull。"
disable-model-invocation: true
---

# where-am-i

使用者隔了一陣子回到專案，問「上次做到哪？」之類的話時，快速、準確地幫他回顧：
git 狀態如何、最近在這裡做什麼、合理的下一步是什麼。這是 `wrap`（session 結束）
對應的 **session 開頭** skill。

讀 pane 是唯讀的，不需要授權。使用者問進度時如果明確要 agent 檢查某個 tmux pane
再動手，就把這個 skill 和 `tmux-orchestration` 一起用：where-am-i 負責回顧，
tmux-orchestration 負責 pane 那一面。

預設唯讀。唯一可以做的動作是 `git pull`，而且要使用者確認後才做。

## 什麼時候不用

- 結束 session／commit／push → `wrap` skill。

## 步驟 1 — Git 狀態（唯讀）

在目前的工作目錄收集：

```bash
git rev-parse --is-inside-work-tree 2>/dev/null || echo "(not a git repo)"
git branch --show-current
git log --oneline -10
git status --short
git rev-list --left-right --count HEAD...@{upstream} 2>/dev/null || echo "(no upstream)"
git stash list
```

解讀：比 upstream 多幾個、少幾個 commit，工作目錄乾不乾淨，最近 commit 的走向，
有沒有留下的 stash。

## 步驟 2 — 這個專案最近的 agent 紀錄

重用 daily-loop 的擷取器（共用的底層），過濾到目前的目錄，看*你和其他 agent*
實際在這裡做了什麼：

```bash
"$HOME/dotfiles/skills/shared/daily-loop/scripts/mine_transcripts.sh" \
  --since 168 --format json \
  | jq --arg cwd "$PWD" '.projects[] | select(.cwd == $cwd)
      | {sessions, user_turns, tools, snippets: (.snippets[0:6])}'
```

`$PWD` 沒有對到任何東西（這個目錄最近沒有 session），就把時間窗放寬
（`--since 336`），或說明這裡沒有最近的 agent 紀錄，只靠 git 狀態。不要讀原始
`.jsonl`，相信 digest。

## 步驟 3 — 同步檢查

步驟 1 顯示 branch **落後** upstream，就講出來並提議補上，不要默默 pull：

- 單純落後（沒有分歧）→ 提議 `git pull --ff-only`。
- 分歧（又領先又落後）→ 說明分歧狀況，讓使用者選 rebase 或 merge；這裡不 pull。

任何 pull 都先問。

## 步驟 4 — 回顧 + 下一步

用使用者的溝通風格給一段短回顧，要一眼看得完：

```
## Where you were: <repo> (<branch>)

- Git: <ahead/behind summary>, <clean|N dirty files>, <stash note if any>
- Last worked on: <1-2 lines from recent commits + recent agent asks>
- Loose ends: <uncommitted work / open threads from the snippets>

### Suggested next step
<one concrete suggestion, e.g. "finish X", "pull then continue Y">
```

然後停下來，讓使用者決定。where-am-i 只負責定位，不往前衝。

## 跨工具說明

這份 SKILL.md 由 Claude Code 和 Codex 一起讀。git 指令和擷取器在兩邊都能跑。
某一步要用到 Claude 才有的機制時，退回用一般的編號問題。
