# Dedup Schema Design（去重資料表設計）

## Learner Goal（Sprin 手機自述，2026-06-27）
Sprin 是 GuangFuHero（光復超人）救災平台志工，這套 level-up 不只學概念，要**產出實際交付物**。下次工作 4 項：
1. 想幾個 case（基本測試集）
2. flow diagram + ticket 狀態機
3. 想需要後端幫什麼（測試集；要開欄位就用 EAV 開）
4. super admin 怎麼 onboard 這套 dedup：後台能改 dedup 演算法 / AI api-key，最好把設定 UI 外包到外部網站
- 參考來源：`dedup-brief-wanguard.vercel.app`（brief）、`dedup-system-design-wanguard.vercel.app`（system design）、同資料夾 `dedup-design.md`（SSOT）。

## Status
- mastered（概念關教完）。交付物關由 user 改為「orchestrator + Codex 艦隊」直接做完，不再教學。
- 交付物全數完成並 commit 進 .local repo（ae89829）：測試案例 13 案+json 假資料、EAV 欄位清單、super admin onboarding、v1 schema 提案（SSOT §九，命名定案 ticket_duplicate_pairs 家族）。
- 模式轉換（2026-07-04）：user 明講「finish all of the task」→ 此 topic 之後是工作模式不是教學模式，除非再開課。

## 環境/協作（2026-07-01）
- repo 路徑移動：`~/Desktop/CodeForge/...` → `~/CodeForge/...`。SSOT 在 `~/CodeForge/learning_resources/github_repo/GuangFuHero/optimized-version/.local/dedup-design.md`。
- 交付物累積：狀態機圖 `.local/dedup-state-machine.html`（含 dup_ignored）、決策表已上 brief（§七鏡像）、索引清單已寫 dedup-design.md §八。

## Analogy
- Vainglory 好友名單 & 公會系統：好友名單=關聯表、公會=群組、都是永久存檔。User 是 Vainglorious Silver（top 0.1%），進階機制可直接用。

## 已掌握（概念全通）
- 關係本身是一筆資料（junction table），屬於 pair 而非單方；對 Postgres 命名有直覺。
- self-referential M:N：兩外鍵都指回 tickets 合法。
- canonical ordering + UNIQUE 防 (A,B)/(B,A) 重複，自推「B 較有效率」。
- ticket vs task 去重是兩層各自的 self-referential 關聯表；去重邊永遠同層級。對跨層級/邊界案例敏銳。
- 關係列 payload 顆粒度：一對「一份」(similarity/status/method/created_at 放列上) vs 「一串」(audit/歷程另開表)。
- FK ON DELETE：CASCADE 只在 hard delete 當清道夫；災防系統多用 soft delete；audit/歷程表不該 CASCADE（稽核要留）。
- 相似不傳遞 vs 成群合併是兩個分開階段：相似邊(自動/寬鬆) → connected component(刻意/人工/嚴門檻)；merge drift 會讓真實受災戶被連鎖併走（brief 紅線）。
- 狀態機：機器只生「建議」、只有人能推「確認/駁回」、確認要可反悔。自己延伸出 dup_ignored 終結狀態（不聽勸=建單+dup_ignored）。
- 查詢決定索引：修正「index 是只裝符合條件列的小表」誤解（那是 partial index）；自推最左前綴缺口要補 high 欄索引、寫入變慢取捨。

## 讀過的 brief 重點
- 去重只建議不自動合併（錯合併會讓真實受災戶消失）；兩種重複（鄰居撞單／同人重開）；規則存 DB 可動態改；similarity ≠ confidence；兩階段（同步快層 + 非同步背景層）；空間索引、200ms 上限；垂直大樓樓層比對。

## Known Gaps
- （待觀察）

## Teaching Notes
- 用 Vainglory 好友/公會類比，不混楓之谷；top 0.1% 進階機制可直接用。
- 專有名詞（英雄名、技能）要查證或用 user 給的例子，不可亂掰。
- 語氣別太嚴肅、每關綁一個遊戲場景、口吻輕鬆。
- 聊天只送課程內容本身：不要報告「已記進 learning 檔」之類 bookkeeping，記錄靜默做（曾因此讓 user wtf）。

## Next Suggested Levels
- 概念課完結；若再開課接交付物驗收或演算法層（見 dedup-meeting-prep）。
