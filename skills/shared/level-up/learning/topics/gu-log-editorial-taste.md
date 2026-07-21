# gu-log editorial taste

## Learner Goal
- 把「該解釋的沒解釋、不該解釋的解釋太多」拆成可重複套用於 gu-log 文章、writer prompt、review rubric 與 deterministic hooks 的 editorial taste function。

## Current Level
- Status: mastered
- Last updated: 2026-07-16
- Confidence: high; completed the full editorial replay and transferred the principles to a real rewrite decision

## Evidence
- 2026-07-15: 指出 SP-256 文字自然但資訊取捨失衡，主動要求以約 20 個短 shotcall decisions 釐清偏好。
- 2026-07-15: 選擇 Vainglory 賽後 shotcall review 類比、深度 2；要求每次拍板後立即持久化語意決策，避免 compaction loss。
- 2026-07-16: 指出 raw option letters 是 bookkeeping noise，要求全部刪除；紀錄只保留可遷移的 principle、理由、條件與反例。
- 2026-07-16: 完成 SP-256 replay，辨認出問題是文章型態從 source-first 翻譯漂成多重比喻 explainer，不能靠局部 polish 修復。

## Editorial Decisions

### Reader and value
- 文章要讓讀者從公共利益角度判斷提案：管太死可能留下安全但無用的模型；管太鬆可能讓鄰居取得危險能力。
- 預設讀者長期追 AI 新聞，已知道 benchmark 與 Agent。不要為 general public 重播 boilerplate；可重用概念由有趣、值得讀的 glossary 承接。
- Glossary 負責「它是什麼」；正文負責「它在這件事裡改變了什麼」。

### Explanation and hierarchy
- Explanation budget 依「誤解後是否會改變讀者結論」分配；不平均灑給每個術語或段落。
- Capability threshold 的設定權、位置與雙向公共後果，是 Hassabis 這篇的 load-bearing concept。
- Source-specific labels 先講會觸發什麼後果，再補原文名稱。
- 例子只在核心取捨或 failure mode 難以由抽象文字看見時使用；paired counterfactual 優先。
- 開頭直接給 reader-facing conflict；背景採 just-in-time。接受一點微標題黨換取漂亮、緊湊的讀感。
- 每個正文段落必須改變理解或判斷、推進核心因果，或讓風險可見；新 fact 本身不等於 payoff。
- Unknown institution 首次出場要交代它是誰、能做什麼、為什麼此刻與故事相關。重要且可重用才進 glossary；其他用查證過的白話角色描述。

### Narrative trade-offs
- 禁止逐節固定跑「功能／好處／風險／修法」或「evidence／立即 caveat」；這會形成 rubric-shaped prose。
- Read-only audit 部分確認 GPT-5.5 在 mechanism-heavy 題材容易出現此 pattern：SP-212、SP-217 是正例；SP-219 是單一主線清楚的反例。
- 整篇只追一個中央矛盾；代價只在真正反咬主張、改變局勢時出現。
- 一個可信 failure story 若能同時壓測多個 load-bearing mechanisms，可作為條件式手法；不能為了有故事硬塞事故。
- 比喻不是免費裝飾。理想情況是在動筆前選定一個能承載全文的核心比喻／故事視角，後續只延伸同一套映射；臨時切換新比喻會增加讀者的認知負擔。
- 一篇文章最多使用三套獨立比喻系統，且三套是上限而非目標；能用一套說到底就不要開第二套，原文直接清楚時也可以完全不用比喻。

### SP source boundary and MoguNote
- 對原作者本身很強的 SP，正文採 strict source-first：忠實、自然、好讀的 zh-tw 翻譯／轉寫，不混入 gu-log 自己的分析。
- Source fidelity 採 semantic completeness，不追求 sentence completeness：保留所有會改變原文論證的主張；重複修辭、暖場與已交付過的結論可以合併或壓縮。忠於作者真正說了什麼，不必忠於同一件事說了幾次。
- MoguNote 是 gu-log 的靈魂與 value-add：放 insight-first 的 funny stress test、額外 insight、反例、跨文連結或現實延伸。
- 一般情況下，拿掉 MoguNote 後正文仍須邏輯完整；重大原文錯誤是少數例外：忠實呈現原 claim，緊接醒目 MoguNote 修正，不由正文偷偷替作者改口。
- Fact-check 採 materiality gate：只有會改變核心判斷、公共後果、權力關係或關鍵證據的錯誤必須出場；其他只有真的有趣才寫。
- 若一篇有大量數字普遍查不到來源，只放一則自然、簡短的 aggregate evidence-quality MoguNote；禁止逐數字 caveat。

### Language and presentation
- 「首屏」讀起來像支語；改用「開頭、首段、文章一開始」。
- Repo 實查目前沒有完整支語警察 hook：zh-tw style guide 是散文規則，晶晶體 checker 管 English mixing，AI-tells hook 只有窄版 blocklist。後續應把高信心、低誤判用語放 deterministic gate，語境型 taste 留 reviewer。
- Kaomoji 只用常見、已知能穩定渲染的字元；避免 superscript modifier letters 與罕見 glyph 組合。
- Hassabis 原文標題已核對為 `A Framework for Frontier AI and the Dawning of a New Age`；文內 H2 `A Framework for a Frontier AI Standards Body` 不是全文標題。
- 標題新方向：直接翻譯原標題，但刻意採超爆中二的 zh-tw 語氣，因為原文在使用者讀感裡本來就很中二；exact wording 尚待拍板。
- 標題 taste correction：`前沿 AI 之框架` 正式淘汰，只有換虛詞、毫無中二能量；`破曉之時` 可接受。前半需要真正的最終章語彙與畫面，例如「創世綱要／奇點山麓／創世宣言」，但仍應取材自原文而非憑空改寫。
- Hassabis SP 標題拍板：`當沙礫開始思考：前沿 AI 創世綱要與新紀元破曉之時`。素材取自原文的 `make sand think`、frontier AI framework 與 dawning of a new age，夠中二且仍看得懂。
- 中二標題 boundary：氣氛不能蓋過語意。`奇點山麓的創世綱要` 雖然夠中二，但使用者看不懂在講什麼，因此淘汰；最終標題必須保留一個可立即理解的具體 semantic anchor。
- H2／visual hierarchy：保留原文論述順序，但由 gu-log 重切成 3–4 個 narrative turns；只有局勢真正改變時才開新 H2，不替每個制度零件建立功能目錄。Source-first 不要求照抄原文視覺結構。
- MoguNote 本身已是強視覺卡片；避免每節固定重播「H2→正文→note→分隔線」元件節奏，否則頁面像重複模板而非文章。

## Known Gaps
- 尚未以實際重寫成品驗證這套 taste 是否能穩定被 writer 與 reviewer 執行。

## Pipeline Encoding Decision
- 採 thin guardrails + annotated examples，不把整套 taste 複製成長篇 writer checklist。
- Deterministic hooks 只處理高信心 binary failures，例如高信心支語、錯誤 glossary link、缺 source attribution；主觀節奏與品味不能 regex 化。
- Writer 只取得少數 product principles：SP source-first、單一中央矛盾、semantic completeness、MoguNote 是 gu-log value-add 等。
- Reviewer 參考 annotated good／bad articles 做整體診斷，只指出病灶與高槓桿修改方向，不要求每節補齊 pros／cons 或逐條打勾。
- Examples：SP-219 可作單一主線清楚的正例；SP-212／SP-217 的指定段落可作 rubric-shaped prose 反例。引用整篇前要加 annotation，避免 model 模仿反例表面內容。
- 任何 prompt／rubric 實作仍須 simplify review：Keep／Simplify／Drop，防止把一次事故寫成二十條規則。
- SP-256 採全文重寫：保留 ticket 與來源，使用已拍板標題；正文直接、自然翻譯 Hassabis，只重切 3–4 個敘事轉折，MoguNote 僅放必要修正與真正有趣的延伸。

## Teaching Notes
- 全程使用 Vainglory 賽後 shotcall review；一次一題、短回合。
- 每次 user 拍板後，進下一關前立即記錄語意決策、理由與適用條件。
- 絕不記 MCQ option letters、level answer letters 或「選 A／選 B」等噪音。

## Next Suggested Levels
- 以重寫後的 SP-256 做 debrief，驗證 writer／Vibe／Fresh Eyes 是否都能抓到比喻漂移與 source-boundary 問題。
