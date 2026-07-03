---
name: "night"
description: "Run the `night` workflow when the user is going to sleep and wants Codex to finish remaining work, check dirty worktrees, commit and push safe progress, then report what was done in zh-tw."
---

# night

Use this skill when the user asks to run `night`, says night night, or wants Codex to keep working and close things down while they are away.

## Command Template

# night — 使用者要睡了，Codex 自己收尾

使用者說 night night 就是要去睡了。Codex 負責：把剩下的事情做完，然後跑 wrap 流程收工。

**核心原則：不要問問題。** 使用者已經不在螢幕前了。所有決策自己判斷、自己做。遇到真的無法判斷的事情，跳過並記錄在最後報告裡，不要卡住。

**備份原則：一人專案，大膽 push。** 這台機器上的 repo 幾乎都是使用者自己一個人在維護的。收尾時一律 commit + push 到 remote 備份進度，不需要猶豫。只有明確危險的情況（force push main、push 含密碼的檔案）才需要跳過。

## Execution Flow

### Step 1: 盤點未完成的工作

1. 用 the current task list 檢查所有未完成的 tasks
2. 回顧對話紀錄，找出使用者交代但還沒做完的事
3. 列出待辦清單，按優先順序排列

### Step 2: 完成剩餘工作

按優先順序逐一完成待辦事項。規則：

- **能做的就做** — 寫 code、跑測試、修 lint、更新文件，全部自己來
- **不要問使用者** — 他已經去睡了，所有決策自己下
- **安全第一** — 不確定的破壞性操作（刪東西、force push、改 production config）不要做，記下來就好
- **卡住就跳過** — 需要使用者判斷的、需要密碼的、需要手動操作的 → 記在「待使用者處理」清單，不要卡住整個流程
- **完成一項就更新 task plan** — 保持進度可追蹤

### Step 2.5: 相關 repo 檢查交給 Step 3 的 wrap

相關 repo 檢查交給 Step 3 的 wrap；night 模式下 wrap 的 stop-and-ask 項目自動處理，secrets 與 force-push 除外。

### Step 3: 跑 wrap skill

所有能做的都做完之後，跑 `$wrap`，但套用 night policy：不要問問題；可安全處理的就自己處理；不安全或需要使用者判斷的項目跳過並記錄。

### Step 4: 晚安報告

在 wrap 報告之後，加一段簡短的晚安報告，只寫相對於 wrap 的 delta：幫你做完的、明天起來要處理的；如果沒有待辦事項，就直接說一切搞定。

## Style

- zh-tw，跟平常一樣
- 行動優先，少廢話
- 晚安訊息簡短溫馨就好，不要寫小作文
