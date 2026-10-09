---
name: delegate
description: "規劃或把實作、研究、review 委派給另一個 agent 時使用：決定交給哪個 provider 或 worker、回答 quota / rate-limit / usage-reset 問題，或以 headless 方式跑 codex、grok、claude CLI（codex exec、grok -p、claude -p）。整條流程都在這裡：要不要委派、哪個角色交給誰、讓寫入模式安全的 sandbox profile、spec 格式，以及驗收規則。"
allowed-tools: Bash
---

# Delegate

Claude Code、Codex、Grok 都會載入這份檔案（Grok 透過 `~/.claude/skills` 找到它）。

```
委派地圖           [A]=一直載入  [L]=需要時才讀  [R]=執行時算出來
------------------------------------------------------------------------
[A] agents/AGENTS.md「委派與跨 agent」：先用內建 subagent；會寫檔的
    CLI 只能走 `delegate`；永不 bypass；tmux 預設唯讀
                 |  「任務很重／工具迴圈很長／想要第二意見」
                 v
[L] skills/shared/delegate/SKILL.md   （本檔；README.md 指到這裡）
    1 WHEN   ≤10 行的修改 -> 自己做
             >20 次同樣形狀的迴圈、ssh/gh 大量掃描、大批修改 -> 委派
    2 WHO    [R] scripts/pick-worker -> provider + 理由 + reset 時間
             角色：實作 -> quota 最多的 | review -> 有範圍限制的唯讀
                   guardrail reviewer -> 全新的 Claude，用 Fable
    3 HOW    provider == 自己的 runtime？--是--> 內建 subagent
                      | 否                   （Agent / codex / spawn_subagent）
                      v
             spec 寫進檔案；runbook/<provider>.md  <- profile：
             （精確的 CLI flag 與怪癖）   codex/cc-worker[-ro].config.toml
                                          grok/sandbox.toml
    4 ACCEPT 驗證指令自己重跑；空 diff = 拒絕；
             guardrail 修改 -> push 前找全新 reviewer
------------------------------------------------------------------------
[persona] claude/agents/orchestrator.md（`cldo`）：同一條路，WHEN 更嚴
[L] skills/shared/tmux-orchestration：另一種介面（看得到的 pane），
    只由人呼叫；WHEN/WHO/ACCEPT 仍以本檔為準
```

## When

- 單一檔案、大約 10 行以內的修改，或委派的成本比工作本身還高：自己做。
- 任務眼看要把 controller 的 context 燒在機械式的反覆操作上，就算每一步看起來都很簡單，也預設委派：超過大約 20 次同樣形狀的工具迴圈（讀檔／grep／修改來回、翻 log）、對遠端主機跑一批 SSH 指令、掃過大量 GitHub issue／PR／run、需要抓很多頁的大範圍網路研究、跨很多檔案的大批修改。
- 工作需要 spec、驗收標準和另一個負責實作的 owner時就委派，前端工作也一樣：controller 握著設計意圖，自己做畫面驗證。
- 判斷、範圍、架構、debug 找根因、看 diff、git 所有權都留在 controller 這邊。原因查清楚之後，再把具體的修正委派出去。
- 退路：不要預先猜 worker 會失敗，先派出去再說。給了具體的修正回饋、它還是連兩次沒達到驗收標準，就留下 diff 裡有用的部分，自己收尾。

## Who

用角色分派，不寫死 provider 名稱：`scripts/pick-worker` 會依即時 quota 挑 provider。

- **重度實作**（大批修改、很多檔案、跑很久）→ 目前 runtime 的內建 subagent，或套 sandbox profile 的 headless CLI worker；挑剩餘 quota 最多的 provider。headless 只是選項，不是非用不可。
- **Review、唯讀研究、第二意見** → 有範圍限制的唯讀 worker；這裡換一個 provider 沒問題，常常還更有用。不要只為了換 provider 就多扛一套介面的成本。
- **Guardrail / prompt / SSOT reviewer** → 一律找全新的 Claude subagent，用 Fable，一次做完 safety 與 simplify。重點是「全新」，不是哪家 provider：作者腦中帶著這次修改的脈絡，最看不出過時的 flag 和自相矛盾。這個角色刻意不用 Codex（太過防禦、會塞一堆多餘的脈絡）；需要對立觀點的 code review，還是可以用它有範圍限制的唯讀 reviewer。

模型原則：

- 任何交付物都照 `intelligence > taste > cost` 取捨；成本只能當個案的例外，從來不是決定性因素。
- 便宜的模型適合 spec 寫清楚的機械工作（migration、log 分類、批次讀檔、grep 式調查）。需要品味的工作，像 UI、文案、API 設計、架構、計畫 review，交給你能用的最強模型（Claude 的部分看下一條）。
- Claude subagent 一律明確指定 `model`，不靠繼承。判斷類工作（review、規劃、架構、taste、難解的 debug）直接用 `fable`，不用先問；其他工作用 `opus`。`pick-worker` 顯示 Claude quota 偏低、或 Fable 撞到上限時，退回 `opus` 並講明。
- 絕不委派給 Haiku；使用者用過，幻覺很嚴重。
- 使用者指定的模型絕不偷偷換掉。quota 逼得非換不可，先講再換。

## How

1. 執行 `~/.claude/skills/delegate/scripts/pick-worker`（照寫這個絕對路徑；在 Claude Code 裡要帶 `dangerouslyDisableSandbox`）。它會印出剩餘 quota、推薦的 provider 與理由，以及對應的 `runbook/<provider>.md`。`--provider <name>` 強制指定；`--quiet` 只印推薦結果。
2. **推薦的 provider 就是你目前所在的 runtime 時，用內建 subagent**（Claude Code：`Agent` tool；Codex：內建 subagent；Grok：`spawn_subagent`）。絕不從 shell 呼叫自己的 CLI。每份 runbook 裡的 CLI 用法是給「不同 runtime」的呼叫方用的。
3. 寫 spec，照 runbook 派出去，再套用下面的驗收規則。

三條絕對規則：

1. **寫入模式一定要套 sandbox profile。** 任何可能碰到檔案的 headless CLI，都要跑在 kernel 層的 sandbox profile 下：寫入只限 workspace 和暫存目錄（`/tmp`、`$TMPDIR`；grok 另加 `~/.grok/`），禁止「讀取」憑證路徑，平台支援的話把網路關掉。**唯讀模式也要套 profile**：唯讀只擋寫入、不擋讀取，沒套 profile 的話，憑證還是會被讀進模型 context。有兩條路沒有 kernel profile：`codex review`（沒有 `-p` flag，看 `codex review --help`）和 `claude -p`（只有設定層的限制，見 `runbook/claude.md`），這兩條都只能餵可信任的輸入。
2. **永不 bypass。** `danger-full-access`、`--dangerously-bypass-*`、`--yolo`、`bypassPermissions` 在任何模式都禁止，沒有例外。
3. **自帶 sandbox 的 CLI 要跑在 Claude Code 的 Bash sandbox 外面**（`dangerouslyDisableSandbox: true`；巢狀 Seatbelt 會報 `sandbox initialization failed`），路徑一律給絕對路徑：sandbox 內外的 `$TMPDIR` 不一樣。

Spec 格式，每次委派都要有這六項：目標 · 範圍內的檔案 · 介面（要遵守的 signature、schema、CLI 合約）· 限制 · 驗證指令 · reasoning effort。寫成檔案，傳絕對路徑過去。

前端：controller 把設計意圖寫進 spec，然後自己跑 app、截圖，帶著具體的畫面回饋重新派工，直到 UI 符合設計意圖。

## Accept

- 驗證指令由 controller 自己重跑；worker 說「測試通過」只是宣稱，不是證據。
- 回報「完成」但 diff 是空的，就是拒絕（常常是 worker 自己的指示擋住了），絕不算成功。
- 關鍵宣稱用便宜的唯讀檢查確認：grep 有沒有殘留的引用、`git status` / `git diff --stat`、確認檔案真的搬了或刪了、只讀準確度真正要緊的那一段。
- 打開大檔案前先 `wc -l`，再讀關鍵的那一段。worker 輸出很長時，叫便宜的 subagent 摘要，自己只核對決定能不能驗收的那幾段：context 乾淨的 reviewer 至少跟帶著一長串對話的 controller 一樣可靠。
- 大型交付物把「完整」review 交給全新的 worker，不要自己從頭重讀。某個面向沒過，就修那個面向、只重評那個面向；重評的 prompt 要帶上原本的失敗標準和這次改了什麼。
- 每份 worker 合約都寫明「合約範圍外的 CI 失敗只回報、不修」：不然平行的 worker 會各自修同一個繼承來的紅燈，同樣的修正進來 N 次。
- Guardrail / SSOT 修改：先 commit，再照 `## Reviewer 授權` 找全新 reviewer，通過再 push。

## Fallback

1. 內建 subagent 卡住 → 如果還在 `## When` 的門檻內，就由目前的 agent 自己收尾。
2. 還是卡住 → 把 review 或研究改交給另一家 provider 的唯讀 worker。
3. 每家 provider 的 quota 都偏低 → `pick-worker` 會印出最早的 reset 時間；睡到那時候（留一點緩衝，不要留著 lock 或寫一半的檔案），或用 `--provider grok`，codexbar 看不到 grok 的 quota。
4. 醒來後重跑 `pick-worker`，再繼續被打斷的工作。quota 數字絕不憑記憶背；reset 時間不清楚就回報 blocker，不要用猜的。

## Reviewer 授權

- 使用者持續授權其他 agent（含已設定的外部 AI reviewer）做 review，不必逐次詢問。
- 送出 diff、prompt 或檔案前先檢查實際待傳資料有沒有 secret、憑證、private key 或未公開個資；發現敏感內容、無法判斷，或目的地與範圍超出既有 reviewer workflow 時才停下確認。
- 這項授權只涵蓋 review：不授權 reviewer 寫檔、執行外部 mutation，或繞過其他工具與權限邊界。
- guardrail / SSOT 改動的 reviewer 同時做 safety 與 simplify review。simplify 看三件事：只針對單次事故的過窄規則、過度工程化、能不能換成更通用的說法；逐項回報 Keep / Simplify / Drop。

上游來源：改寫自 `blader/arbitrage`，commit `ccfd55098cc9e0b9910bc5c0f67a16a2fd61d5bd`。
