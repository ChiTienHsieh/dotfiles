# USER

關於這台機器的唯一使用者（User）。活檔，邊互動邊補。目的是「了解 User 好把事做好」，不是監控檔。

## 基本
- 名字：Sprin（GitHub: ChiTienHsieh）
- 怎麼稱呼：Sprin
- 時區：Asia/Taipei (UTC+8)
- 語言：CC 回覆一律台灣繁體中文 (zh-tw)。User 打英文是為了打字快，但讀英文偏慢（約國中程度）。完整語言規則在 CLAUDE.md。

## User 在乎什麼
- 職業：AI 應用工程師 (AI Application Engineer)。技術棧：Python、FastAPI、LLM。環境：macOS M1/M2、Python 用 uv、套件偏好 bun > npm。
- 重視手藝與品味，討厭最大公約數的安全牌。要有觀點的偏見 > 無聊打太極（這份品味對應到 CC 的 SOUL.md）。
- 現在在做：User 志工參與 GuangFuHero（光復超人）救災平台；用 level-up 技能學它的站點/任務單資料模型。

## 什麼讓 User 爽 (delights)
- 舊版楓之谷 —— **只有大改版 Big Bang 之前那版**，新楓之谷 User 完全沒玩過。遊戲化、北七的教學對 User 超有效。
- 教材要比 YouTube Shorts / Instagram Reels 更好看 User 才肯讀。知識要**載在生動比喻上**，不是旁邊放裝飾。
- User 先讀自包含 HTML 講解、再答一題 MCQ；步調 chill。

## 什麼讓 User 煩 (frustrates)
- 無靈魂的打太極（「有些人喜歡 A、有些人喜歡 B」）、客服廢話、無聊文件。
- 太多沒解釋的英文術語；簡體中文用語或自造怪詞（要道地 zh-tw）。
- 要 User 幫忙轉達 CI / codex 紅綠燈 —— 那是 agent 自己該盯的。
- 我憑記憶背數字／門檻、而不是讀實作 ground-truth（最新事實依據）—— User 會抓到事實漂移 (fact drift)。講任何具體數字前，先讀程式碼/設定確認，不要背。

## 教學框架（給 level-up / 講解用）
**雙類比制 —— 兩個都留，依概念形狀選一個；單一題目只用一個類比一路扛到底，絕不混搭兩個遊戲世界。**

- **主力 = Vainglory（手遊 MOBA，多人線上即時戰術競技）。** User 自報 Vainglorious Silver、約 top 0.1% 高端玩家 → 進階機制可直接當類比、不必從新手村解釋。涵蓋面比原本想的廣，大多數「動態／技術」概念都吃得下：
  - 協調 / 編排：指揮 (shotcalling)、輔助遊走、一隊專才配合、「為何不能信單一 agent」（沒有單英雄 carry 全場）。
  - 時機 / 延遲 / 排程：打野算好野怪生成時間、扣掉路程反推出發時機（≈ prefetch／預熱、扣 latency 反推 timeout）；大型目標時機 (Kraken timing)。
  - 平行 / 取捨：清線吃光光（搶吞吐）vs 等隊友分錢分經驗（共享）≈ 一個 worker 獨吞 vs 拆給多 worker；換資源（放小目標換大目標）≈ scope 取捨。
  - 成長（**會重置的時間窗型**）：每場 level 1→12、英雄各有強勢期（Koshka 前期、Varya 後期才變女神）≈ power spike／「某方法前期划算、後期失效」。
  - 已實證有效（gu-log 的 CCC SOP / tribunal 主題 MCQ 全對）。
- **副框架 = 舊楓之谷 (pre-Big-Bang)。** 兩個用途：(1) level-up 技能的等級/XP/打王骨架本身就是楓之谷形狀，當**環境語氣外殼**最自然；(2) 扛 Vainglory 不擅長的「**永久累積、不重置**」型概念 —— 長期苦練、持久狀態、新手村基礎、分級難度、升級帶風險（衝卷軸 ≈ 機率操作）。用道地繁中用語：墮落城市、菇菇寶貝、嫩寶、魔法森林、漢斯、紅水/藍水、卷軸、公會、掉落物、計程車回家。不確定就 web 查，**絕不混入新版內容**。
- **選用規則**：動態／協調／時機／取捨／會重置的 power curve → Vainglory；永久累積／持久狀態／新手村基礎 → 楓之谷。兩種「成長」的差別：Vainglory = 每場重置的時間窗，楓之谷 = 不重置的永久存檔。中間地帶平手 → 用 Vainglory（主力優先）。
- **Vainglory 專有名詞紀律**：通用 MOBA 機制（打野時機、清線取捨、power spike、roam、換資源）model 很熟、直接用、不用查。但**專有名詞層**（英雄名字/技能組、確切野怪生成秒數、等級上限、道具名）model 不可憑印象掰 —— 要嘛停在機制層不點名，要嘛用 User 給的例子（User 是 top 0.1%，本身就是 ground truth），要嘛先跟 User 確認。呼應 frustrates 的 fact-drift 那條。
- **黑名單：Roguelike 已驗證沒命中，別再用。**
- 類比要**承載概念本身**（User 跟著故事就吸收到真概念），不是貼旁邊當裝飾；一個強類比一路扛到底。
- 強度：最大化搞笑；約九成劇情、一成精簡技術錨點。

## User 的知識底子（會變動）
- 已上手：Claude Code、LLM 維運、資料庫基本、略懂 SQL。
- 正在學：EAV 屬性模型、多表關聯（站點/任務單資料模型）。
