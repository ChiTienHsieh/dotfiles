# Dedup 設計會議準備（討論 session：schema + 演算法攻防）

## Learner Goal
- 準備跟 GuangFuHero 團隊開會對線 dedup 設計。四大目標全要（user 自選 all 4）＋補了一個第五目標（演算法立場成形，因演算法半邊還沒定案）。
- 優先序（2026-07-05 提案，待 user 確認）：①盲點掃描 → ②演算法立場成形 → ③red-team 拷問 → ④底線清單 → ⑤說服答辯劇本。
- 範圍 = 資料庫設計 + 「怎麼判斷 2+ tickets 是否重複」的演算法（含 data-driven solution 要不要採用）。
- 會議筆記截圖素材（user 提供）：後台可改規則(規則放DB)、高樓樓層比對、data-driven 演算法(測試案例迭代)、AI 額度/API key、Phase 1 門檻(100m/15min/30m/T1–T3 靠現場資料校正別釘死)、200ms 可調+空間索引、confidence_score 不混用、merge audit v1 深度、tickets_relations(可能不需要)/dedup_audit(需要,查 audit_log ER-diagram alembic)/audit_log jsonb、embedding vector search(what columns/models?)、pg_trgm 中文支援疑慮、hybrid RAG(vector+BM25+rerank)、SiliconFlow free tier、test-cases 能分好/能併好、ticket graphQL 包三四個 table。
- 注意：會議筆記用舊命名（dedup_audit、tickets_relations），SSOT §九已收斂成 ticket_dedup_audit_events / ticket_duplicate_pairs —— 對齊詞彙本身就是 Act I 討論點。

## Current Level
- Status: learning（Level 0 完成，等 user 確認優先序後開 L1）
- Last updated: 2026-07-05
- Confidence: 高（user 明確選 B3）

## Analogy & Depth (Level 0 選擇)
- **Analogy: B）公會幹部會議** —— Vainglory 好友/公會世界觀續作。schema 概念對映全部沿用 dedup-schema topic（好友名單=pair table、公會=group）；本 topic 新增：幹部會議=團隊會議、公會規章=v1 schema、模擬戰(scrim)=red-team、談判底線=讓/守清單、出征=正式提案。
- **Depth: 3 深挖細節** —— Q1–Q6 立場+攻防演練+red-team 拷問+命名歧異會議劇本+「為什麼不用 Y」反向論證。
- User 要求 dynamic ~30 levels preflight check。

## Level Map（4 幕，動態增減）
- Act I 內務審查（約 L1–L8）：7 張表逐一過堂、Q1–Q6 立場、命名歧異（ticket_low_id vs *_uuid；會議筆記舊名 vs SSOT 新名）
- Act II 演算法軍議（約 L9–L18）：Phase 1 門檻與現場校正、空間索引/200ms、樓層比對、Layer 2 技術選型（embedding columns/models、pg_trgm 中文、hybrid RAG、SiliconFlow free tier）、data-driven test-case 迭代法
- Act III 模擬戰（約 L19–L24）：red-team 拷問 per 主題
- Act IV 出征準備（約 L25–L30）：底線清單、會議 agenda、說服劇本

## Evidence
- 2026-07-05: Level 0 完成。user 選 B3，主動擴 scope 到演算法層+data-driven，附會議筆記截圖，並要求協助排目標優先序（4 目標全要+問有沒有漏的目標）。

## Known Gaps
- 演算法半邊（Layer 2 選型、data-driven）尚無 SSOT 定案 —— 是「立場成形」不是「防守既有設計」。

## Teaching Notes
- 先備：dedup-schema topic L1–L9 全 mastered，概念不重教，直接站在上面討論。
- 續用 Vainglory 公會世界觀，不混楓之谷；語氣輕鬆、九成劇情一成技術錨點。
- 這是討論 session：唯讀為主，不動 repo 檔案（除 learning 紀錄）。
- SSOT: `.local/dedup-design.md`（§七/§八/§九）；未決 Q 清單: `.local/tasks/report-converge.md`。

## Next Suggested Levels
- L1: 優先序拍板（決策確認）→ Act I 第一張表過堂
