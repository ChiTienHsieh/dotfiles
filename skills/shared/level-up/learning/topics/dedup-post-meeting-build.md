# Dedup 會後施工 preflight（合約＋schema 出貨）

## Learner Goal
- 7 月底交出「前端能開工的合約＋schema」＝贏；8/20 demo 次要。慢層選型外包給 agent 平行跑（免費可擴充路線已研究完：Python BM25＋jieba 起步、pg_trgm 輔助、pgvector＋免費 embedding 額度升級）。

## Current Level
- Status: mastered（六關全通，決策全拍板並出貨至 repo）
- Last updated: 2026-07-13
- Confidence: high

## Evidence
- 2026-07-13: L1 資料形狀選 C（配對留審計、群組另存為連線結果）—— 且自己主動推進到遞移性：「a merge b、b merge c，a c 自然是同一張 ticket，群＝一張 ticket 由各張細節組成」。merge 語意的心智模型正確且超前。
- 2026-07-13: 自己立了「merge＝內容整理責任（地址只能有一個）」原則，正確推翻教學者的漿糊單前提設定 —— 並看出它就是焊接事故的主防線。
- 2026-07-13: L4 對 A/B 案的取捨猶豫本身正確（合約 vs UI 兩層混在一起）；接受「合約照超集合凍、行為先保守」的拆法。L5 自己加碼「成分燈號」UI（各成分過線與否），把門檻制的可質疑性搬進權重世界。L6 自己補「手動全掃＋排程全掃」旋鈕。
- 決策拍板：L1 兩層並用／L2 遞移＋群併群旗標／L3 拆群＝原單復活／L4 合約 B 形顯示先 A／L5 權重拆帳＋燈號／L6 增量掃＋版本觸發全掃＋手動＋排程。出貨：`cth-note/dedup-workspace/tasks/report-preflight-build.md`。

## Known Gaps
- （無 —— 遞移性放大風險已透過「merge＝內容整理」原則自行化解）

## Teaching Notes
- 「合帳」自創中文詞被打槍（2026-07-13）：不存在的台灣用語。內容調和直接說「merge 時把兩張單的內容整理成一張」；merge 一詞本身 OK。呼應既有「廢詞/AI 代號零容忍」。
- 本課程 = shotcall MCQ 格式首航 dogfood（當時暫名「實戰課程」，後定名 shotcall）：每關一段概念故事＋一題決策 MCQ（選項全合理＋一個北七），user 的選擇＝決策定案，CC 標推薦。
- 一次只出一題（user 2026-07-13 明確否決多題批次）；回合要短。
- 外殼：preflight 航空框架輕量用；概念類比走 Vainglory 公會/好友（dedup-schema 已驗證 mastered）。
- 決策紀錄（拍板）：L1=C 兩層並用。

## Next Suggested Levels
- L2 遞移性（群併群要不要旗標）→ L3 拆群/undo → L4 前端合約（狀態枚舉、半夜 pending 顯示）→ L5 權重計分（冷啟動＋可解釋性）→ L6 掃描範圍 → 收尾出貨：合約＋schema 草案＋工單（fixtures 重出、200ms 拆除、DTC-001）。
