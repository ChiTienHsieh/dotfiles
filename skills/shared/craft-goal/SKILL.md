---
name: craft-goal
description: 協助撰寫、縮短、驗證、整理可交給下一個 agent session（Claude Code 或 Codex）執行的 handoff prompt，含 Codex app 的 `/goal`。當使用者要寫 `/goal`、準備 handoff prompt、把模糊任務整理成可執行 goal、在 GitHub Issue 與 tracked task spec file 間選 durable spec、要依任務性質與剩餘 quota 決定交給 CC 還是 Codex、需要 clarification、research、side-effect boundary、或 quick smoke test 時使用。
---

# Craft Goal

使用這個 skill，把一個粗略任務想法整理成下一個 agent session 可以可靠執行的 handoff prompt。目標不是寫漂亮 prompt，而是做出能交棒、能驗證、風險邊界清楚的 handoff。

## 先選接棒者：CC 還是 Codex

產出 prompt 前先決定交給誰，兩個因素一起看：

- **預設路由**：讀 `~/dotfiles/codex/notes/worker-routing.md`（訂閱狀態＋路由規則）決定交給 CC 還是 Codex。
- **quota 肥瘦**：用 quota skill（`codexbar usage --provider both --source cli`）看即時餘量；在 SSOT 規則之內，其他條件接近時選較肥的一邊。

目標介面隨接棒者決定：Codex app `/goal`（受 4000 characters 限制）、codex CLI、claude CLI、或使用者手動貼。不要替 handoff 自行指定 tmux；只有 human 明確要求接棒 agent 使用 tmux 時才能加入。4000-character 限制只適用 Codex app `/goal`；CLI 交棒同樣使用一行 durable-spec pointer，但不受此限。

使用者預設用 zh-tw proofread，所以除非使用者明確要求英文，**輸出給使用者的 brief 與 `/goal` prompt 都預設用繁體中文**。保留必要 English technical terms，例如 `/goal`、Codex、GitHub、VM、SSH、API、CLI、token、commit、push、branch、file path、command、config key、model ID、UI label。

## 核心流程

1. **釐清任務**
   - 找出使用者真正要的 outcome、target environment、需要的 tools、完成標準。
   - 只有在缺失資訊會改變 scope、risk、命名、或實作方式時才問問題。
   - 先定好命名、topic、target path、side-effect boundary，再產生 final `/goal`。

2. **選 durable spec，再寫短 pointer**
   - 先依下方「Durable Spec Routing」判斷 existing GitHub Issue 是否 suitable；suitable 且 receiving agent 可可靠讀取時，優先用 Issue body，不另建重複的 tracked spec。
   - 不 suitable、access 無法驗證、non-GitHub、或沒有 relevant Issue 時，只有在 file storage 的 visibility 與內容敏感度相容時，才依 repo 慣例建立 tracked task spec file；無安全 storage 就 ask-first。
   - 實際貼進 Codex app `/goal` 的 prompt 必須低於目前 4000-character 限制；不論選 Issue 或 file，都只寫 exact pointer 與 launch-time policy，不複製 spec。
   - ignored temp file 只能當 scratch draft；如果接棒 agent 必須跨 session 讀取 file fallback，該檔案必須 tracked。
   - **已有 durable spec 時，`/goal` prompt 應極短。** 不要把 scope、side-effect boundary、verification checklist 再複製一遍；那些內容留在 Issue body 或 tracked spec。
   - **`/goal` prompt 是一次性 chat text，預設不要寫進 repo，也不要建立 temporary prompt artifact file。** 不要建立 `goal-prompt.md`、`prompt.md`、scratch prompt file、不要把 prompt 放在 spec 檔開頭，也不要把 prompt commit 進 git history，除非使用者明確要求保存 prompt 本身。
   - 如果使用者說「我只想 review spec」，final response 只給 Issue URL／number或 spec path，以及 chat 裡的短 prompt；不要新增 prompt file 讓使用者或接棒 agent 讀兩次。

3. **定義 side effects**
   - 明確寫出接棒 agent 可以讀或改哪些 local files。
   - 明確寫出可能會改哪些 external systems，例如 VM config、Telegram、GitHub、Vercel、browser state。
   - 明確禁止 destructive、permission-sensitive、billing、credential、或 broad-scope changes，除非使用者另外批准。
   - 寫清楚接棒 agent 是否可以 commit / push。預設不要 commit / push，除非使用者要求。
   - 如果使用者要求「完成後備份」或「讓接棒 agent 好 review」，可以在 spec 裡允許接棒 agent 在驗證通過、確認沒有 secrets/private data/unrelated changes 後 commit + push。
   - **不要建立或 commit 一次性 prompt 檔、scratch draft、review notes、或僅為溝通方便建立的臨時 artifact。** 若使用者沒有明確要求保存這些檔案，連 temp prompt artifact file 都不要建立；若不小心 commit/push 了這類檔案，優先移除或 amend；是否改寫 remote history 依使用者要求與風險決定。

4. **做快速 feasibility check**
   - 檢查相關 repo paths、docs、commands、installed tools、existing config，避免接棒 agent 第一步就失敗。
   - 如果 `/goal` 依賴特定 CLI、plugin、connector、skill、browser automation、或其他工具，確認它不只是「應該存在」，而是當下真的可見且可用。
   - 對 CLI 工具，至少檢查 command path 與版本；如果使用者要求 latest/up-to-date，確認版本是否符合當下可用資訊或明確標註未驗證。
   - 對 Playwright CLI、`agent-browser` 這類會被接棒 agent 直接操作的工具，做最低成本 smoke test，例如確認 exact CLI 的 `--version` 與 relevant help command 可執行；若任務依賴 standalone browser，確認可用的啟動方式或把待驗證項寫進 handoff。
   - 不要混淆不同 browser automation surface：Playwright CLI、`agent-browser` CLI、MCP browser tools、以及 in-app browser skill 是不同能力；handoff 必須寫 exact tool name，並驗證同一個 tool。
   - 對 skill/plugin 依賴，確認 skill/plugin 在接棒 agent 當前可見路徑或 tool discovery 裡可見；不要只確認 repo tree 有檔案。
   - 如果 `/goal` 會引用 Issue，分別 smoke-test 目前 agent 與 receiving agent 使用的 exact connector／CLI／GitHub App；另一套工具成功不算通過。引用 file 時則確認存在且需要跨 session 使用的版本已 tracked。
   - 如果接棒 agent 會在本地 worktree 工作，先看 `git status`，並在 prompt 或 brief 裡說清楚預期狀態。
   - 不要為了讓 prompt 看起來完整，而跑昂貴、破壞性、或高風險檢查。

5. **做 adversarial review gate**
   - 若任務涉及 external systems、commit / push、SSH / VM、GitHub、Vercel、browser automation、多 repo、多 agent handoff、credentials、billing、data-loss risk，或需要 durable spec，交付前先做 adversarial review。
   - 可以開 subagent 時，傳給 reviewer 的資料只包含 raw artifacts：使用者原始需求摘要、draft `/goal`、Issue URL／body、task spec path 或必要 excerpt。
   - 不要把自己的診斷、預期答案、懷疑問題、打算採用的修法傳給 reviewer；review 的價值來自獨立挑錯，不是附和。
   - 要求 reviewer 專門找 ambiguous scope、unsafe side effects、missing ask-first boundary、unverifiable success criteria、tool/path assumptions、以及 prompt 是否超過 4000 characters。
   - 若沒有 subagent 工具或任務明顯 low-risk，改做 self-adversarial pass，並在 brief 裡說明未開 subagent 的原因。
   - 對 review findings 要明確處置：接受並修改、拒絕並說明理由，或列為接棒 agent 必須先確認的 open question。
   - 如果使用者明確要求 reviewer subagent review spec，review 對象應是 **目前最終 Issue body 或 spec file**，不是過期 draft prompt。若 review 後又大幅改寫 spec，必須重新 review 或明確說明改動很小、不影響 review 結論。
   - reviewer 結論若提到已修的 blocking finding，要本地確認檔案真的包含該修正，再告訴使用者「可 review」。

6. **產出結果**
   - 給使用者一段簡短 zh-tw brief，方便快速 proofread。
   - 用 code block 提供 final `/goal` prompt。
   - `/goal` prompt 預設也用 zh-tw；只有 exact names、paths、commands、config snippets、tool names 保持原文。
   - 使用 imperative instructions、exact names、exact paths、明確 deliverable checklist。
   - 決策定案後，移除 `maybe`、`probably`、`I think` 這類模糊字眼。
   - 若已有 durable spec，final `/goal` prompt 優先使用一行 pointer，指向 exact repo context＋Issue URL／number或 tracked file，補充 commit／push policy、Issue write authority、ask-first boundary與 final report。詳細任務不要重複貼在 prompt。
   - final response 要明確分開：
     - **給使用者 review 的 durable spec**：列 Issue URL／number或 spec path，以及選擇理由。
     - **要貼進 `/goal` 的文字**：放在 chat code block。
     - **已 commit/push 的狀態**：如果有，列 commit hash 與 worktree state。

## Durable Spec Routing

依序執行；任一 gate 無法可靠確認就 fail closed。只有 storage visibility gate 通過時才改用 tracked file，否則 ask-first：

1. **Resolve target**：確認 exact repository、remote platform、Issue URL／number與接棒環境；不得靠相似標題猜 target。
2. **Validate existing Issue**：candidate 必須在同一 repo、open、topic／outcome／acceptance criteria 相符、沒有 conflicting spec或另一個 active owner，並能提供 exact URL＋number。先搜尋去重；不要建立第二張同目的 Issue。
3. **Storage visibility／sensitivity gate**：確認 repository visibility、適用 access controls與 spec storage 的實際讀取範圍。Public storage不得放 secrets、credentials、private data、未公開個資、machine-private topology或 private-repo details。敏感 task只能使用 visibility與access controls皆已驗證相容的 storage；target repo為public、private storage不可驗證或沒有安全 storage時，停止並ask-first，不得把 tracked file當自動 fallback。
4. **Creator／receiver capability gate**：用目前 agent 與 receiving agent 各自將使用的 exact connector／CLI／GitHub App做 read smoke test。只確認 repo tree、Issue URL存在或另一套工具可用不算通過。
5. **Authority gate**：Issue存在、read access、repo push權限都不等於 external-write authority。只有使用者或目前 task 對 exact Issue 明確授權 create／edit／comment／close時，才可執行對應動作；未授權不得先寫再問。新建 Issue也需要明確 create authority，一般「craft a goal」不包含這項授權。
6. **Choose SSOT**：suitable＋receiving-agent readable時，Issue body優先；read-only Issue仍可作 spec，但 progress只能回到明確、持久且已授權的 tracker（例如PR），沒有這類 tracker就只在final report回報並明示無法回寫Issue。其他情況只有通過storage visibility gate時，才依repo慣例用tracked file，不自行發明新目錄。

### Issue body、comments與 concurrency

- Body保存 current executable scope、side-effect boundaries、ask-first conditions與acceptance criteria。會改變後續執行的 scope、risk、allowed side effects或acceptance criteria時，先更新 body；comment只記理由與時間序列。
- Comments只保存 material decision rationale、findings、scope／risk change審查、blocker，以及 PR／CI／deployment／final timeline；不得讓 comment成為唯一有效的新規格，也不留 heartbeat。
- Existing Issue若不是本 flow建立，只有在明確授權 whole-body exclusive ownership，或明確擁有 section且API支援拒絕stale write的conditional／versioned update時才可 edit；否則提出 authorized material comment／回報建議並 fallback，不得 clobber。
- Issue body API通常是整段覆寫。只有API支援conditional／versioned update，或目前task有明確的whole-body exclusive ownership時才可寫入；兩者皆無就不得覆寫body。每次允許的edit仍要：
  1. fresh-read body與`updatedAt`，保存可比較的版本與內容；
  2. 緊鄰寫入前再讀一次；
  3. version或內容改變就停止覆寫、重新整合，無法安全整合則ask-first；
  4. conditional update帶入expected version／precondition；沒有conditional API時，只能依whole-body exclusive ownership更新；
  5. 只改目前task擁有的內容，寫入後立即read-back驗證。
- Comment與close前也要 fresh-read current state，確認 target、scope與authority仍正確。
- Handoff與 final brief都要說明 Issue是read/write或read-only，以及 progress的 durable回報位置。

## `/goal` Pointer Examples

### Existing suitable read/write Issue

```text
請在 `<repo／project context>` 依照 `<exact Issue URL>`（Issue #<number>）完成全部工作；先 fresh-read repo instructions與Issue。依已授權範圍維護Issue body、留下material comments並於完成後close；驗證通過後<commit／push／PR policy>。任何scope或side-effect expansion先問使用者；完成後回報changed files、checks、PR／commit與Issue狀態。
```

### Existing suitable read-only Issue

```text
請在 `<repo／project context>` 依照唯讀的 `<exact Issue URL>`（Issue #<number>）完成全部工作；先 fresh-read repo instructions與Issue。不得edit／comment／close Issue，progress回報到<已授權durable tracker，例如PR；若無則final report>；依<commit／push policy>執行。任何scope或side-effect expansion先問使用者；完成後回報changed files、checks、PR／commit與remaining Issue actions。
```

### Tracked file fallback

```text
請在 `<repo path>` 依照 `<tracked spec path>` 完成所有任務；<commit／push policy>；任何scope或side-effect expansion先問使用者，完成後回報<final deliverables>。
```

以下情況不得勉強使用或建立 Issue：

- Public storage會暴露敏感內容：拒絕寫入；只有已驗證visibility與access controls相容的storage才可使用，否則ask-first。
- 目前或 receiving agent的 exact Issue access無法驗證：只有 storage visibility gate 通過時才改用 tracked file，否則 ask-first。
- 沒有 suitable Issue且使用者未授權建立：不得自行 create；只有 storage visibility gate 通過時才改用 tracked file，否則 ask-first。
- Existing Issue只部分相符、有 conflicting spec或 active owner：不得把它當 executable SSOT或覆寫。

## Task Spec File Guidance

沒有通過 Issue routing gates、但已確認 target file storage適合內容敏感度時，依下列條件建立 task spec file：

- `/goal` prompt 會超過 4000 characters。
- 任務有很多步驟、安全規則或 external systems，且沒有 suitable／readable Issue。
- 接棒 agent 需要 exact config snippets、topic lists、command formats、verification criteria。
- 任務之後需要 audit trail。

依 repo 慣例選檔案位置：

- `runbook/`：operational setup、VM changes、config changes、incident-style handoff。
- `studies/`：conceptual research 或 analysis。
- repo 已有明確 docs/spec 目錄時，沿用既有慣例。
- 不要在已有結構規則的 repo 裡自行發明新的 top-level directory。
- spec file 只放接棒 agent 必須讀的 durable instruction。不要在 spec file 內嵌「這段貼進 `/goal`」的 prompt；那是 launch-time chat text，不是 spec 內容。不要在已選 Issue作 SSOT時再建一份重複 file spec。
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
- 短版 `/goal` prompt，低於 4000 characters。
- durable spec選擇與理由：Issue URL／number或 tracked file path。
- visibility／sensitivity判斷，以及 creator與receiver exact capability smoke checks。
- Issue是read/write或read-only、各項 create／edit／comment／close authority與progress回報位置。
- local side effects 與 external side effects。
- ask-first boundaries。
- verification steps。
- 已完成或明確列出的 CLI/skill/plugin availability checks 與 smoke tests。
- adversarial review disposition：若有跑 review，列出 accepted / rejected findings；若沒跑，簡短說明原因。
- final report expectations。
- zh-tw brief，讓使用者可以快速 proofread。
