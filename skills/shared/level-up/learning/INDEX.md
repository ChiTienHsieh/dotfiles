# level-up Learning Index

這是 `level-up` 的長期學習索引。每次使用 skill 前先讀這裡，再讀相關 `topics/*.md`；每個 level 結束後，只記錄有證據的理解、誤解修正、或使用者自述已會的先備知識。

| Topic | Status | Evidence | Updated | File |
| --- | --- | --- | --- | --- |
| 投資配置：39w 全球股容器 | learning | A2 舊楓之谷 7 關；L1–L2 完成（XP 3/7，L2 MCQ 對）。**Fable 決策已寫在 topic 檔（VWRA 主推＋決策樹），Opus 接手帶 user 逐關重走決策點；數字全部先查證再講。** | 2026-07-06 | topics/invest-global-allocation.md |
| Dedup 設計會議準備（討論） | learning | B3 公會幹部會議續作；scope=schema+演算法+data-driven；Level 0 完成、優先序提案待確認。 | 2026-07-05 | topics/dedup-meeting-prep.md |
| gu-log editorial presentation preflight | mastered | C3 米其林餐廳框架，L1–L6 MCQ 6/6 全對；三 open questions 全拍板（sans-first／標題下小卡／全進抽屜＋TOC 細線）。品味規則：卡片質感>裸文字、UI 不用 emoji 用 SVG icon、小字要配緊行高。 | 2026-07-05 | topics/gu-log-editorial-presentation.md |
| Implementation loop / debrief mode | mastered | 航空框架 debrief 5/5 全對＋preflight 盲測 2/2（四象限、風險觸發）；七項決策確認與 shipped 全吻合，重量分配由 preflight 顯式化。**報告要拆 level，不可一次倒完。** | 2026-07-05 | topics/implementation-understanding-loop.md |
| html-artifacts vs html-explainer 分工 | mastered | A2 楓之谷商店街類比，3/3 MCQ 全對：work artifact vs 教學配方、description 路由、品名搶字眼病灶。自述已熟 agent skills 觸發機制。 | 2026-07-04 | topics/html-duo.md |
| 裝修優先序與溝通 | learning | A3 Vainglory shotcaller；浴室/防蟑螂/臥室睡眠為一期核心，預算約 50 萬評估。通風=浴室排濕、臥室可控通風、全熱研究。若爆預算先砍全熱/封陽台/客廳大窗/全屋冷氣。 | 2026-07-04 | topics/renovation-prioritization.md |
| Transcript 研究決策關 | mastered | A2 Vainglory shotcaller；決策走廊（分支/arbitrage/marker/helpers/新skill/出兵）。L1-L6 全通收關，成果：gu-log PR #541、arbitrage 門檻、helper 三件裝。 | 2026-07-04 | topics/transcript-study-decisions.md |
| gu-log 大掃除回放 | learning | A1 Vainglory 深夜排位場；追劇+實戰 BOSS 關（#538 merge 等）；depth 3。剛開課。 | 2026-07-03 | topics/gu-log-cleanup-replay.md |
| Dotfiles 10x 審計回放 | learning | A3 楓之谷倉庫大掃除；純娛樂追劇補進度；結尾接實戰決策關（4 ask_user + html* 融合 + merge main）。剛開課。 | 2026-07-03 | topics/dotfiles-10x-audit.md |
| LLM 應用核心能力 | familiar | 自述已熟 agent/context window/三種 API/Python 基本/基礎 SQL，及「不信單一 agent」前提；教學跳過。**Gap: 不熟 message broker/Kafka/RabbitMQ/Celery，別當類比。** | 2026-07-01 | topics/llm-app-foundations.md |
| AgentFlow 專案商業邏輯 | learning | 剛開課；MAP「路標非證據」已能複述(familiar)；pipeline/角色/腳本仍待教。 | 2026-06-17 | topics/agentflow-repo.md |
| Dedup Schema Design | mastered | Vainglory 好友/公會類比。L1–L9 mastered（關聯表→狀態機→索引），常自推正解升級版。交付物關改由 Codex 艦隊直接完成（v1 schema 已進 SSOT）。 | 2026-07-04 | topics/dedup-schema.md |
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
