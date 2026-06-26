# Codex SQLite Log Churn / SSD Endurance (issue #28224)

## Learner Goal
- 真正動機：練「怎麼在 GitHub issue/PR 表現得讓 OpenAI 有天想挖角」，把 #28224 當活教材。仿 steipete 路線（靠公開貢獻被注意，而非投履歷）。
- 因此每關都掛一條「🎯 獵頭視角」callout，把技術動作對映到「會被當噪音 vs 會被記住」。此框架本人很買單。

## Current Level
- Status: mastered（A3 深挖，7 關全破）
- Last updated: 2026-06-26
- Confidence: high

## Evidence
- 2026-06-26: 7/7 MCQ 全對（L1 SSD endurance、L2 pipeline、L3 WAL、L4 trigger vs patch、L5 upstream 兩義、L6 優雅接球、L7 PR 組裝）。
- 主動提出 batching/ring-buffer 優化並自己推理 durability 取捨（預告 L4/L5）。
- 主動問「TRACE 還能不能看？要不要做 toggle」——自己摸到「sane default + escape hatch」。
- 要求查自己真實 fork 的 diff，發現 patch 缺 sqlite 端 opt-in 逃生門（log_db_layer 寫死 default_filter()，無 EnvFilter 覆寫；對比檔案 log 那層有 try_from_default_env）。= 會自我 review 抓 design gap。

## Known Gaps
- 一開始把別人 issue 留言預設成「反駁我」，後來懂要當「遞球」（已修正）。
- 不熟 GitHub repo 政策：把「openai/codex 限制只有 collaborator 能開 PR」誤解成「我沒 CI 權限」。

## Teaching Notes
- 用這個類比：罐頭工廠生產線（pipeline 七關→品管站②是修最省的點；倉庫地板踏數上限=SSD endurance；出貨暫存檯=WAL；門口警衛=DB trigger）。一路扛得住、本人吃這套。
- 工程直覺很強、會自己跑到下一關，給他空間自己推導再收網。
- MCQ 別再把正解固定放 A/B、別讓正解最長（本人會抓包；已修進 SKILL.md）。

## Next Suggested Levels
- 實戰：把 B 方案的 PR 描述草稿寫出來，貼進 #28224 + 本機 cargo test 結果。
- 延伸主題：Rust tracing/tracing-subscriber 的 layer/filter 架構；EnvFilter vs Targets 差異。
- 延伸主題：開源貢獻者社交學（CLA、collaborator 路徑、怎麼從 issue 被請進團隊）。
