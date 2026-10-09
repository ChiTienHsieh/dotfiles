---
name: delegate
description: "規劃或把實作、研究、review 委派給另一個 agent 時使用：決定交給哪個 provider 或 worker、回答 quota / rate-limit / usage-reset 問題，或以 headless 方式跑 codex、grok、claude CLI（codex exec、grok -p、claude -p）。整條流程都在這裡：要不要委派、哪個角色交給誰、讓寫入模式安全的 sandbox profile、spec 格式，以及驗收規則。"
allowed-tools: Bash(~/.claude/skills/delegate/scripts/pick-worker:*)
---

# Delegate

Claude Code、Codex、Grok 都會載入這份檔案（Grok 透過 `~/.claude/skills` 找到它）。流程是 When → Who → How → Accept；`claude/agents/orchestrator.md`（`cldo`）走同一條路，只是 When 更嚴；`tmux-orchestration` 是另一種介面（看得到的 pane），只由人呼叫，規則仍以本檔為準。

## When

- 單一檔案、大約 10 行以內的修改，或委派比自己做還貴：自己做。
- 會把 controller 的 context 燒在機械式反覆操作上的就委派，就算每一步都很簡單：超過大約 20 次同樣形狀的工具迴圈（讀檔／grep／修改來回、翻 log）、對遠端主機跑一批 SSH、掃大量 GitHub issue／PR／run、要抓很多頁的網路研究、跨很多檔案的大批修改。
- 判斷、範圍、架構、找根因、看 diff、git 所有權留在 controller；原因查清楚之後，再把具體的修正委派出去。
- 不要預先猜 worker 會失敗，先派再說。給了具體回饋還是連兩次沒達到驗收標準，就留下 diff 裡有用的部分，自己收尾。

## Who

用角色分派，不寫死 provider：`scripts/pick-worker` 依即時 quota 挑 provider。

- **重度實作**（大批修改、很多檔案、跑很久）→ 目前 runtime 的內建 subagent，或套 sandbox profile 的 headless CLI worker；挑剩餘 quota 最多的 provider。headless 是選項，不是非用不可。
- **Review、第二意見** → 全新的 Claude 唯讀 subagent，用 Fable，照 `## Reviewer 授權` 先審意圖。
- **唯讀研究** → 有範圍限制的唯讀 worker；這裡換 provider 沒問題，常常還更有用。
- **Guardrail / prompt / SSOT reviewer** → 同上，一次做完 intent、safety、simplify。重點是「全新」：作者帶著修改的脈絡，最看不出過時的 flag 和自相矛盾。這個角色不用 Codex（太防禦、會塞一堆多餘的脈絡）；要對立觀點就另加一個別家 provider 的唯讀 worker。

模型原則：

- `intelligence > taste > cost`，成本只能當個案例外。便宜模型只做 spec 寫清楚的機械工作（migration、log 分類、批次讀檔、grep 式調查）；需要品味的工作（UI、文案、API 設計、架構、計畫 review）交給能用的最強模型。
- Claude subagent 一律明確指定 `model`，不靠繼承：判斷類工作（review、規劃、架構、taste、難解的 debug）直接用 `fable`，不用先問；其他用 `opus`。`pick-worker` 顯示 Claude quota 偏低、或 Fable 撞到上限時，退回 `opus` 並講明。
- 絕不委派給 Haiku，幻覺很嚴重。使用者指定的模型絕不偷偷換掉；quota 逼得非換不可，先講再換。

## How

1. 跑 `~/.claude/skills/delegate/scripts/pick-worker`（照寫這個絕對路徑；在 Claude Code 裡要帶 `dangerouslyDisableSandbox`）。它會印出剩餘 quota、推薦的 provider 與理由，以及對應的 `runbook/<provider>.md`；`--provider <name>` 強制指定，`--quiet` 只印推薦結果。
2. **推薦的 provider 就是你所在的 runtime 時，用內建 subagent**（Claude Code：`Agent` tool；Codex：內建 subagent；Grok：`spawn_subagent`），絕不從 shell 呼叫自己的 CLI。runbook 裡的 CLI 用法只給不同 runtime 的呼叫方。
3. spec 寫成檔案、傳絕對路徑，六項都要有：目標 · 範圍內的檔案 · 介面（要遵守的 signature、schema、CLI 合約）· 限制 · 驗證指令 · reasoning effort。前端工作另把設計意圖寫進 spec，controller 自己跑 app、截圖，帶著具體的畫面回饋重派，直到 UI 符合設計意圖。

三條絕對規則：

1. **寫入模式一定要套 sandbox profile。** 任何可能碰到檔案的 headless CLI，都要跑在 kernel 層的 sandbox profile 下：寫入只限 workspace 和暫存目錄（`/tmp`、`$TMPDIR`；grok 另加 `~/.grok/`），禁止「讀取」憑證路徑，平台支援的話把網路關掉。**唯讀模式也要套 profile**：唯讀只擋寫入、不擋讀取，沒套 profile 的話憑證還是會被讀進模型 context。有兩條路沒有 kernel profile：`codex review`（沒有 `-p` flag，看 `codex review --help`）和 `claude -p`（只有設定層的限制，見 `runbook/claude.md`），這兩條都只能餵可信任的輸入。
2. **永不 bypass。** `danger-full-access`、`--dangerously-bypass-*`、`--yolo`、`bypassPermissions` 在任何模式都禁止，沒有例外。
3. **自帶 sandbox 的 CLI 要跑在 Claude Code 的 Bash sandbox 外面**（`dangerouslyDisableSandbox: true`；巢狀 Seatbelt 會報 `sandbox initialization failed`），路徑一律給絕對路徑：sandbox 內外的 `$TMPDIR` 不一樣。

## Accept

- 驗證指令由 controller 自己重跑；worker 說「測試通過」只是宣稱，不是證據。
- 回報「完成」但 diff 是空的，就是拒絕（常常是 worker 自己的指示擋住了），絕不算成功。
- 關鍵宣稱用便宜的唯讀檢查確認：grep 有沒有殘留的引用、`git status` / `git diff --stat`、確認檔案真的搬了或刪了。大檔先 `wc -l` 再讀關鍵段；worker 輸出很長就叫 subagent 摘要，自己只核對決定能不能驗收的那幾段。
- 大型交付物的完整 review 交給全新的 worker，不要自己從頭重讀。某個面向沒過，就只修、只重評那個面向；重評的 prompt 要帶上原本的失敗標準和這次改了什麼。
- 每份 worker 合約都寫明「合約範圍外的 CI 失敗只回報、不修」，不然平行的 worker 會各自修同一個繼承來的紅燈。
- Guardrail / SSOT 修改：先 commit，再照 `## Reviewer 授權` 找全新 reviewer，通過再 push。

## Fallback

1. 內建 subagent 卡住 → 還在 `## When` 的門檻內，就由目前的 agent 自己收尾。
2. 還是卡住 → review 或研究改交給另一家 provider 的唯讀 worker。
3. 每家 provider 的 quota 都偏低 → `pick-worker` 會印出最早的 reset 時間；睡到那時候（留一點緩衝，不要留著 lock 或寫一半的檔案），或用 `--provider grok`，codexbar 看不到 grok 的 quota。
4. 醒來後重跑 `pick-worker`，再繼續被打斷的工作。quota 數字絕不憑記憶背；reset 時間不清楚就回報 blocker，不要用猜的。

## Reviewer 授權

- 使用者持續授權其他 agent（含已設定的外部 AI reviewer）做 review，不必逐次詢問。這項授權只涵蓋 review：不授權 reviewer 寫檔、執行外部 mutation，或繞過其他工具與權限邊界。
- 送出 diff、prompt 或檔案前先檢查實際待傳資料有沒有 secret、憑證、private key 或未公開個資；發現敏感內容、無法判斷，或目的地與範圍超出既有 reviewer workflow 時才停下確認。
- 每個 reviewer 都先審意圖再看實作：prompt 照抄使用者原話與要解決的問題，不轉述，因為 reviewer 沒有對話脈絡。請它先寫出自己理解的使用者意圖，再判斷有沒有更理想、更簡潔的做法，最後才看程式碼與措辭。
- 會改變做法或範圍的意圖層建議只是推薦：controller 轉給使用者決定，不因此卡住 push；同一意圖下更簡潔的寫法照 simplify 規則處理。
- guardrail / SSOT 改動的 reviewer 同時做 intent、safety 與 simplify review。simplify 看三件事：只針對單次事故的過窄規則、過度工程化、能不能換成更通用的說法；逐項回報 Keep / Simplify / Drop。

上游來源：改寫自 `blader/arbitrage`，commit `ccfd55098cc9e0b9910bc5c0f67a16a2fd61d5bd`。
