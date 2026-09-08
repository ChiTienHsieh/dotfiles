---
name: delegate
description: "委派有明確範圍的實作、研究或 review，查 quota／reset 時間，或安全啟動 headless CLI worker 時使用。"
allowed-tools: Bash
---

# Delegate

共用委派規則；`claude/agents/orchestrator.md` 是使用者手動啟動的指揮模式。
`tmux-orchestration` 另管可見 terminal，human-invoked only。

## When

- 有可獨立完成的明確子任務，且平行處理能省時或提升品質時委派；小改動或緊密相依的工作直接完成，不用行數或工具次數當門檻。
- Controller 負責範圍、整合與驗收，worker 執行期間繼續不依賴其結果的工作。
- Worker 卡住時，依原因選擇具體回饋、換適合的 worker 或自行完成；不強制先派一次或重試固定次數。

## Who

- 預設使用目前 runtime 內建 worker：use your native subagent。不要從自己的 runtime 再呼叫同 provider 的 CLI；跨 provider 才讀對應的 `runbook/<provider>.md`。
- 研究與 review 使用有明確範圍的唯讀 worker。實作分配檔案責任，告知 worker 有其他人同時工作，不得覆寫他人變更。
- **Guardrail / prompt / SSOT reviewer** 是 provider 路由的例外：使用 fresh、無作者對話脈絡的最強 Claude reviewer，同時做 safety 與 simplify。Codex 可做一般 code review，不替代此角色。
- 保留使用者指定的 model；需要更換時先說明。選擇仍以 `intelligence > taste > cost` 為原則；機械任務可用較小 model，不用 Haiku。
- 只有需要選 provider、查餘量或處理 quota blocker 時才跑 `scripts/pick-worker`；解析為本 skill 下的絕對路徑，Claude Code 從 Bash sandbox 外執行。已選 native worker 的小任務不先查所有 provider；未知餘量不當作零或無限。

## How

- Native worker 的 prompt 交代目標、範圍、權限與預期結果即可；介面、驗證方式與 effort 按需要補充。
- Headless CLI worker 使用獨立 spec 檔與絕對路徑，包含 objective、files in scope、interfaces、constraints、verification command、reasoning effort；跨 session 的交接也需可讀到的持久 spec。
- 所有 worker 只回報超出契約的 CI 失敗，不自行修正。Frontend 的 spec 要含設計意圖，controller 以實際畫面驗收。
- 只有讀取對應 provider runbook 後才啟動 CLI；旗標、profile 路徑與工具怪癖留在 runbook。

### CLI 安全邊界

1. Write 與 read-only CLI 都要用 sandbox profile：限制 workspace／temp 寫入、禁止讀取 credentials，並依平台限制網路。唯讀不代表能安全讀取機密。僅 `codex review` 與 `runbook/claude.md` 的 `claude -p` lane 沒有 kernel profile，兩者只接收可信輸入；Claude lane 的設定限制與即時 deny 檢查仍須遵守。
2. `danger-full-access`、`--dangerously-bypass-*`、`--yolo`、`bypassPermissions` 一律禁止。
3. 自帶 sandbox 的 CLI 在 Claude Code Bash sandbox 外執行（`dangerouslyDisableSandbox: true`），避免 nested Seatbelt 失敗；這不允許移除 CLI 自己的 profile。使用絕對路徑，因內外 `$TMPDIR` 可能不同。

## Accept

- 檢查實際交付物、diff 與驗證指令的原始輸出或 log，不能只接受 worker 的摘要或「tests pass」。完成必要 checks 後，只在整合修改、失敗、未解疑慮或證據不足時重跑相關驗證；大型結果先讀決定驗收的部分，不另派 worker 只為摘要。
- 預期需要修改卻沒有 diff 時查明原因；唯讀研究、review 或有證據證明不需修改，都可以是有效交付，空 diff 不等於拒絕。
- Review 後只重查受修改影響的部分與尚未解決的問題。
- Guardrail / SSOT 改動：先 commit，再由上述 fresh reviewer 依下節審查，通過才 push。

## Fallback

有可用 worker 或 controller 能安全完成時繼續；quota 真的阻擋工作才查即時餘量與 reset 時間。不要背數字、假設未知 provider 可用，或默默替換使用者指定 model。需要稍後續做時依 runtime 的排程能力與使用者授權處理，不強制長時間 sleep。

## Reviewer 授權

- 使用者持續授權其他 agent（含已設定的外部 AI reviewer）做 review，不必逐次詢問。
- 送出 diff、prompt 或檔案前先檢查實際待傳資料有沒有 secret、憑證、private key 或未公開個資；發現敏感內容、無法判斷，或目的地與範圍超出既有 reviewer workflow 時才停下確認。
- 這項授權只涵蓋 review：不授權 reviewer 寫檔、執行外部 mutation，或繞過其他工具與權限邊界。
- guardrail / SSOT 改動的 reviewer 同時做 safety 與 simplify review。simplify 看三件事：只針對單次事故的過窄規則、過度工程化、能不能換成更通用的說法；逐項回報 Keep / Simplify / Drop。

Upstream: adapted from `blader/arbitrage` at `ccfd55098cc9e0b9910bc5c0f67a16a2fd61d5bd`.
