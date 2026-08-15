# Worker 路由 SSOT

哪個 provider 當重活 worker、哪個當 reviewer，由本檔決定。**換訂閱等級時只改本檔的「目前訂閱狀態」區**；其他 prompt（orchestrator persona、arbitrage、guardrail 閘門等）只引用本檔，不得各自寫死 provider 優先序。

## 目前訂閱狀態（更新於 2026-07-05）

- **Claude Code＝主力**：訂閱充足，重活與 review 預設走這裡。
- **Codex＝省著用**：20 USD tier，5 小時窗小、weekly 上限低，quota 珍貴。

## 路由規則（用「主力／省著用」角色寫，換訂閱時規則不動）

- **重活實作**（bulk edits、多檔改動、長時間跑）→ 主力的 current session 或 platform-native subagent，並明確限制 editable scope。外部 headless agent 只做 read-only 工作；只有使用者明確點名 `tmux-orchestration` skill 時才建立 tmux worker。
- **省著用的一邊**只在三種情況出場：輕量 review、read-only 研究（Codex 的硬條件見 orchestrator persona）、或 user 明講指定。
- **guardrail / SSOT repo 的 reviewer**：預設主力的 fresh reviewer（fresh instance 或 subagent，含 simplify 視角）；省著用那邊只有 quota 有餘裕且 diff 小才接。
- **fallback 順序**：主力撞牆 → 輕量活可暫轉另一邊（仍限 review / read-only）；兩邊都撞牆 → 睡到 reset。即時餘量不要背數字，跑 `codexbar usage --provider both --source cli` 查（細節見 `quota` skill）。
