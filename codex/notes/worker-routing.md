# Worker 路由 SSOT

哪個 provider 當重活 worker、哪個當 reviewer，由本檔決定；worker surface 的授權門檻則以 `codex/AGENTS.md` 為準。**換 provider 角色時只改本檔的「目前角色分工」區；訂閱等級與 quota 記在本機 `~/.local/share/machine/machine.md`**；其他 prompt（orchestrator persona、arbitrage、guardrail 閘門等）只引用本檔，不得各自寫死 provider 優先序。

## 目前角色分工（更新於 2026-09-03）

- **沒有固定的實作主力。** 每個 provider 都是訂閱制、quota 週期性重置，沒用掉就浪費：派重活前先跑 `codexbar usage --provider both --source cli` 看餘量，**誰剩得多就派給誰，尤其是快 reset 還沒用完的那家**。
- **Claude Code**：內建 subagent 可改檔，是 file-mutating 委派的預設 surface；套 sandbox profile 的 headless CLI worker（Codex `-p cc-worker`、Grok `--sandbox cc-worker`、nested `claude -p`）是餘量不夠時的替代選項，怎麼安全呼叫見 `headless-cli-agents` skill。
- **Claude Code subagent 預設跑 Sonnet**（`claude/settings.json` 的 `CLAUDE_CODE_SUBAGENT_MODEL`）：省錢。只有任務明確需要更強推理（棘手 debug、架構取捨、guardrail 的最終 reviewer）才在 Agent 呼叫時指定更大的 model，並在回報裡說明為什麼。
- **Codex**：任何 agent 都能用，不限 Codex app。從 Claude Code 或 Grok 派實作走 `headless-cli-agents` 的 `runbook/codex.md`（`codex exec -p cc-worker`，不用 Claude Code 的 codex plugin：三跳、憑證 deny 未驗證，status/cancel 用 `--json` + `kill` 就能做）；review、read-only 研究、第二意見用 `codex exec --sandbox read-only`（條件見 `headless-cli-agents` skill）；Codex app 直接派也行。
- **Grok**：SuperGrok 獨立 quota，`grok -p` + `--sandbox cc-worker` 已驗證能改檔且擋 `.env`（2026-09-03）；`codexbar` 查不到它的餘量，派之前只能憑 grok 自己的回報。Claude Code 沒有 Grok subagent。
- 訂閱等級、quota 與帳號狀態記在本機 `~/.local/share/machine/machine.md`（不進 git）。

## Surface 規則

- 委派預設使用目前 runtime 內建的 subagent。這通常比另開 CLI process、pane 或 session 更省資源，也能沿用 runtime 的權限與 lifecycle 管理。
- 不要只為了遵守 provider 優先序而另開外部 CLI；目前 runtime 沒有該 provider 的內建 subagent 時，先衡量是否由目前 agent 完成，或用 bounded、read-only headless reviewer 取得第二意見。
- tmux 是 human opt-in surface，授權門檻以 `codex/AGENTS.md` 為準；本檔只決定 provider，不提供 tmux 授權。
- 寫檔的 headless CLI worker 條件與呼叫方式依 `headless-cli-agents` skill；bypass flags 一律禁止。

## 路由規則（用角色寫，換 provider 時規則不動）

- **重活實作**（bulk edits、多檔改動、長時間跑）→ 目前 runtime 內建、能安全改檔的 subagent，或套 sandbox profile 的 headless CLI worker；選餘量最多的那家，headless 是選項不是義務（Codex 週配額常先用完，回到 Claude 內建 subagent 很正常）。主 agent 保留 scope、判斷、驗收與 git ownership；驗收與 acceptance rules 依 `headless-cli-agents` skill。
- **review、read-only 研究、第二意見**預設可交給 Codex（bounded、read-only）。不要為了切 provider 而提高 surface 成本。
- **guardrail / prompt / SSOT 類的 reviewer**：一律 fresh Claude subagent、指定最強的 Claude model（含 safety 與 simplify 視角）。重點是 fresh（作者帶著改動脈絡，最看不見 stale 旗標與前後矛盾），不是換 provider：Codex（GPT-5.6 Sol）當 guardrail reviewer 偏過度防禦、愛加冗餘脈絡，不派；它的 bounded read-only reviewer 留給需要對手視角的 code review。
- **fallback 順序**：內建 subagent 撞牆 → 目前 agent 可安全收尾就自行完成 → review／研究可轉另一個 provider 的 bounded read-only reviewer；兩邊都撞牆才等 quota reset。即時餘量不要背數字，跑 `codexbar usage --provider both --source cli` 查（細節見 `quota` skill）。

## Reviewer 授權

- 使用者持續授權其他 agent（含已設定的外部 AI reviewer）做 review，不必逐次詢問。
- 送出 diff、prompt 或檔案前先檢查實際待傳資料有沒有 secret、憑證、private key 或未公開個資；發現敏感內容、無法判斷，或目的地與範圍超出既有 reviewer workflow 時才停下確認。
- 這項授權只涵蓋 review：不授權 reviewer 寫檔、執行外部 mutation，或繞過其他工具與權限邊界。
- guardrail / SSOT 改動的 reviewer 同時做 safety 與 simplify review。simplify 看三件事：只針對單次事故的過窄規則、過度工程化、能不能換成更通用的說法；逐項回報 Keep / Simplify / Drop。
