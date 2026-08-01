# Worker 路由 SSOT

哪個 provider 當重活 worker、哪個當 reviewer，由本檔決定。**換訂閱等級時只改本檔的「目前訂閱狀態」區**；其他 prompt（orchestrator persona、arbitrage、guardrail 閘門等）只引用本檔，不得各自寫死 provider 優先序。

## 目前訂閱狀態（更新於 2026-07-05）

- **Claude Code＝主力**：訂閱充足，重活與 review 預設走這裡。
- **Codex＝省著用**：20 USD tier，5 小時窗小、weekly 上限低，quota 珍貴。

## 路由規則（用「主力／省著用」角色寫，換訂閱時規則不動）

- **重活實作**（bulk edits、多檔改動、長時間跑）→ 主力的 worker。主力是 Claude 時：會改檔的活走 tmux 裡的互動式 claude session（observable surface 慣例照舊，機制見 `tmux-orchestration`）；CC subagent（`Agent` 工具）留給不改檔的研究 / review。
- **省著用的一邊**只在三種情況出場：輕量 review、read-only 研究（Codex 的硬條件見 orchestrator persona）、或 user 明講指定。
- **guardrail / SSOT repo 的 reviewer**：預設主力的 fresh reviewer（fresh instance 或 subagent，含 simplify 視角）；省著用那邊只有 quota 有餘裕且 diff 小才接。
- **大型第三方 source review**：quota 允許時使用當下可用、成本合宜且能力足夠的 fresh reviewer，reasoning effort 依範圍與風險選擇。啟動前查 runtime availability 與 quota；啟動後記錄實際 model/effort。fallback 或沒有 final verdict 都必須揭露，沉默不能當 PASS。
- **fallback 順序**：主力撞牆 → 輕量活可暫轉另一邊（仍限 review / read-only）；兩邊都撞牆 → 睡到 reset。即時餘量不要背數字，跑 `codexbar usage --provider both --source cli` 查（細節見 `quota` skill）。
