# Dedup 設計會議準備（討論 session：schema + 演算法攻防）

## Learner Goal
- 準備跟 GuangFuHero 團隊開會對線 dedup 設計。四大目標全要 ＋ 第五目標（演算法立場成形，因演算法半邊還沒定案）。
- 優先序（提案待 user 確認）：①盲點掃描 → ②演算法立場成形 → ③red-team 拷問 → ④底線清單 → ⑤說服答辯劇本。
- 範圍 = 資料庫設計 + 「怎麼判斷 2+ tickets 是否重複」的演算法（含 data-driven solution 要不要採用）。
- 命名對齊本身是討論點：會議筆記用舊名（dedup_audit、tickets_relations），SSOT §九已收斂成 ticket_dedup_audit_events / ticket_duplicate_pairs。

## 會議筆記素材（user 提供，raw agenda）
- 後台可改規則(規則放DB)、高樓樓層比對、data-driven 演算法(測試案例迭代)、AI 額度/API key、Phase 1 門檻(100m/15min/30m/T1–T3 靠現場資料校正別釘死)、200ms 可調+空間索引、confidence_score 不混用、merge audit v1 深度、tickets_relations(可能不需要)/dedup_audit(需要,查 audit_log ER-diagram alembic)/audit_log jsonb、embedding vector search(what columns/models?)、pg_trgm 中文支援疑慮、hybrid RAG(vector+BM25+rerank)、SiliconFlow free tier、test-cases 能分好/能併好、ticket graphQL 包三四個 table。

## Status
- learning。Analogy: B）公會幹部會議（Vainglory 好友/公會世界觀續作，沿用 dedup-schema 對映；新增：幹部會議=團隊會議、公會規章=v1 schema、scrim=red-team、談判底線=讓/守清單、出征=正式提案）。深度 3。

## 剩餘關卡地圖（動態增減）
- Act I 內務審查：7 張表逐一確認、Q1–Q6 立場、命名歧異（ticket_low_id vs *_uuid；舊名 vs SSOT 新名）。
- Act II 演算法軍議：Phase 1 門檻與現場校正、空間索引/200ms、樓層比對、慢層技術選型（embedding columns/models、pg_trgm 中文、hybrid RAG、SiliconFlow free tier）、data-driven test-case 迭代法。
- Act III 模擬戰：red-team 拷問 per 主題。
- Act IV 出征準備：底線清單、會議 agenda、說服劇本。

## 已掌握（概念）
- ticket_duplicate_pairs 狀態分工：status=現在位置、layer1_outcome=歷史事實。
- denormalization / YAGNI 直覺天生就有：能自己把概念對映到 SSOT（"not following SSOT"），有遷移能力。
- 狀態機圖 = status 欄位的使用說明書（格子=合法值、箭頭=合法 UPDATE、沒畫的=不該寫的 UPDATE）；懂 text+CHECK vs PG ENUM 取捨。
- EAV（ticket_dedup_attributes）：衍生特徵另開表、加新種類不動 tickets 結構。
- audit_logs（記「改了什麼」）vs dedup 稽核表（記「為什麼決策」）：自丟 what-if「兩張表合併會怎樣」並自答「會污染既有 audit_logs」→ 自推「另開新表較好」。監視器 vs 會議記錄類比有效。
- 政策三表（dedup_settings / rule_versions / ai_configs）：規則版本疊加不覆蓋＝歷史判定可解釋。
- 委派判斷：判斷在前、苦工在後且量大 → 委派；判斷跟苦工纏一起或只剩兩刀 → 自己動手。

## 已拍板的決策（會議素材，steers future）
- **Q2 立場**（已寫回 SSOT §七）：單後端 + PG VM 不用為百萬人設計 → v1 走 join、先推 POC、瓶頸出現再重構。
- **rejected pair 永久黏**（立場 1）：worker 查詢層排除；理由=錯誤不對稱哲學延伸（錯合併 >> 漏合併）。
- **Layer 1/2 命名廢除 → 快層/慢層**：schema 全改（'fast'/'slow'、hint_outcome、rescan_needed、fast_*/slow_*、hint_accepted、pause_slow）。
- **Carol 會議 ground truth 推翻文件**：鄰居撞單送出者也收完整選項（開單者常是志工、樂意參與；所有單公開，個資疑慮是假議題）。AskUserQuestion 拍板：選項一視同仁、admin 照舊收通知。
- **double-submit 答辯定稿**：前端 disable/debounce 只擋「手滑」；擋不住的（回應丟失+重送、跨裝置、NGO 批次匯入）本來就是慢層存在理由；反手建議 backend 加 idempotency key（submission_uuid + UNIQUE）。故事要挑「前端擋不住」的機制才立於不敗。

## 未定案 / 待團隊決
- **undo（confirmed 反悔）是紅線要求，但 SSOT 沒定 undo 後卡回哪狀態**（suggested 重審 or rejected？）→ 候選 Q8。
- **merge 語意細究**（Task #8）：數量語意（2+2 箱=4 or 2？）、內容互補欄位合成、取代（=merge 特例）、三張成群 canonical 選法、merge 後副件被更新 → 可能產出 Q9。
- 旋鈕（快層閘門調音台）存廢+命名留 backlog（Task #7），等 Act II 演算法討論再定，別先幫可能被砍的旋鈕打蠟。
- 演算法半邊（慢層選型、data-driven）尚無 SSOT 定案 —— 是「立場成形」不是「防守既有設計」。

## 詞彙 / 品味（硬規則）
- **廢詞（絕不再用）**：「安心話」（user: sounds like cn, wtf）；「個資疑慮」當去重擋箭牌（Carol 證偽）；「過堂」（看不懂）→ 改「逐一確認」。
- **user 對「AI 生的代號」零容忍**（Layer 1/2、情境 A/B/C、T1–T3、branch_a 全中槍）→ 新名詞一律用人話。
- 課文品味：sonnet 版太無聊 → fable 接手；課文必須場景先行、角色開口說話、劇情載知識，不是「說明文＋類比裝飾」。光復在地假資料敘事對 user 有效。
- mock data 合理性原則：每齣戲的機制必須對得上快層/慢層規則，不能只是好笑（user 高品質 design smell：不合理的 user story 會害團隊為爛情況設計資料結構）。

## 工程教訓
- sed 全域替換會吃掉「記錄舊名的命名決定」本身（自我指涉事故）；改 SSOT 命名紀錄要用舊名原文寫、避開替換 pattern。
- **UI 驗收 SOP**：改 dedup-system-design 站一律測三組寬度 3840 全寬 / 2133（90% 半寬）/ 1920（100% 半寬），全部 pageHScroll=0、表格框內捲。曾踩 grid 子元素 min-width:auto 被寬表撐爆 → `.flow>*{min-width:0}`（4K 全寬時 bug 不可見，易誤判正常）。

## 欠帳（下一批文件同步）
- dedup-brief 站（11 處 Layer 舊詞）、dedup-test-cases.md（1 處安心話）、**index.html DTC-001「送出者只收安心話」與 Carol 改版矛盾**、dedup-eav-columns.md / dedup-admin-onboarding.md（Layer 舊詞）、獨立 dedup-state-machine.html（Layer 舊詞 24 處）尚未換新詞彙；vercel 推送等 user 驗收後一次推。

## Teaching Notes
- **重要糾正**：schema 交付物是 vibe coded（Codex 艦隊產的），user 正在還認知債 → 逐一確認＝他在學自己的 schema，不是複習。每關只講一個東西、細節現場攤開不能只丟代號、/chill 模式已啟用（PTT 說故事、一關一口）。
- 先備：dedup-schema topic 概念全 mastered，不重教，直接站在上面討論。
- 續用 Vainglory 公會世界觀，不混楓之谷；輕鬆、九成劇情一成技術錨點。
- 討論 session：唯讀為主，不動 repo 檔案（除 learning 紀錄）。
- SSOT: `.local/dedup-design.md`（§七/§八/§九）；未決 Q 清單: `.local/tasks/report-converge.md`。

## Next Suggested Levels
- 優先序拍板（決策確認）→ Act I 第一張表逐一確認。
