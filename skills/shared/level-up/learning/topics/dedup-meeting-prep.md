# Dedup 設計會議準備（討論 session：schema + 演算法攻防）

## Learner Goal
- 準備跟 GuangFuHero 團隊開會對線 dedup 設計。四大目標全要 ＋ 第五目標（演算法立場成形，因演算法半邊還沒定案）。
- 優先序（提案待 user 確認）：①盲點掃描 → ②演算法立場成形 → ③red-team 拷問 → ④底線清單 → ⑤說服答辯劇本。
- 範圍 = 資料庫設計 + 「怎麼判斷 2+ tickets 是否重複」的演算法（含 data-driven solution 要不要採用）。
- 命名對齊本身是討論點：會議筆記用舊名（dedup_audit、tickets_relations），SSOT §九已收斂成 ticket_dedup_audit_events / ticket_duplicate_pairs。
- 2026-07-30 快層規則子課程目標：能用自己的話解釋整套規則、抓出 AI 沒根據的假設、逐條決定保留／修改／刪除，最後整理成 backend 可實作的規格；每關理解與決策完成後同步精修 system-design HTML §03。

## 會議筆記素材（user 提供，raw agenda）
- 後台可改規則(規則放DB)、高樓樓層比對、data-driven 演算法(測試案例迭代)、AI 額度/API key、Phase 1 門檻(100m/15min/30m/T1–T3 靠現場資料校正別釘死)、200ms 可調+空間索引、confidence_score 不混用、merge audit v1 深度、tickets_relations(可能不需要)/dedup_audit(需要,查 audit_log ER-diagram alembic)/audit_log jsonb、embedding vector search(what columns/models?)、pg_trgm 中文支援疑慮、hybrid RAG(vector+BM25+rerank)、SiliconFlow free tier、test-cases 能分好/能併好、ticket graphQL 包三四個 table。

## Status
- learning。快層規則子課程採 Vainglory 會戰前 shotcalling 類比、深度 3；adaptive 代表以 chat 逐關教學並把已確認的改動直接施工到既有 HTML，不另開教材頁。
- 2026-07-31 既有方法研究後的新地基課程採 `A3m`：全程用 Vainglory 會戰類比，在聊天中逐關深挖。目標是讓 user 親自判斷每次送出的 `ticket` 應只代表一筆不可遺失的回報，還是也同時代表可彙整多次回報的實際需求；最後能決定是否拆成 Report／Case、快層接受提示後該怎麼保存資料，以及如何同步回 system-design HTML／SSOT。

## 剩餘關卡地圖（動態增減）
- Act I 內務審查：7 張表逐一確認、Q1–Q6 立場、命名歧異（ticket_low_id vs *_uuid；舊名 vs SSOT 新名）。
- Act II 演算法軍議：Phase 1 門檻與現場校正、空間索引/200ms、樓層比對、慢層技術選型（embedding columns/models、pg_trgm 中文、hybrid RAG、SiliconFlow free tier）、data-driven test-case 迭代法。
- Act III 模擬戰：red-team 拷問 per 主題。
- Act IV 出征準備：底線清單、會議 agenda、說服劇本。

## 已掌握（概念）
- 2026-08-01 參考系統平衡檢查：user 要求對 Carol 明列實際查過的文件，不能只寫含糊的「9-1-1／311」；也要求找單一 ticket 同時承載回報與工作案件的反例。read-only 研究確認三種成熟模式並存：NENA NG9-1-1 的 Call／Incident 分離；Austin 311 的每筆 Service Request 保留＋duplicate parent/master；FixMyStreet／SeeClickFix 的單一 report/issue＋subscribe/follow/update。泛用 Zendesk、Request Tracker、Jira、GitHub 也證明 ticket-only 可成熟運作，但風險與救災不同。尚未找到 primary source 足夠強的「災害救援 ticket-only 派工模型」；因此不能宣稱業界一致支持拆表或單表，應依是否必須保存每次原始回報、錯誤 merge 風險與結案單位決定。
- 2026-08-01 Report／Case 第二關：user 能用自己的話指出現行 `tickets` 同時代表「使用者送出的一次回報」與「確實存在、需要處理的需求」，而 9-1-1／311 類系統會拆開這兩種責任；也主動發現拆分後 `task` 的歸屬會變得需要重新定義。user 不接受 `need_cases`，因 `need` 詞性不直觀；命名待改。初步直覺選三戶分三個案件（B），但明說仍在猜，需用「能否各自結案」釐清案件邊界。
- 2026-07-31 Report／Case 第一關：user 選 C，認為同一現實需求的多次回報都應保存，但連到同一件待處理需求；隨即 challenge「schema 是否實際可做、是否有研究或既有系統採用」，下一關需比較 master-ticket 最小改法與 call／incident 正規分層，不可直接把完整五表模型當答案。
- 2026-07-30 快層候選第一關：user 已抓到候選集合、必要條件、排序與 UI 提示是不同步驟；也理解聯集符號 `∪`，並要求文件使用標準術語「聯集」。進一步 challenge 雙候選網後拍板 v1 移除同帳號歷史查詢：在相同距離資格下，它不會增加有效結果，只增加查詢、逐 pair 評估與維護成本；`base_geometries.created_by` 改為選出第一名後才決定提示文案。
- 2026-07-30 快層排序決策：user 偏向先提高 recall，接受早期稍微多提示來收集真實回饋；距離與時間不再用 100m／15min 硬淘汰，改作 half-life ranking signal。全部候選取第一名後仍須達 `hint_threshold` 才提示；user 主動把名稱從 `prompt_threshold` 改成 `hint_threshold`，避免與 LLM prompt 混淆。理解 `rank_score` 只用於排序，不代表重複機率。
- 2026-07-30 `task type` 決策：user 拍板 v1 只把 `tickets.task_type` 當粗略 ranking signal，不同不淘汰；理解 ticket 可有多種 child task，而現行 `tickets.task_type` 只跟著主要／第一個 child type，因此 exact match 既非必要也非充分條件。缺值代表沒有 evidence，不應當成 0 扣分；完整 child task 集合比對等 API 能收到整份 ticket＋tasks 草稿再升級。
- 2026-07-30 ranking 參數決策：user 主動要求 data-driven 決定 distance/time half-life、訊號權重與 `hint_threshold`，不在單一 A/B 情境憑直覺填數字。產品目標維持 recall-first；評估要重播每張新單的完整候選排序與 top-1 提示流程，至少看 top-1 recall、duplicate hint recall、false hint rate，不能只看 pair accuracy。
- 2026-07-30 語意比對研究決策：user 要求先比較方法，不掉進 model list 海。第一輪並列 local lexical／字元 n-gram、multilingual embedding、cross-encoder reranker、strict structured-output 小型 LLM，允許 cascade；全部用同一批 query-level 候選集合比較品質、完整結果 p50／p75／p95 latency、timeout／invalid output、RAM／VRAM／index、money/query、self-host compute 與 PII 邊界。方法與模型都先 shadow，不因名稱或 benchmark 直接升格成 v1。
- 2026-07-30 初步技術方向：字元 n-gram 作最低成本可解釋 baseline；embedding 作可預先計算的第四個 ranking signal；reranker 只重排 top-K；LLM 若需要 order＋reason codes，先放 shadow／非必要路徑。NVIDIA `llama-nemotron-rerank-vl-1b-v2` 可自架但視覺 encoder 對純文字 ticket 多餘，應優先比較 text-only reranker。現有 13 組 pair fixture 只夠 sanity check，正式選型需要多候選、人工 `confirmed`／`rejected` 的 query-level 資料。
- 2026-07-29 system-design HTML debrief：能正確區分「讀者看得懂的白話說明」與「程式必須精確保留的 identifier／enum contract」；判斷應改寫前者、保留後者原值。也能判斷「收合」只是畫面狀態，不應自動改變已讀進度；已讀必須由明確動作標記。
- ticket_duplicate_pairs 狀態分工：status=現在位置、layer1_outcome=歷史事實。
- denormalization / YAGNI 直覺天生就有：能自己把概念對映到 SSOT（"not following SSOT"），有遷移能力。
- 狀態機圖 = status 欄位的使用說明書（格子=合法值、箭頭=合法 UPDATE、沒畫的=不該寫的 UPDATE）；懂 text+CHECK vs PG ENUM 取捨。
- EAV（ticket_dedup_attributes）：衍生特徵另開表、加新種類不動 tickets 結構。
- audit_logs（記「改了什麼」）vs dedup 稽核表（記「為什麼決策」）：自丟 what-if「兩張表合併會怎樣」並自答「會污染既有 audit_logs」→ 自推「另開新表較好」。監視器 vs 會議記錄類比有效。
- 政策三表（dedup_settings / rule_versions / ai_configs）：規則版本疊加不覆蓋＝歷史判定可解釋；並自己補上「一鍵回滾也是版本化的好處之一（非唯一目的）」的正確修正。補充教材：`cth-note/dedup-workspace/rule-versioning-story.html`（兩個宇宙對照）——user 讀完評「ok read、有建出心智模型，但不上癮（能忍著讀完）」→ 純敘事時間軸頁只到及格線；要上癮大概需要互動成分（點擊探索、預測再揭曉）或更強遊戲感，下次做補充頁時試。
- DDL 讀法基礎已補完（家教回報 tasks/report-ddl-tutor.md）：三段式讀法（欄名→型別→約束）、常見型別、NOT NULL/DEFAULT 三分法、PK vs 業務 UNIQUE 分工、外鍵、CHECK、複合 UNIQUE、partial index 全數有作答證據；卡過「表 vs 欄地盤」「複合 UNIQUE 衝突判定」已修正。教學法教訓：**先教才考**（user 明確糾正過先考後教）。
- **事實漂移警報**：Codex 家教段自編過 EAV 表不存在的欄名（namespace／attribute_key；真實鍵是 property_name/source_layer/COALESCE(source_version,'')）——開會前要重新錨定真實欄名；委派工單須強制「每個主張附 file:line」。
- user 自挖會議級問題：`ticket_duplicate_groups.created_by` 可空 vs「群組只在人工合併時誕生」矛盾，該不該 NOT NULL → 候選議程。
- **EAV 表挑戰（進行中，user 發起）**：tickets 對去重訊號並不乾淨（phone raw、無地址/樓層欄），但正規化系 key 的正解是 expression index／generated column 而非 EAV；18 key 三分類（決定性正規化→索引解決／全新資訊→找家／昂貴衍生→慢層專屬）；CC 立場＝v1 不建 EAV、降級為慢層隨行行李。**懸而未決：reporter.role／proxy_batch_id／manual_hint 的家（tickets 硬欄位 vs 小表）**，user 尚未拍板。
- 委派判斷：判斷在前、苦工在後且量大 → 委派；判斷跟苦工纏一起或只剩兩刀 → 自己動手。

## 已拍板的決策（會議素材，steers future）
- **快層 timeout 衝突定案（2026-07-28）**：移除 `fast_timeout_ms`、200ms 預設值與後台旋鈕；後端仍保留固定的查詢安全期限，逾時就 fail-open 放行並記錄指標。HC 的會議脈絡支持移除任意的 200ms 政策值，但網路順暢不代表後端查詢永遠快速；DB lock、連線池塞車、負載尖峰或 query plan regression 仍需工程層安全期限兜底。
- **樓層 v1/v2 邊界定案（2026-07-28）**：v1 樓層不參與候選進出，只在提示卡顯示；UI 稱「已有的求助單」，不稱「舊單」或跨層誤叫「任務單」。v2 要解析並正規化樓層；具體技術路線尚待實作前確認，建議 deterministic parser 優先、LLM structured output 只作模糊字串 fallback，任何失敗都 fail-open、不阻擋送單，且先 shadow 驗證再讓樓層成為排除候選的硬條件。
- **快層提示 UI 決策（2026-07-28）**：採兩步 progressive disclosure。第一步只讓使用者判斷「是不是現在要回報的同一件事」，確認後才顯示留言／建議修改／更新需求。主動作不用抽象的「是，同一件事」，改成直接描述去向的「去看看這張求助單」，並讓按鈕本身就是 permalink，避免重複連結；另一個動作定案為「不是同一件事，另外開單」，輔助文字「將建立新的求助單，分開追蹤處理」，不承諾專人。候選卡 mobile-first 顯示樓層、需求數量、回報時間，手機可點開／長按、desktop 可 hover 或 keyboard focus 預覽；hover 只是 enhancement，不承載必要資訊，開連結前需保住尚未送出的表單內容。
- **快層候選與排序定案（2026-07-30）**：v1 只查附近、未結案的候選；移除同帳號歷史查詢。座標可信是 happy path，座標缺失或明顯無效時 fail-open；真正的座標品質 fallback 等有 location source／accuracy／pin confirmation 等資料再設計。距離與時間採 half-life ranking signal，100m／15min 只作強訊號的討論起點；`tickets.task_type` 只作粗略 ranking signal，不同不淘汰、缺值不扣分。取第一名後須達 `hint_threshold` 才提示。candidate boundary 待確認；half-life、權重與門檻改由 top-1 data-driven evaluation 決定。
- **會議用可拖曳快層圖已施工（2026-07-30）**：system-design §03 內嵌由 `diagram-editor` 資產改成的專用編輯器，另有整頁模式；一般節點是已確認骨架，金色＋💬 是未決內容，可拖曳、改字、加註解並匯出 Mermaid。它只服務 design-time 討論，絕不直接控制 production；拖曳座標不會匯出。圖上仍待逐關拍板的是 candidate boundary、half-life、排序權重與 `hint_threshold`。
- **送出者／受災戶身分拆分定案（2026-07-29）**：v1 只用 `created_by` 判 `reporter_relation = same | different | unknown`；active GraphQL 建單需登入且 mutation 固定填登入者 UUID，所以正常新單通常是 same/different，unknown 留給 legacy／import／未來匿名資料。`affected_person_relation` 不從現有聯絡欄位硬猜：`contact_name` required 但只是現場聯絡人自由文字，`contact_phone`／`contact_email` nullable，且沒有電話角色 contract，因此 v1 維持 unknown。unknown 仍跑地點＋時間＋類別，只提示「附近可能有相同需求」，不宣稱鄰居撞單。
- **Q2 立場**（已寫回 SSOT §七）：單後端 + PG VM 不用為百萬人設計 → v1 走 join、先推 POC、瓶頸出現再重構。
- **rejected pair 永久黏**（立場 1）：worker 查詢層排除；理由=錯誤不對稱哲學延伸（錯合併 >> 漏合併）。
- **Layer 1/2 命名廢除 → 快層/慢層**：schema 全改（'fast'/'slow'、hint_outcome、rescan_needed、fast_*/slow_*、hint_accepted、pause_slow）。
- **Carol 會議 ground truth 推翻文件**：鄰居撞單送出者也收完整選項（開單者常是志工、樂意參與；所有單公開，個資疑慮是假議題）。AskUserQuestion 拍板：選項一視同仁、admin 照舊收通知。
- **double-submit 答辯定稿**：前端 disable/debounce 只擋「手滑」；擋不住的（回應丟失+重送、跨裝置、NGO 批次匯入）本來就是慢層存在理由；反手建議 backend 加 idempotency key（submission_uuid + UNIQUE）。故事要挑「前端擋不住」的機制才立於不敗。

## 未定案 / 等團隊拍板
- **Report／Case 架構方向（2026-08-01 新發現）**：研究既有 9-1-1／311 系統後，現行 `tickets` 可能混合了「一次回報」與「可派工、可結案的需求案件」兩種責任。user 認為值得回報 Carol，也傾向把資料模型與整體工作方式排在快層／慢層之前，因演算法的目標可能從「阻止／合併 ticket」改成「把 report 連到正確案件」。尚未定案是否拆表、案件邊界、資料表命名與 `ticket_tasks` 歸屬；在確認前不得把 GPT 提案直接寫成 production contract。
- **可拖曳快層圖仍有未決參數**：編輯器本身已於 2026-07-30 施工；圖仍是可質疑、可迭代的 design-time 草稿，不是 production 規格。候選來源、距離／時間／`task_type` 訊號與 `hint_threshold` 骨架已同步；candidate boundary、half-life、排序權重與門檻值繼續逐關決定。
- **`contact_phone` 角色仍待團隊拍板（2026-07-28）**：user 傾向把它定義成「本單聯絡電話，可填受災戶、志工或其他已知聯絡人，並記錄角色」。最小提案為 nullable `contact_phone_role = affected_person | reporter | other`；NULL 代表舊資料／角色未知，只能聯絡、不能當去重身分訊號，不另設 `unknown` enum。`optimized-version` 現況只有 nullable 的現場／follow-up 聯絡方式，沒有角色欄位或代報表，因此尚未涵蓋；此為提案，不是已定案 contract。
- **undo（confirmed 反悔）是紅線要求，但 SSOT 沒定 undo 後卡回哪狀態**（suggested 重審 or rejected？）→ 候選 Q8。
- **merge 語意細究**（Task #8）：數量語意（2+2 箱=4 or 2？）、內容互補欄位合成、取代（=merge 特例）、三張成群 canonical 選法、merge 後副件被更新 → 可能產出 Q9。
- 旋鈕（快層閘門調音台）存廢+命名留 backlog（Task #7），等 Act II 演算法討論再定，別先幫可能被砍的旋鈕打蠟。
- 演算法半邊（慢層選型、data-driven）尚無 SSOT 定案 —— 是「立場成形」不是「防守既有設計」。

## 詞彙 / 品味（硬規則）
- **廢詞（絕不再用）**：「安心話」（user: sounds like cn, wtf）；「個資疑慮」當去重擋箭牌（Carol 證偽）；「過堂」（看不懂）→ 改「逐一確認」；「13 個案例**守住門檻**」這類翻譯腔動賓亂配（user: 懶覺中文）—— 動詞要配得上受詞，寫人話；「**待團隊決**」這類砍尾縮寫（決定→決）也中槍（user: 又是三小懶覺中文）→ 站上已改「未決問題」——內容裡的詞一律寫完整，不自創縮寫。
- **user 對「AI 生的代號」零容忍**（Layer 1/2、情境 A/B/C、T1–T3、branch_a 全中槍）→ 新名詞一律用人話。
- 2026-07-28 system-design HTML 全頁改寫的基準讀者已拍板為「大三資工生」：可假設懂基本 DB／API，但不熟本專案；標準 technical term 與 code token 保留，專案自創詞、會議黑話、AI 翻譯腔必須先用台灣口語講清楚。
- 2026-07-28 technical term 規則採「午餐測試」：台灣工程師真的會講且更精準才保留，第一次出現補一句人話；刪除語意已包含的贅字，例如「固定排程的背景工作」縮成「背景排程工作」。
- 2026-07-28 system-design HTML 資訊架構採雙層閱讀：現行做法與原因先顯示，規則、DDL、歷史紀錄放摺疊區；已讀內容也要能收成 outline，保留閱讀進度感，動畫方向為 iOS/macOS 式平順、可追蹤內容去向。
- 2026-07-28 閱讀互動拍板：區塊右下角另設「讀完並收起」，不把一般收合誤算成讀完；完成時可有輕量 silly animation。整頁 Polaris 是 chill、好玩，同時 informative、educational，互動要引起好奇但不能蓋過技術內容。
- 課文品味：sonnet 版太無聊 → fable 接手；課文必須場景先行、角色開口說話、劇情載知識，不是「說明文＋類比裝飾」。光復在地假資料敘事對 user 有效。
- **故事角色名必須自帶職位**（user 拍板）：裸名（阿華／小美／老王）是白噪音，只有職位有資訊量。要嘛只用職位，要嘛用職位縮合名——user 自創：阿台=後台 admin、小幹=幹部、老工=工程師（此三名已獲批准，之後故事沿用）。
- mock data 合理性原則：每齣戲的機制必須對得上快層/慢層規則，不能只是好笑（user 高品質 design smell：不合理的 user story 會害團隊為爛情況設計資料結構）。

## 工程教訓
- sed 全域替換會吃掉「記錄舊名的命名決定」本身（自我指涉事故）；改 SSOT 命名紀錄要用舊名原文寫、避開替換 pattern。
- **UI 驗收 SOP**：改 dedup-system-design 站一律測三組寬度 3840 全寬 / 2133（90% 半寬）/ 1920（100% 半寬），全部 pageHScroll=0、表格框內捲。曾踩 grid 子元素 min-width:auto 被寬表撐爆 → `.flow>*{min-width:0}`（4K 全寬時 bug 不可見，易誤判正常）。**同型再犯（2026-07-12 夜）**：摺疊動畫容器 `.mf-b`（grid）的 item `.mf-bi` 沒加 min-width:0，17 欄 mock 表框內橫捲整個失效 —— 以後任何新 grid 包既有內容，item 一律同時加 `min-height:0;min-width:0`。
- **contenteditable 未失焦的改動不進 edits map**：還原/匯出只掃 edits 會漏「改完直接按按鈕」那筆 —— 還原改掃 originals 全量復原、匯出前先 `saveEl(document.activeElement)`（2026-07-12 uiux-auditor 抓到、CC 重現修復）。
- **大改動後雙 fable review 有效**：內容審查抓到 §03 新拍板輻射不到 §01/§04 的 5 處矛盾（H1 代報 EAV vs 小表、H2 題庫 700m vs 候選圈 300m、H3 佛祖街 race condition）；fresh-eyes UI 稽核抓到 C1/C2。「新章拍板後，全站舊章要做一輪同步掃描」列為固定步驟。

## 欠帳（下一批文件同步）
- dedup-brief 站（11 處 Layer 舊詞）、dedup-test-cases.md（1 處安心話）、**index.html DTC-001「送出者只收安心話」與 Carol 改版矛盾**、dedup-eav-columns.md / dedup-admin-onboarding.md（Layer 舊詞）、獨立 dedup-state-machine.html（Layer 舊詞 24 處）尚未換新詞彙；vercel 推送等 user 驗收後一次推。

## Teaching Notes
- 2026-07-30 快層候選教學需以 18 歲初學者粒度重拆；user 明確指出「地點網／帳號網」不具描述性、直接討論查詢是否冗餘跳太快。後續固定改稱「附近求助單查詢／同帳號歷史查詢」，先教候選、各查詢輸入輸出、合併，再談取捨。
- 2026-07-30 候選查詢基礎：user 正確判斷候選查詢只負責從大量既有單中找出一小批值得後續比較的資料，不直接判重複、不排序。
- 2026-07-30 附近求助單查詢：user 能依半徑正確選出位置候選，並區分這一步尚未檢查帳號、時間、任務類型或是否重複。
- 2026-07-30 同帳號歷史查詢：user 正確判斷查詢只依 `created_by` 取回同帳號的既有單，不受距離影響；理解這只證明送出者相同，不代表同一事件。
- 2026-07-30 聯集關卡：user 正確選出兩種查詢結果的聯集，理解同一張單只進候選集合一次；學會 `∪` 後主動要求回到標準術語「聯集」。
- **重要糾正**：schema 交付物是 vibe coded（Codex 艦隊產的），user 正在還認知債 → 逐一確認＝他在學自己的 schema，不是複習。每關只講一個東西、細節現場攤開不能只丟代號、/chill 模式已啟用（PTT 說故事、一關一口）。
- 先備：dedup-schema topic 概念全 mastered，不重教，直接站在上面討論。
- 續用 Vainglory 公會世界觀，不混楓之谷；輕鬆、九成劇情一成技術錨點。
- 討論 session：唯讀為主，不動 repo 檔案（除 learning 紀錄）。
- SSOT: `.local/dedup-design.md`（§七/§八/§九）；未決 Q 清單: `.local/tasks/report-converge.md`。

## Next Suggested Levels
- 優先序拍板（決策確認）→ Act I 第一張表逐一確認。
