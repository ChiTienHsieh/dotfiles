---
name: "where-am-i"
description: "回顧專案進度：使用者問上次做到哪裡、目前狀態或如何接續時使用；預設唯讀，整理 Git 與相關 task 的脈絡。"
disable-model-invocation: true
---

# where-am-i

使用者隔一陣子回到專案，問「我們做到哪了」之類的話時，快速、準確地回顧：git 現在什麼狀態、最近在這裡做什麼、合理的下一步是什麼。這是 `wrap`（session 收尾）的**開場**對應版。

讀 pane 是唯讀的，不需要授權。如果這次 human 的進度提問明確要求 agent 看某個 tmux pane 再動作，就搭配 `tmux-orchestration`：where-am-i 負責回顧，tmux-orchestration 負責 pane 那一面。

預設唯讀。使用者同時要求 pull 或同步時，在那個授權範圍內照 `tidy-workspace` 做，不再問一次。

## 不適用

- 結束 session／commit／push 的事：用 `wrap`。

## 第 1 步：Git 狀態（唯讀）

在目前目錄收集：

```bash
git rev-parse --is-inside-work-tree 2>/dev/null || echo "(not a git repo)"
git branch --show-current
git log --oneline -10
git status --short
git rev-list --left-right --count HEAD...@{upstream} 2>/dev/null || echo "(no upstream)"
git stash list
```

解讀：領先／落後 upstream 幾個 commit、tree 髒不髒、最近的 commit 走向、有沒有留下的 stash。

## 第 2 步：這個專案最近的 agent 活動

先用相關的對話脈絡或 runtime 原生的 task 摘要。不夠判斷上次做到哪時，再用 daily-loop 的抽取器篩到目前目錄：

```bash
"$HOME/dotfiles/skills/shared/daily-loop/scripts/mine_transcripts.sh" \
  --since 168 --format json \
  | jq --arg cwd "$PWD" '.projects[] | select(.cwd == $cwd)
      | {sessions, user_turns, tools, snippets: (.snippets[0:6])}'
```

沒有東西對到 `$PWD` 時，只在真的需要更舊的紀錄才放寬時間窗；否則說明沒有紀錄，用 Git 狀態就好。不要讀原始 `.jsonl`，用 digest。

## 第 3 步：同步檢查

第 1 步顯示 branch **落後** upstream 時，講出來並提議追上，不要默默 pull：

- 單純落後（沒分岔）：提議 `git pull --ff-only`。
- 分岔（又領先又落後）：把分岔情況攤開，讓使用者選 rebase 或 merge；這裡不 pull。

沒被要求的 pull 要先問；已經要求的同步照 `tidy-workspace` 做，不再確認一次。

## 第 4 步：回顧與下一步

用使用者的溝通風格給一段短回顧，要一眼掃得完：

```
## 上次停在：<repo>（<branch>）

- Git：<領先／落後摘要>，<乾淨｜N 個髒檔>，<有 stash 就註明>
- 最近在做：<從最近 commit 與 agent 對話抓 1–2 行>
- 未收尾：<未提交的工作／snippets 裡還開著的事>

### 建議下一步
<一個具體建議，例如「把 X 做完」「先 pull 再接 Y」>
```

然後停下來讓使用者決定。where-am-i 負責定位，不往前衝。

## 跨工具

這份 SKILL.md Claude Code 和 Codex 都會讀。git 指令和抽取器兩邊都能跑；某一步用到 Claude 才有的機制時，退回用一般的編號問題。
