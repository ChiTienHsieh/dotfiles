# gu-log 文章頁 editorial presentation（PR #548 openspec preflight）

## Learner Goal
- Preflight 導讀 openspec change `improve-article-editorial-presentation`（PR #548），理解三個 scope（typography／首屏 metadata／底部工具收斂）與決策點，形成「同意哪些、要改哪些」結論回給 orchestrator（%29）。
- User 明講：沒有 before/after prototype 看不懂改版提案 → 教材必須帶視覺對照（live 截圖 + 互動 mock）。

## Current Level
- Status: mastered（L1–L6 MCQ 6/6 first-try；三個 open questions 全拍板）
- Last updated: 2026-07-05
- Confidence: high

## Analogy / Depth
- C3：米其林餐廳 vs 工廠食堂（新框架，user 選的），深度 3（深挖細節）。
- 對映表：正文=菜、H1=招牌、H2=菜名牌、行高=上菜節奏、TOC=牆上菜單、source card=進貨單、status banner=衛生公告、Tribunal scores=食安檢驗數據牆、pipeline 名單=廚房員工名冊、底部工具牆=結帳要過九個攤位、collapse=行政櫃檯。
- 外殼：航空 preflight（機長/塔台拍板）輕量沿用。

## Evidence
- 2026-07-05: L1 MCQ 答對（D：招牌氣勢、章節呼吸、行政資訊音量與動線重排）——正確抓到「修正量測後病因不是字太小」的核心翻案。
- 2026-07-05: 決策 D0 拍板：**同意** Approval Meaning（文章頁先是讀物、才是工具面板；non-goals 邊界照案）。
- 2026-07-05: L2 MCQ 答對（A：章距/H2 行高是「一大鍋粥」的第一刀）。玩過實驗廚房拉桿。
- 2026-07-05: 決策 D2 拍板：**同意方向**（不放大字、調節奏；「米其林排版挺酷」＝ H1 38px 級距 OK）。**附帶條款：Mogu 真心話降音量後行高要跟著縮**——user 明講不喜歡小字配 1.8 大行距的鬆散感（quiet note 要 tighter line-height）。此條要進 L7 結論與 implementation 要求。
- 2026-07-05: L3 MCQ 答對（B：CJK 字型檔上萬字符要 subset，是中文特有成本）。
- 2026-07-05: 決策 Open Q1 拍板：**sans-first（方案三）**——不引入 serif，先用 scale/節奏拿氣勢；user 自己補一句「書法招牌掛在賽博蘑菇店面上不搭」（品牌判斷，非只省成本）。serif 留未來獨立實驗。
- 2026-07-05: L4 MCQ 答對（C：來源只進 HTML metadata 給爬蟲＝違反可及性）。
- 2026-07-05: 決策 Open Q2 拍板：**標題下輕量「小卡」**——user 反提案，勝過 design.md 原本的 inline 小字選項：「小卡比小字有誠意」「卡片比 pure html text 有質感，pure text looks like 沒寫 css」。**重大品味訊號：降音量 ≠ 去卡片化；縮小、收窄（inline-block 不滿版）、降 padding 都可以，但保留卡片質感。** 此原則同樣約束 L5 TOC 與 L6 收合區的實作。
- 2026-07-05: Q2 補充細節：source 小卡**不要用 📄 這種 cheap emoji**——改設計 SVG icon 或乾脆不放 icon（user 原話）。
- 2026-07-05: L5 MCQ 答對（A：chrome 判準＝是否與內容卡共用視覺文法/撞衫理論）。
- 2026-07-05: 決策 TOC 拍板：**細線導航（hairline rail + active 亮標）**——user 接受「導航穿運動服不算裸奔」的調解，質感店規與去卡片化不衝突。mobile TOC 照 spec（可發現＋不佔首屏）。
- 2026-07-05: L6 MCQ 答對（D：版本歷史是 provenance 不是讀者指令）。MCQ 戰績 L1–L6 全對（6/6 first-try）。
- 2026-07-05: 決策 Open Q3 拍板：**全部進抽屜**（pipeline＋Tribunal＋version 收單一「技術資訊」disclosure），摘要列秀總分當鉤子。
- 2026-07-05: **品味規則升級為全站級：UI chrome 一律 clean SVG line icons、不用 emoji（🔧📄 都 cheap）**——對齊 gu-log 現有 nav 的 search/globe/moon 線條 icon 風格。

## Known Gaps
- （待觀察）

## Teaching Notes
- **互動拉桿大受好評**（「實驗廚房拉桿超酷」）——之後的 level 盡量給可操作的 slider/toggle playground，不只靜態對照。
- 教材檔在 session scratchpad：`L1-restaurant-inspection.html` + live 截圖 before-*.png（tmp，session 結束會消失；如 user 要留檔再搬）。
- 每關 = 教一個概念 + 一個決策確認（preflight 模式）。
- 決策已全數拍板（D0、Q1 sans-first、Q2 標題下小卡、Q3 全進抽屜、TOC 細線）——詳見 Evidence。

## Next Suggested Levels
- 課程完結（L1–L6 全通過）。後續：PR #548 實作若偏離拍板結論，用 debrief mode 驗收實作 vs 決策。
