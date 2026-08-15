# Worker 路由 SSOT

哪個 provider 當重活 worker、哪個當 reviewer，由本檔決定；worker surface 的授權門檻則以 `codex/AGENTS.md` 為準。**換訂閱等級時只改本檔的「目前訂閱狀態」區**；其他 prompt（orchestrator persona、arbitrage、guardrail 閘門等）只引用本檔，不得各自寫死 provider 優先序。

## 目前訂閱狀態（更新於 2026-07-05）

- **Claude Code＝主力**：訂閱充足，重活與 review 預設走這裡。
- **Codex＝省著用**：20 USD tier，5 小時窗小、weekly 上限低，quota 珍貴。

## Surface 規則

- 委派預設使用目前 runtime 內建的 subagent。這通常比另開 CLI process、pane 或 session 更省資源，也能沿用 runtime 的權限與 lifecycle 管理。
- 不要只為了遵守 provider 優先序而另開外部 CLI；目前 runtime 沒有該 provider 的內建 subagent 時，先衡量是否由目前 agent 完成，或用 bounded、read-only headless reviewer 取得第二意見。
- tmux 是 human opt-in surface，授權門檻以 `codex/AGENTS.md` 為準；本檔只決定 provider，不提供 tmux 授權。
- 禁止 file-mutating headless CLI worker；需要改檔時使用內建 subagent 或目前 agent。human 已明確授權 tmux 時，才依 `tmux-orchestration` 的權限、觀察與 cleanup 合約執行。

## 路由規則（用「主力／省著用」角色寫，換訂閱時規則不動）

- **重活實作**（bulk edits、多檔改動、長時間跑）→ 目前 runtime 內建、能安全改檔的 subagent；若 runtime 能選 provider，選主力。主 agent 保留 scope、判斷、驗收與 git ownership。
- **省著用的一邊**只在三種情況出場：輕量 review、read-only 研究，或 human 明講指定。不要為了切 provider 而提高 surface 成本。
- **guardrail / SSOT repo 的 reviewer**：預設 fresh subagent（含 safety 與 simplify 視角）；確實需要跨 provider 的第二意見時，選主力的 bounded、read-only reviewer。省著用那邊只有 quota 有餘裕且 diff 小才接。
- **fallback 順序**：內建 subagent 撞牆 → 目前 agent 可安全收尾就自行完成 → 輕量 review／研究可暫轉另一邊的 bounded read-only reviewer；兩邊都撞牆才等 quota reset。即時餘量不要背數字，跑 `codexbar usage --provider both --source cli` 查（細節見 `quota` skill）。
