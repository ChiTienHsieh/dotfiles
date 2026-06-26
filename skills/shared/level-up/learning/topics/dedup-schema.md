# Dedup Schema Design（去重資料表設計）

## Current Level
- Status: learning
- Last updated: 2026-06-23
- Confidence: L0 complete, L1 in progress

## Analogy & Depth (Level 0 選擇)
- **Analogy**: Vainglory 好友名單 & 公會系統。好友名單 = 關聯表、公會 = 群組、都是永久存檔。
- **Depth**: 紮實打底 — 走完 L1~L10，能自己定出 v1 提案、知道每個選擇的 trade-off。
- **User context**: Vainglorious Silver (top 0.1%)，好友/公會機制超熟，進階概念可直接用。

## Level Map (10 關)
1. L1: 關係自己就是一筆資料 —— 好友名單的誕生（junction table）
2. L2: 自我關聯 (self-referential M:N)：兩欄都指向同一張 tickets 表
3. L3: pair vs group：好友配對 vs 公會
4. L4: canonical ordering + UNIQUE 約束
5. L5: 關係上的 payload（similarity、偵測方法、狀態、時間）
6. L6: FK 與 ON DELETE
7. L7: 從 pair 長成 group（connected component）
8. L8: 關係的狀態機（建議 → 確認/駁回）
9. L9: 查詢決定索引
10. L10: 收斂回現有 schema，定出 v1 提案

## Evidence
- 2026-06-23: Level 0 完成。User 主動問「Vainglory 也有好友公會」，選 D2。
- 2026-06-23: 前一 session 已答對「per-row vs per-pair 顆粒度」MCQ（正解 B）。

## Known Gaps
- (待觀察)

## Teaching Notes
- 用 Vainglory 好友/公會類比，不混楓之谷
- User 是 top 0.1%，進階機制可直接用、不必從新手村解釋
- 專有名詞（英雄名、技能）要查證或用 user 給的例子，不可亂掰

## Next Suggested Levels
- L1: 好友名單 = junction table
