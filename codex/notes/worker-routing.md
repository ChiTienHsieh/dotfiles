# Worker 路由 SSOT

哪個 provider 當重活 worker、哪個當 reviewer，由本檔決定。**換訂閱或 quota tier 時只改本檔的「目前 quota tier」區**；其他 prompt（orchestrator persona、arbitrage、guardrail 閘門等）只引用本檔，不得各自寫死 provider 優先序。

## 目前 quota tier（2026-08-02）

- **Codex＝高額度主力**：重活、一般 review、read-only fan-out 預設優先使用。
- **Claude Code＝低額度輔助**：保留給 Claude-specific workflow、controller judgment，或需要不同 provider 的獨立 review。
- **Grok＝低額度輔助**：保留給不同 provider 的 second opinion，或 Codex/Claude 都卡住時的 fallback。

quota tier 只決定預設路由，不代表當下剩餘額度。長任務與 limit error 仍用 `quota`
skill 查 live 狀態；CodexBar 不涵蓋 Grok 時，不猜 Grok 剩餘額度。

## 路由規則

- **重活實作**（bulk edits、多檔改動、長時間跑）→ Codex worker。會改檔的委派走 tmux 裡可觀察、可中斷的互動式 Codex session，不用 headless process。
- **bounded read-only 工作** → controller 是 Codex、且可共用 parent trust/permission boundary 時優先用 native subagent；controller 是 Claude Code，或工作需要 workspace-only read、disabled shell network、乾淨 CLI process / structured output 時，走 shared `headless-agents` 的 hardened Codex wrapper。
- **Claude Code**保留 product judgment、Claude-specific 行為驗證，以及 cross-provider review；不要用較低 quota 承擔可由 Codex 完成的機械型長迴圈。
- **Grok**不是預設 bulk worker。它最有價值的角色是對 Codex 產出提供真正不同 provider 的 dissent、找盲點，或在其他兩邊 quota/服務不可用時接手 bounded 工作。
- **guardrail / SSOT repo review**：先用 fresh Codex reviewer 做 safety + simplify review；若 diff 由 Codex 撰寫且風險不低，再加 Claude 或 Grok 的 cross-provider pass。若輔助 provider 不可用，至少用 blinded fresh Codex prompt，不能讓作者自己充當唯一 reviewer。
- **fallback 順序**：Codex 撞牆 → 依任務形狀選 Claude Code 或 Grok → 都撞牆才等 reset。user 指定 provider 或 model 時，以 user 指令優先，不擅自替換。
