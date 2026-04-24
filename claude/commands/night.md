---
allowed-tools: [Bash, Agent, Read, Write, Edit, Grep, Glob, TaskList, TaskUpdate]
---

# night — 使用者要睡了，CC 自己收尾

使用者說 night night 就是要去睡了。CC 負責：把剩下的事情做完，然後跑 /wrap 收工。

**核心原則：不要問問題。** 使用者已經不在螢幕前了。所有決策自己判斷、自己做。遇到真的無法判斷的事情，跳過並記錄在最後報告裡，不要卡住。

**備份原則：一人專案，大膽 push。** 這台機器上的 repo 幾乎都是使用者自己一個人在維護的。收尾時一律 commit + push 到 remote 備份進度，不需要猶豫。只有明確危險的情況（force push main、push 含密碼的檔案）才需要跳過。

## Pre-loaded Context

Tasks: !`echo "（TaskList 會在執行時呼叫）"`
Branch: !`git branch --show-current 2>/dev/null || echo "(n/a)"`
Status: !`git status --short 2>/dev/null || echo "(n/a)"`

## Execution Flow

### Step 1: 盤點未完成的工作

1. 用 TaskList 檢查所有未完成的 tasks
2. 回顧對話紀錄，找出使用者交代但還沒做完的事
3. 列出待辦清單，按優先順序排列

### Step 2: 完成剩餘工作

按優先順序逐一完成待辦事項。規則：

- **能做的就做** — 寫 code、跑測試、修 lint、更新文件，全部自己來
- **不要問使用者** — 他已經去睡了，所有決策自己下
- **安全第一** — 不確定的破壞性操作（刪東西、force push、改 production config）不要做，記下來就好
- **卡住就跳過** — 需要使用者判斷的、需要密碼的、需要手動操作的 → 記在「待使用者處理」清單，不要卡住整個流程
- **完成一項就 TaskUpdate** — 保持進度可追蹤

### Step 2.5: 檢查相關 repo 並同步

一人專案，改動做完就 push — 睡前備份最重要。

1. **目前的 repo** — 有改動就 commit + push
2. **相關 repo**（例如 `~/dotfiles` 追蹤 `~/.claude/` 的 symlink 來源）— 也要檢查有沒有被弄髒，有的話一起 commit + push
3. **多個 repo 都有改動** — 每個都推，不用問

只有以下情況**不推**：
- 含密碼 / secrets 的檔案在 diff 裡
- 需要 force push（代表有 diverge，可能吃掉別人的東西）
- upstream 有設保護規則擋住了

### Step 3: 跑 /wrap

所有能做的都做完之後，用 Skill tool 呼叫 `wrap`，讓它處理：
- commit 未 commit 的改動
- push 到 remote
- 儲存 memory
- 產出 wrap-up 報告

### Step 4: 晚安報告

在 /wrap 的報告之後，加一段簡短的晚安訊息：

```
---
🌙 晚安報告

### 幫你做完的
- [x] ...

### 明天起來要處理的
- [ ] ... （原因：需要你判斷 / 需要 sudo / ...）

晚安，明天見 (￣▽￣)／
```

如果沒有待辦事項（一切都已經搞定了），直接：

```
---
🌙 一切搞定，安心睡 (￣▽￣)／
```

## Style

- zh-tw，跟平常一樣
- 行動優先，少廢話
- 晚安訊息簡短溫馨就好，不要寫小作文
