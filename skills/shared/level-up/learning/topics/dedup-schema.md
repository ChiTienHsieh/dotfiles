# Dedup Schema Design（去重資料表設計）

## Learner Goal（Sprin 在手機上自述，2026-06-27；下一輪教學以此為準）
Sprin 是 GuangFuHero（光復超人）救災平台志工，這套 level-up 不只是學概念，是要**產出實際交付物**。「七點下次的工作」4 項：
1. **想幾個 case**（基本測試集）
2. **flow diagram + ticket 狀態機**（← L8 狀態機正中這項）
3. **想需要後端幫什麼**（測試集；要開欄位就用 **EAV** 開）
4. **super admin 怎麼 onboard 這套 dedup**：後台能改 dedup 演算法 / AI api-key，最好把設定 UI 外包到外部網站，不然要跟 UI 組要欄位
- **參考來源**：`https://dedup-brief-wanguard.vercel.app/`（brief）、`https://dedup-system-design-wanguard.vercel.app/`（system design，需 refine）、以及同資料夾 `dedup-design.md`（SSOT）。
- **教學形態**：每關盡量綁一個能交付的產物（測試 case 集、狀態機/flow 圖、寫進 `dedup-design.md` 的 schema 提案、EAV 欄位清單、super admin onboarding 流程），不只是答 MCQ。
- **節奏**：放鬆、玩著學、預期 20–30 關、命名押到最後一關。語氣輕鬆、多用 Vainglory 類比。

## Current Level
- Status: mastered（概念關 L1–L9 教完；交付物關 L10+ 由 user 改為「orchestrator + Codex 艦隊」直接做完，不再教學）
- Last updated: 2026-07-04
- 交付物全數完成並 commit 進 .local repo（ae89829）：測試案例 13 案+json 假資料、EAV 欄位清單、super admin onboarding、v1 schema 提案（SSOT §九，命名定案 ticket_duplicate_pairs 家族）。
- 模式轉換：2026-07-04 user 明講「instead of teaching…finish all of the task」→ 後續此 topic 是工作模式不是教學模式，除非 user 再開課。

## 環境/協作變更（2026-07-01）
- **repo 路徑移動**：`~/Desktop/CodeForge/...` → `~/CodeForge/...`。SSOT 現在在 `~/CodeForge/learning_resources/github_repo/GuangFuHero/optimized-version/.local/dedup-design.md`。
- **User 要省 Mac RAM**：不要再開 Codex tmux pane，改用 CC subagent（同 process）或 orchestrator 自己做。%81/%82 已關（`claude -r` 可 resume）。
- **交付物累積**：狀態機圖 `.local/dedup-state-machine.html`（含 dup_ignored）、決策表已上 brief（§七鏡像）、索引清單已寫 dedup-design.md §八。

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
- 2026-06-27: L1 答對（正解 C，junction table）。主動把它類比成「ticket 之間的 mapping」，並舉公司 Oracle `MPG_USER_ROLE` 為關聯表實例 → 已內化「關係本身是一筆資料、屬於 pair 而非單方」。對 Postgres 命名有直覺（dedup_<x>）。
- 2026-06-27: 中途主動問 foreign key，並自帶假設「不設 FK 是為了避免資料被誤刪」。已給不破梗版更正（FK 本身不刪、ON DELETE 才決定；不設 FK 真正理由是跨服務/效能/彈性），標記 L6 主講。→ 訊號：對 FK/刪除語意有興趣，L6 可講深一點、可考慮提前。
- 2026-06-27: L2（self-referential M:N）答對（正解 B：兩外鍵都指回 tickets 合法）。
- 2026-06-27: L3（canonical ordering + UNIQUE）答對（正解 B），且自行推理出 A 多一次 read、B 較有效率 → 已內化 dedup 表防 (A,B)/(B,A) 重複的標準做法。順帶帶過 FK 基礎（不破 L6 梗）與三個命名候選（ticket_similarities / ticket_duplicate_pairs / dedup_candidates），但依 User 要求命名延到最後一關定。
- 2026-06-27: 讀過 brief（dedup-brief-wanguard.vercel.app）。重點：去重只建議不自動合併（錯合併會讓真實受災戶消失）；兩種重複型態（鄰居撞單／同人重開）；一張 ticket 可含多 task，先做 ticket 還是 task 未定；規則存 DB 可動態改；similarity ≠ confidence；兩階段（同步快層 + 非同步背景層）；空間索引、200ms 查詢上限；垂直大樓樓層比對。
- 2026-06-27: User 主動問「要不要對 task 去重」→ 正中 brief 的 ticket/task 顆粒度議題，已決定當 L4（新插關）。
- 2026-06-27: L4（ticket vs task 去重顆粒度）答對（正解 B：兩層各需邏輯 → 兩張各自的 self-referential 關聯表）。接著主動問「ticket 會不會跟 task 撞」，舉「爸爸 vs 小 Tom 各自申請泰迪熊」例。已澄清：去重邊永遠同層級（不會 ticket↔task 直接比），他的例子其實是 task↔task 跨 ticket；並用同戶/鄰居兩情況帶出 similarity ≠ confidence、只建議不自動合併。訊號：對跨層級/邊界案例很敏銳。
- 2026-06-27: L5（關係列的 payload）答對方向（B/C，正確排除 A）。已講清 B vs C 分水嶺＝每對「一份 vs 一串」：similarity/status/method/created_at 用 B（放列上），audit/歷程用 C（一對多另開表）。v1 主體＝B。
- 2026-06-27: L6（FK ON DELETE）答對（A=CASCADE），理由精準：「配對情報的意義寄生在兩端都還活著」。已補實務 nuance：災防系統多用 soft delete（呼應 brief 不讓受災戶消失），CASCADE 只在 hard delete 當清道夫；audit/歷程表反而不該 CASCADE（稽核要留得住）。
- 2026-06-27: L7（相似度傳遞性 / pair→group）。Sprin 覺得難、三個都覺得有理、主動求解 → 此關非自行推出，是引導講解。正解 B：相似不傳遞，merge drift 會讓真實受災戶被連鎖併走（brief 紅線）；A 陷阱=連鎖合併；C 精神對(別漏 A-C)但做法錯(不可憑空建邊，應丟佇列實算)。核心觀念：相似邊(自動/兩兩/寬鬆) vs 成群合併(刻意/人工/嚴門檻 / connected component)是兩個分開階段。
- 2026-06-27: L7 正解（B）首次送出時遺失，只送到 bookkeeping 行 → User wtf。已重貼乾淨版，理解確認。
- 2026-06-28: 開 L8（狀態機）。用 Vainglory 好友邀請流程類比（陌生人→邀請中→好友/拒絕；推薦好友=機器建議不會自動成立）。狀態：建議(機器發)/確認(人工)/駁回(人工)。MCQ 正解 B：機器只生建議、只有人能推確認/駁回、確認要可反悔（呼應 brief 紅線）。
- 2026-06-28: L8 答對 B。之後自己延伸到「每條 transition 的觸發條件+後果」，用四格表推出 Layer 1「聽勸=靜默 / 不聽勸=建單+dup_ignored」模式 → 揭露 dup_ignored 這個新終結狀態。狀態機圖已補 dup_ignored 分支。決策表寫進 dedup-design.md §七、%81 render 進 brief。訊號：對狀態機的邊/副作用很敏銳，會自己把圖補完整。
- 2026-07-01: L9（查詢決定索引）答對 B。原本以為 index 是「只裝符合條件列的小表」→ 已修正（一般 index 收整欄排序+指標），但順勢帶出他其實描述的是 partial index（真東西），並肯定他自推的「寫入變慢」取捨。自己推出最左前綴缺口要補 high 欄索引。產出索引清單交付物（dedup-design.md §八）。

## Known Gaps
- (待觀察)

## Teaching Notes
- 用 Vainglory 好友/公會類比，不混楓之谷
- User 是 top 0.1%，進階機制可直接用、不必從新手村解釋
- 專有名詞（英雄名、技能）要查證或用 user 給的例子，不可亂掰
- 2026-06-28 User 回饋：語氣別太嚴肅、Vainglory 類比要再多。每關盡量綁一個遊戲場景（好友邀請=狀態機、公會=群組、推薦好友=機器建議），口吻輕鬆一點。
- 聊天只送課程內容本身：不要在訊息裡報告「已記進 learning 檔」之類的 bookkeeping，記錄要靜默做。曾因附上系統筆記讓 User wtf。

## Next Suggested Levels
- L1: 好友名單 = junction table
