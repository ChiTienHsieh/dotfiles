# gu-log 文章頁 editorial presentation（PR #548 openspec preflight）

## Learner Goal
- Preflight 導讀 openspec change `improve-article-editorial-presentation`（PR #548），理解三個 scope（typography／首屏 metadata／底部工具收斂）與決策點，形成「同意哪些、要改哪些」結論回給 orchestrator（%29）。
- User 明講：沒有 before/after prototype 看不懂改版提案 → 教材必須帶視覺對照（live 截圖 + 互動 mock）。

## Status
- mastered（MCQ 6/6 first-try；三個 open questions 全拍板）。

## Analogy（landed）
- 米其林餐廳 vs 工廠食堂（user 選的），深度 3。對映：正文=菜、H1=招牌、H2=菜名牌、行高=上菜節奏、TOC=牆上菜單、source card=進貨單、底部工具牆=結帳過九攤、collapse=行政櫃檯。外殼：航空 preflight 輕量沿用。

## 已掌握（概念）
- 修正量測後病因不是「字太小」，而是招牌氣勢/章節呼吸/行政資訊音量與動線。
- CJK 字型檔上萬字符要 subset，是中文特有成本。
- 來源只進 HTML metadata 給爬蟲 = 違反可及性。
- chrome 判準 = 是否與內容卡共用視覺文法（撞衫理論）。
- 版本歷史是 provenance 不是讀者指令。

## 已拍板的決策（steers PR #548 實作）
- **D0**：同意 Approval Meaning —— 文章頁先是讀物、才是工具面板；non-goals 邊界照案。
- **D2**：同意方向 —— 不放大字、調節奏，H1 38px 級距 OK。**附帶條款：Mogu 真心話降音量後行高要跟著縮**（user 不喜歡小字配 1.8 大行距的鬆散感，quiet note 要 tighter line-height）。
- **Open Q1 → sans-first**：不引入 serif，先用 scale/節奏拿氣勢（「書法招牌掛在賽博蘑菇店面上不搭」）。serif 留未來獨立實驗。
- **Open Q2 → 標題下輕量「小卡」**：勝過 inline 小字（「卡片比 pure text 有質感」）。**重大品味：降音量 ≠ 去卡片化；縮小、收窄（inline-block 不滿版）、降 padding 都可以，但保留卡片質感。** 此原則同樣約束 TOC 與收合區。source 小卡不要用 cheap emoji（📄）→ 設計 SVG icon 或不放。
- **TOC → 細線導航**（hairline rail + active 亮標）；mobile TOC 照 spec（可發現＋不佔首屏）。
- **Open Q3 → 全部進抽屜**（pipeline＋Tribunal＋version 收單一「技術資訊」disclosure），摘要列秀總分當鉤子。
- **品味規則升級為全站級：UI chrome 一律 clean SVG line icons、不用 emoji（🔧📄 都 cheap）**，對齊 gu-log 現有 nav 的 search/globe/moon 線條 icon 風格。

## Teaching Notes
- **互動拉桿大受好評**（「實驗廚房拉桿超酷」）→ 之後 level 盡量給可操作的 slider/toggle playground，不只靜態對照。
- 每關 = 教一個概念 + 一個決策確認（preflight 模式）。

## Next Suggested Levels
- 課程完結。後續：PR #548 實作若偏離拍板結論，用 debrief mode 驗收實作 vs 決策。
