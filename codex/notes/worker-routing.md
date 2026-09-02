# Worker 路由 SSOT

哪個 provider 當重活 worker、哪個當 reviewer，由本檔決定；worker surface 的授權門檻則以 `codex/AGENTS.md` 為準。**換 provider 角色時只改本檔的「目前角色分工」區；訂閱等級與 quota 記在本機 `~/.config/machine.md`**；其他 prompt（orchestrator persona、arbitrage、guardrail 閘門等）只引用本檔，不得各自寫死 provider 優先序。

## 目前角色分工（更新於 2026-09-02）

- **Claude Code＝實作主力**：重活實作、改檔委派預設走這裡。
- **Codex＝review 與 read-only 研究的共同承擔者**：不再是「省著用」。
- **Grok＝Codex app 側的備援 worker**：有獨立訂閱 quota，Codex 額度見底時可從 Codex app 用 Router 的 grok agent 分擔；Claude Code 沒有 Grok subagent，本檔不把它排進 CC 的委派順序。
- 即時訂閱等級、quota 與帳號狀態一律記在本機 `~/.config/machine.md`（不進 git）；要看餘量跑 `codexbar usage --provider both --source cli`（見 `quota` skill）。

## Surface 規則

- 委派預設使用目前 runtime 內建的 subagent。這通常比另開 CLI process、pane 或 session 更省資源，也能沿用 runtime 的權限與 lifecycle 管理。
- 不要只為了遵守 provider 優先序而另開外部 CLI；目前 runtime 沒有該 provider 的內建 subagent 時，先衡量是否由目前 agent 完成，或用 bounded、read-only headless reviewer 取得第二意見。
- tmux 是 human opt-in surface，授權門檻以 `codex/AGENTS.md` 為準；本檔只決定 provider，不提供 tmux 授權。
- 禁止 file-mutating headless CLI worker；需要改檔時使用內建 subagent 或目前 agent。human 已明確授權 tmux 時，才依 `tmux-orchestration` 的權限、觀察與 cleanup 合約執行。

## 路由規則（用「實作主力／review 共同承擔」角色寫，換 provider 時規則不動）

- **重活實作**（bulk edits、多檔改動、長時間跑）→ 目前 runtime 內建、能安全改檔的 subagent；若 runtime 能選 provider，選實作主力。主 agent 保留 scope、判斷、驗收與 git ownership。
- **review、read-only 研究、第二意見**預設可交給 Codex（bounded、read-only）；重活實作與改檔仍走 Claude Code 內建 subagent。不要為了切 provider 而提高 surface 成本。
- **guardrail / SSOT repo 的 reviewer**：預設 fresh subagent（含 safety 與 simplify 視角）；確實需要跨 provider 的第二意見時，Codex 的 bounded、read-only reviewer 可直接接手。
- **fallback 順序**：內建 subagent 撞牆 → 目前 agent 可安全收尾就自行完成 → review／研究可轉另一個 provider 的 bounded read-only reviewer；兩邊都撞牆才等 quota reset。即時餘量不要背數字，跑 `codexbar usage --provider both --source cli` 查（細節見 `quota` skill）。
