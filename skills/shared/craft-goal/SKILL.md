---
name: craft-goal
description: 協助撰寫、縮短、驗證、整理可交給下一個 agent session（Claude Code 或 Codex）執行的 handoff prompt，含 Codex app 的 `/goal`。當使用者要寫 `/goal`、準備 handoff prompt、把模糊任務整理成可執行 goal、要依任務性質與剩餘 quota 決定交給 CC 還是 Codex、需要 clarification、research、task spec file、side-effect boundary、或 quick smoke test 時使用。
disable-model-invocation: true
---

# Craft Goal

使用這個 skill，把一個粗略任務想法整理成下一個 agent session 可以可靠執行的 handoff prompt。目標不是寫漂亮 prompt，而是做出能交棒、能驗證、風險邊界清楚的 handoff。

## 先選接棒者：CC 還是 Codex

產出 prompt 前先決定交給誰，兩個因素一起看：

- **預設路由**：讀 `~/dotfiles/codex/notes/worker-routing.md`（路由規則）決定交給 CC 還是 Codex。
- **quota 肥瘦**：用 quota skill（`codexbar usage --provider both --source cli`）看即時餘量；在 SSOT 規則之內，其他條件接近時選較肥的一邊。

目標介面隨接棒者決定：Codex app `/goal`（有字元數上限，以 `scripts/check_goal_prompt.py` 為準）、codex CLI、claude CLI、或使用者手動貼。不要替 handoff 自行指定 tmux；只有 human 明確要求接棒 agent 使用 tmux 時才能加入。字元數上限只適用 Codex app `/goal`，CLI 交棒改用 task spec file + 一行 pointer 即可，不受此限。

使用者預設用 zh-tw proofread，所以除非使用者明確要求英文，**輸出給使用者的 brief 與 `/goal` prompt 都預設用繁體中文**。保留必要 English technical terms，例如 `/goal`、Codex、GitHub、VM、SSH、API、CLI、token、commit、push、branch、file path、command、config key、model ID、UI label。

## 核心流程

1. **釐清任務**
   - 找出使用者真正要的 outcome、target environment、需要的 tools、完成標準。
   - 只有在缺失資訊會改變 scope、risk、命名、或實作方式時才問問題。
   - 先定好命名、topic、target path、side-effect boundary，再產生 final `/goal`。

2. **區分短 prompt 與詳細 spec**
   - 實際貼進 `/goal` 的 prompt 有字元數上限，上限由本 skill 的 `scripts/check_goal_prompt.py` 定義。把草稿從 stdin 餵給它（例如 `python3 ~/dotfiles/skills/shared/craft-goal/scripts/check_goal_prompt.py <<'EOF' ... EOF`），沒通過就縮短 prompt 或把內容移進 spec file，反覆到通過後才交給使用者。
   - 如果任務複雜，先在相關 repo 寫一份 tracked task spec file，再讓 `/goal` 引用該檔案。
   - ignored temp file 只能當 scratch draft；如果接棒 agent 必須讀到，請放在 tracked file。
   - **有 task spec file 時，`/goal` prompt 應極短，只負責指向 spec file 與補充少量 launch-time instruction。** 不要把 spec 摘要、任務清單、side-effect boundary、verification checklist 再複製一遍到 prompt；那些內容應留在 spec 裡。
   - `/goal` prompt 是一次性 chat text，只放在 chat code block：不寫進 repo、不建立 `goal-prompt.md`、`prompt.md` 之類的 prompt 檔或 scratch draft、不放在 spec 檔開頭、不 commit 進 git history，除非使用者明確要求保存 prompt 本身。review notes 或僅為溝通方便建立的臨時檔案同樣不建立、不 commit。若不小心 commit/push 了這類檔案，優先移除或 amend；是否改寫 remote history 依使用者要求與風險決定。
   - 如果使用者說「我只想 review spec」，final response 只給 spec path 和 chat 裡的短 prompt。

3. **定義 side effects**
   - 明確寫出接棒 agent 可以讀或改哪些 local files。
   - 明確寫出可能會改哪些 external systems，例如 VM config、Telegram、GitHub、Vercel、browser state。
   - 明確禁止 destructive、permission-sensitive、billing、credential、或 broad-scope changes，除非使用者另外批准。
   - 寫清楚接棒 agent 是否可以 commit / push。預設不要 commit / push，除非使用者要求。
   - 如果使用者要求「完成後備份」或「讓接棒 agent 好 review」，可以在 spec 裡允許接棒 agent 在驗證通過、確認沒有 secrets/private data/unrelated changes 後 commit + push。

4. **做快速 feasibility check**
   - 檢查相關 repo paths、docs、commands、installed tools、existing config，避免接棒 agent 第一步就失敗。
   - 如果 `/goal` 依賴特定 CLI、plugin、connector、skill、browser automation、或其他工具，確認它不只是「應該存在」，而是當下真的可見且可用。
   - 對 CLI 工具，至少檢查 command path 與版本；如果使用者要求 latest/up-to-date，確認版本是否符合當下可用資訊或明確標註未驗證。
   - 對 Playwright CLI、`agent-browser` 這類會被接棒 agent 直接操作的工具，做最低成本 smoke test，例如確認 exact CLI 的 `--version` 與 relevant help command 可執行；若任務依賴 standalone browser，確認可用的啟動方式或把待驗證項寫進 handoff。
   - 不要混淆不同 browser automation surface：Playwright CLI、`agent-browser` CLI、MCP browser tools、以及 in-app browser skill 是不同能力；handoff 必須寫 exact tool name，並驗證同一個 tool。
   - 對 skill/plugin 依賴，確認 skill/plugin 在接棒 agent 當前可見路徑或 tool discovery 裡可見；不要只確認 repo tree 有檔案。
   - 如果 `/goal` 會引用檔案，確認檔案存在；需要跨 session 使用時，確認它是 tracked。
   - 如果接棒 agent 會在本地 worktree 工作，先看 `git status`，並在 prompt 或 brief 裡說清楚預期狀態。
   - 不要為了讓 prompt 看起來完整，而跑昂貴、破壞性、或高風險檢查。

5. **做 adversarial review gate**
   - 若任務涉及 external systems、commit / push、SSH / VM、GitHub、Vercel、browser automation、多 repo、多 agent handoff、credentials、billing、data-loss risk，或需要 task spec file，交付前先做 adversarial review。
   - 可以開 subagent 時，傳給 reviewer 的資料只包含 raw artifacts：使用者原始需求摘要、draft `/goal`、task spec path 或必要 excerpt。
   - 不要把自己的診斷、預期答案、懷疑問題、打算採用的修法傳給 reviewer；review 的價值來自獨立挑錯，不是附和。
   - 要求 reviewer 專門找 ambiguous scope、unsafe side effects、missing ask-first boundary、unverifiable success criteria、tool/path assumptions、以及 prompt 是否通過 `scripts/check_goal_prompt.py`。
   - 若沒有 subagent 工具或任務明顯 low-risk，改做 self-adversarial pass，並在 brief 裡說明未開 subagent 的原因。
   - 對 review findings 要明確處置：接受並修改、拒絕並說明理由，或列為接棒 agent 必須先確認的 open question。
   - 如果使用者明確要求 reviewer subagent review spec，review 對象應是 **目前最終 spec file**，不是過期 draft prompt。若 review 後又大幅改寫 spec，必須重新 review 或明確說明改動很小、不影響 review 結論。
   - reviewer 結論若提到已修的 blocking finding，要本地確認檔案真的包含該修正，再告訴使用者「可 review」。

6. **產出結果**
   - 給使用者一段簡短 zh-tw brief，方便快速 proofread。
   - 用 code block 提供 final `/goal` prompt。
   - `/goal` prompt 預設也用 zh-tw；只有 exact names、paths、commands、config snippets、tool names 保持原文。
   - 使用 imperative instructions、exact names、exact paths、明確 deliverable checklist。
   - 決策定案後，移除 `maybe`、`probably`、`I think` 這類模糊字眼。
   - 若已有 task spec file，final `/goal` prompt 優先使用一行 pointer 格式，例如：「請在 `<repo>` 依照 `<spec path>` 完成所有任務；<commit/push policy>；完成後回報 <deliverables>。」詳細任務不要重複貼在 prompt。
   - final response 要明確分開：
     - **給使用者 review 的檔案**：通常只列 spec path。
     - **要貼進 `/goal` 的文字**：放在 chat code block。
     - **已 commit/push 的狀態**：如果有，列 commit hash 與 worktree state。

## `/goal` Prompt 建議結構

若沒有 task spec file，可優先用這個形狀：

```text
使用 <tools/capabilities>。

請依照 <tracked task spec path> 執行。

Goal:
<一句話描述具體 outcome>

Context:
- <只放接棒 agent 必須知道的背景>

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

若已建立 tracked task spec file，`/goal` prompt 應改用極短 pointer，不要重複 spec：

```text
請在 `<repo path>` 依照 `<tracked spec path>` 完成所有任務；<commit/push policy>；完成後回報 <final deliverables>。
```

## Task Spec File Guidance

出現以下情況時，建立 task spec file：

- `/goal` prompt 超過 `scripts/check_goal_prompt.py` 的上限。
- 任務有很多步驟、安全規則、或 external systems。
- 接棒 agent 需要 exact config snippets、topic lists、command formats、verification criteria。
- 任務之後需要 audit trail。

依 repo 慣例選檔案位置：

- `runbook/`：operational setup、VM changes、config changes、incident-style handoff。
- `studies/`：conceptual research 或 analysis。
- repo 已有明確 docs/spec 目錄時，沿用既有慣例。
- 不要在已有結構規則的 repo 裡自行發明新的 top-level directory。
- spec file 只放接棒 agent 必須讀的 durable instruction。
- spec file 要讓使用者容易 review：標題清楚、段落短、使用「問題 / 要做到 / 驗證」這種穩定結構；不要把 reviewer process、draft prompt 歷史、或 agent 自我辯解寫進去。

## Smoke Test Examples

- `git status --short`
- 用 `test -f` 或 `rg --files` 確認 referenced files 存在。
- 用 `command -v <tool>` 確認 required command 存在，並用 `<tool> --version` 或等價指令確認可執行。
- 若 `/goal` 指定 Playwright CLI 或 `agent-browser`，檢查 exact CLI path、version、relevant help command，並確認對應 skill/plugin 對接棒 agent 可見；不要用另一個 browser tool 的存在替代這項檢查。
- 如果快速且安全，跑 narrow syntax check 或 targeted test。
- 對 external systems，先 inspect current state，再寫需要 names、IDs、branches、resources 的指令。

## Final Response Checklist

交給使用者前，確認包含：

- task name / scope。
- 短版 `/goal` prompt，已通過 `scripts/check_goal_prompt.py`。
- 如果使用 tracked task spec file，提供該 path。
- local side effects 與 external side effects。
- ask-first boundaries。
- verification steps。
- 已完成或明確列出的 CLI/skill/plugin availability checks 與 smoke tests。
- adversarial review disposition：若有跑 review，列出 accepted / rejected findings；若沒跑，簡短說明原因。
- final report expectations。
- zh-tw brief，讓使用者可以快速 proofread。
