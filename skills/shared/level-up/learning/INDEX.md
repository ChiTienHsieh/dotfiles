# level-up Learning Index

這是 `level-up` 的長期學習索引。每次使用 skill 前先讀這裡，再讀相關 `topics/*.md`；每個 level 結束後，只記錄有證據的理解、誤解修正、或使用者自述已會的先備知識。

| Topic | Status | Evidence | Updated | File |
| --- | --- | --- | --- | --- |
| html-artifacts vs html-explainer 分工 | mastered | A2 楓之谷商店街類比，3/3 MCQ 全對：work artifact vs 教學配方、description 路由、品名搶字眼病灶。自述已熟 agent skills 觸發機制。 | 2026-07-04 | topics/html-duo.md |
| Transcript 研究決策關 | learning | A2 Vainglory shotcaller；決策走廊（分支/arbitrage/marker/helpers/新skill/出兵）。剛開課。 | 2026-07-03 | topics/transcript-study-decisions.md |
| gu-log 大掃除回放 | learning | A1 Vainglory 深夜排位場；追劇+實戰 BOSS 關（#538 merge 等）；depth 3。剛開課。 | 2026-07-03 | topics/gu-log-cleanup-replay.md |
| Dotfiles 10x 審計回放 | learning | A3 楓之谷倉庫大掃除；純娛樂追劇補進度；結尾接實戰決策關（4 ask_user + html* 融合 + merge main）。剛開課。 | 2026-07-03 | topics/dotfiles-10x-audit.md |
| LLM 應用核心能力 | familiar | 自述已熟 agent/context window/三種 API/Python 基本/基礎 SQL，及「不信單一 agent」前提；教學跳過。**Gap: 不熟 message broker/Kafka/RabbitMQ/Celery，別當類比。** | 2026-07-01 | topics/llm-app-foundations.md |
| AgentFlow 專案商業邏輯 | learning | 剛開課；MAP「路標非證據」已能複述(familiar)；pipeline/角色/腳本仍待教。 | 2026-06-17 | topics/agentflow-repo.md |
| Dedup Schema Design | learning | 用 Vainglory 好友/公會類比。已答對 per-row vs per-pair 顆粒度。L1 進行中。 | 2026-06-23 | topics/dedup-schema.md |
| Vercel 部署 | familiar→mastered | 楓之谷存檔+公告欄類比(A2)。4/4 MCQ 全對，主動用 ground truth 糾正教學者假設。懂 immutable/alias/promote/rollback。 | 2026-06-25 | topics/vercel-deploy.md |
| Codex log churn / SSD endurance (#28224) | mastered | 罐頭工廠生產線類比(A3)。7/7 MCQ 全對。目標=練 GitHub issue/PR 求職。自己查真實 fork diff、抓出缺 opt-in 逃生門。 | 2026-06-26 | topics/codex-log-churn.md |
| tmux | mastered | 舊楓之谷城鎮類比。L2-L6 全通：pane/window/session、持續性(detach/attach)、多 session(ls/attach -t/nested)、% 切 pane、pane 移動/關閉。全靠推理、抓出教學者 2 個流程錯。剩實機練。 | 2026-06-27 | topics/tmux.md |

## Status Labels

- `mastered`: 使用者已能在情境中正確應用。
- `familiar`: 使用者略懂，但未必能獨立遷移到新情境。
- `learning`: 正在學，仍需要 scaffolding（鷹架式引導；先給支架再逐步拿掉）。
- `gap`: 有誤解、缺先備知識、或連續卡關。
- `skip_for_now`: 這次刻意不教，之後再回來。

## Update Rules

- 只寫會影響下一次教學難度的資訊。
- 不寫 secrets、客戶資料、token、private code、或整段聊天紀錄。
- `Evidence` 必須能說明為什麼下一位 AI 可以合理調整難度。
