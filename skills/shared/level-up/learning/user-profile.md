# User 教學檔案（教學前必讀）

從 `claude/USER.md` 移出的教學專用內容 —— 只在 level-up / 講解 / 出教材時載入。
活檔：教學中發現新的品味訊號就更新這裡，不要塞回 always-loaded 的 USER.md。

## 什麼讓 User 爽 (delights)
- 舊版楓之谷 —— **只有大改版 Big Bang 之前那版**，新楓之谷 User 完全沒玩過。遊戲化、北七的教學對 User 超有效。
- 教材要比 YouTube Shorts / Instagram Reels 更好看 User 才肯讀。知識要**載在生動比喻上**，不是旁邊放裝飾。
- User 先讀自包含 HTML 講解、再答一題 MCQ；步調 chill。

## 教學框架（雙類比制）
**兩個都留，依概念形狀選一個；單一題目只用一個類比一路扛到底，絕不混搭兩個遊戲世界。**

- **主力 = Vainglory（手遊 MOBA，多人線上即時戰術競技）。** User 自報 Vainglorious Silver、約 top 0.1% 高端玩家 → 進階機制可直接當類比、不必從新手村解釋。涵蓋面比原本想的廣，大多數「動態／技術」概念都吃得下：
  - 協調 / 編排：指揮 (shotcalling)、輔助遊走、一隊專才配合、「為何不能信單一 agent」（沒有單英雄 carry 全場）。
  - 時機 / 延遲 / 排程：打野算好野怪生成時間、扣掉路程反推出發時機（≈ prefetch／預熱、扣 latency 反推 timeout）；大型目標時機 (Kraken timing)。
  - 平行 / 取捨：清線吃光光（搶吞吐）vs 等隊友分錢分經驗（共享）≈ 一個 worker 獨吞 vs 拆給多 worker；換資源（放小目標換大目標）≈ scope 取捨。
  - 成長（**會重置的時間窗型**）：每場 level 1→12、英雄各有強勢期（Koshka 前期、Varya 後期才變女神）≈ power spike／「某方法前期划算、後期失效」。
  - 已實證有效（gu-log 的 CCC SOP / tribunal 主題 MCQ 全對）。
- **副框架 = 舊楓之谷 (pre-Big-Bang)。** 兩個用途：(1) level-up 技能的等級/XP/打王骨架本身就是楓之谷形狀，當**環境語氣外殼**最自然；(2) 扛 Vainglory 不擅長的「**永久累積、不重置**」型概念 —— 長期苦練、持久狀態、新手村基礎、分級難度、升級帶風險（衝卷軸 ≈ 機率操作）。用道地繁中用語：墮落城市、菇菇寶貝、嫩寶、魔法森林、漢斯、紅水/藍水、卷軸、公會、掉落物、計程車回家。不確定就 web 查，**絕不混入新版內容**。
- **選用規則**：動態／協調／時機／取捨／會重置的 power curve → Vainglory；永久累積／持久狀態／新手村基礎 → 楓之谷。兩種「成長」的差別：Vainglory = 每場重置的時間窗，楓之谷 = 不重置的永久存檔。中間地帶平手 → 用 Vainglory（主力優先）。
- **Vainglory 專有名詞紀律**：通用 MOBA 機制（打野時機、清線取捨、power spike、roam、換資源）model 很熟、直接用、不用查。但**專有名詞層**（英雄名字/技能組、確切野怪生成秒數、等級上限、道具名）model 不可憑印象掰 —— 要嘛停在機制層不點名，要嘛用 User 給的例子（User 是 top 0.1%，本身就是 ground truth），要嘛先跟 User 確認。呼應 USER.md frustrates 的 fact-drift 那條。
- **黑名單：Roguelike 已驗證沒命中，別再用。**
- **航空框架（preflight/debrief 專用外殼）**：user 自評「超中二 不過我喜歡」並主動延伸（AI＝機長自己處理亂流、during notes＝黑盒子、debrief＝查降落點對不對機票）。僅用於 implementation modes 的語氣外殼，教概念仍走雙類比制。2026-07-05 dogfood 實測：外殼扛住五個概念全程有效。
- **debrief 報告不可一次倒完**（2026-07-05 user 明確糾正）：高密度 decisions-first 報告整篇送出＝無聊失敗。必須照 level-up 拆成多個 level，一關一個決策＋MCQ 分段消化。
- 類比要**承載概念本身**（User 跟著故事就吸收到真概念），不是貼旁邊當裝飾；一個強類比一路扛到底。
- 強度：最大化搞笑；約九成劇情、一成精簡技術錨點。

## User 的知識底子（會變動）
- 已上手：Claude Code、LLM 維運、資料庫基本、略懂 SQL。
- 正在學：EAV 屬性模型、多表關聯（站點/任務單資料模型）。
