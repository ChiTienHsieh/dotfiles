# gu-log 搜尋 Ranking Preflight

## Learner Goal
- 建立一套未來可持續擴充的搜尋 ranking 規則，不只修正單次 `250` 查詢。

## Current Level
- Status: mastered
- Last updated: 2026-08-08
- Confidence: high

## Evidence
- 2026-08-08: 主動指出搜尋裸數字 `250` 時，所有同號 ticket 應先於一般文字 matches。
- 2026-08-08: 選擇 Vainglory 類比、輕鬆速成、Chat Markdown。
- 2026-08-08: 拍板 strict ticket grammar；只有完整裸數字或完整 ticket 格式觸發 structured ticket ranking，混合文字維持一般搜尋。
- 2026-08-08: 拍板 exact tier 內依 normalized `ticketId` 排序，不使用日期、collection 順序或 prefix priority。
- 2026-08-08: 拍板用純函式 invariant tests 鎖完整 ranking contract，另加 browser smoke test 驗 UI integration；不 snapshot production corpus。

## Known Gaps
- 無；preflight 決策已完成，剩 implementation 驗證。

## Decision Confirmed
- 完整裸數字與完整 ticket 格式才觸發 structured ticket ranking。
- 裸數字查詢先列出所有同號 ticket，依 normalized `ticketId` 穩定排序，再接 deduplicated Fuse results。
- 合併與 deduplication 後才套用 `maxResults`。
- 測試鎖行為 invariants，不鎖 production corpus 的完整結果 snapshot。

## Teaching Notes
- Use these examples: `250`、`GP-250`、其他欄位剛好含 `250` 的文章。
- Avoid assuming: 不把 prefix 寫死成舊 taxonomy；以結構化 ticket contract 表達。

## Next Suggested Levels
- 實作 pure ranking helper，讓 production 與 tests 共用同一個 contract。
- 完成 unit invariants、browser smoke 與 production 查詢驗證。
