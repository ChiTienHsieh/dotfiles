---
name: craft-goal
description: 協助撰寫、縮短、驗證、整理可交給下一個 Codex session 執行的 `/goal` prompt。當使用者要寫 `/goal`、準備 handoff prompt、把模糊任務整理成可執行 goal、需要 clarification、research、task spec file、side-effect boundary、或 quick smoke test 時使用。
metadata:
  short-description: Craft reliable /goal handoff prompts
---

# Craft Goal

使用這個 skill，把一個粗略任務想法整理成下一個 Codex 可以可靠執行的 `/goal` prompt。目標不是寫漂亮 prompt，而是做出能交棒、能驗證、風險邊界清楚的 handoff。

使用者預設用 zh-tw proofread，所以除非使用者明確要求英文，**輸出給使用者的 brief 與 `/goal` prompt 都預設用繁體中文**。保留必要 English technical terms，例如 `/goal`、Codex、GitHub、VM、SSH、API、CLI、token、commit、push、branch、file path、command、config key、model ID、UI label。

## 核心流程

1. **釐清任務**
   - 找出使用者真正要的 outcome、target environment、需要的 tools、完成標準。
   - 只有在缺失資訊會改變 scope、risk、命名、或實作方式時才問問題。
   - 先定好命名、topic、target path、side-effect boundary，再產生 final `/goal`。

2. **區分短 prompt 與詳細 spec**
   - 實際貼進 `/goal` 的 prompt 必須低於 app 限制，目前是 4000 characters。
   - 如果任務複雜，先在相關 repo 寫一份 tracked task spec file，再讓 `/goal` 引用該檔案。
   - ignored temp file 只能當 scratch draft；如果下一個 Codex 必須讀到，請放在 tracked file。

3. **定義 side effects**
   - 明確寫出下一個 Codex 可以讀或改哪些 local files。
   - 明確寫出可能會改哪些 external systems，例如 VM config、Telegram、GitHub、Vercel、browser state。
   - 明確禁止 destructive、permission-sensitive、billing、credential、或 broad-scope changes，除非使用者另外批准。
   - 寫清楚下一個 Codex 是否可以 commit / push。預設不要 commit / push，除非使用者要求。

4. **做快速 feasibility check**
   - 檢查相關 repo paths、docs、commands、installed tools、existing config，避免下一個 Codex 第一步就失敗。
   - 如果 `/goal` 依賴特定 CLI、plugin、connector、skill、browser automation、或其他工具，確認它不只是「應該存在」，而是當下真的可見且可用。
   - 對 CLI 工具，至少檢查 command path 與版本；如果使用者要求 latest/up-to-date，確認版本是否符合當下可用資訊或明確標註未驗證。
   - 對 Playwright CLI、`agent-browser` 這類會被下一個 Codex 直接操作的工具，做最低成本 smoke test，例如確認 exact CLI 的 `--version` 與 relevant help command 可執行；若任務依賴 standalone browser，確認可用的啟動方式或把待驗證項寫進 handoff。
   - 不要混淆不同 browser automation surface：Playwright CLI、`agent-browser` CLI、MCP browser tools、以及 in-app browser skill 是不同能力；handoff 必須寫 exact tool name，並驗證同一個 tool。
   - 對 skill/plugin 依賴，確認 skill/plugin 在 Codex 當前可見路徑或 tool discovery 裡可見；不要只確認 repo tree 有檔案。
   - 如果 `/goal` 會引用檔案，確認檔案存在；需要跨 session 使用時，確認它是 tracked。
   - 如果下一個 Codex 會在本地 worktree 工作，先看 `git status`，並在 prompt 或 brief 裡說清楚預期狀態。
   - 不要為了讓 prompt 看起來完整，而跑昂貴、破壞性、或高風險檢查。

5. **產出結果**
   - 給使用者一段簡短 zh-tw brief，方便快速 proofread。
   - 用 code block 提供 final `/goal` prompt。
   - `/goal` prompt 預設也用 zh-tw；只有 exact names、paths、commands、config snippets、tool names 保持原文。
   - 使用 imperative instructions、exact names、exact paths、明確 deliverable checklist。
   - 決策定案後，移除 `maybe`、`probably`、`I think` 這類模糊字眼。

## `/goal` Prompt 建議結構

可優先用這個形狀：

```text
使用 <tools/capabilities>。

請依照 <tracked task spec path> 執行。

Goal:
<一句話描述具體 outcome>

Context:
- <只放下一個 Codex 必須知道的背景>

Instructions:
1. 先 inspect current state。
2. 只做 allowed changes。
3. 在 <risky actions> 前先問使用者。
4. 用 <specific smoke test> 驗證。
5. 回報 <specific deliverables>。

Local side effects:
- May edit: <paths>
- Must not edit: <paths>
- 不要 commit / push，除非使用者明確要求。
```

## Task Spec File Guidance

出現以下情況時，建立 task spec file：

- `/goal` prompt 會超過 4000 characters。
- 任務有很多步驟、安全規則、或 external systems。
- 下一個 Codex 需要 exact config snippets、topic lists、command formats、verification criteria。
- 任務之後需要 audit trail。

依 repo 慣例選檔案位置：

- `runbook/`：operational setup、VM changes、config changes、incident-style handoff。
- `studies/`：conceptual research 或 analysis。
- repo 已有明確 docs/spec 目錄時，沿用既有慣例。
- 不要在已有結構規則的 repo 裡自行發明新的 top-level directory。

## Smoke Test Examples

- `git status --short`
- 用 `test -f` 或 `rg --files` 確認 referenced files 存在。
- 用 `command -v <tool>` 確認 required command 存在，並用 `<tool> --version` 或等價指令確認可執行。
- 若 `/goal` 指定 Playwright CLI 或 `agent-browser`，檢查 exact CLI path、version、relevant help command，並確認對應 skill/plugin 在 Codex 可見；不要用另一個 browser tool 的存在替代這項檢查。
- 如果快速且安全，跑 narrow syntax check 或 targeted test。
- 對 external systems，先 inspect current state，再寫需要 names、IDs、branches、resources 的指令。

## Final Response Checklist

交給使用者前，確認包含：

- task name / scope。
- 短版 `/goal` prompt，低於 4000 characters。
- 如果使用 tracked task spec file，提供該 path。
- local side effects 與 external side effects。
- ask-first boundaries。
- verification steps。
- 已完成或明確列出的 CLI/skill/plugin availability checks 與 smoke tests。
- final report expectations。
- zh-tw brief，讓使用者可以快速 proofread。
