# Chief of Staff Default Interaction Design

## Learner Goal
- 讓 bare skill invocation 自動產生跨 task 優先序 brief，以單字母回覆完成必要決策，減少重複輸入，同時避免未授權的 coordination mutations。

## Current Level
- Status: mastered
- Last updated: 2026-08-15
- Confidence: 已完整拍板 default brief、shortcut authorization、drift 與 follow-through 邊界

## Evidence
- 2026-08-15: 選擇 Vainglory shotcaller 類比、深度 2、Chat Markdown。
- 2026-08-15: 拍板 bare invocation 應廣泛 read-only 掃描近期 tasks，依興趣、影響與需要使用者介入程度選出前三名，附上最小下一步，不自動 mutation。
- 2026-08-15: 拍板只有存在真正需要使用者決定的分岔時，才提供一次一題的 single-letter shotcall；沒有決策時直接回報不需介入，不為格式製造假選項。
- 2026-08-15: 拍板 bare invocation 永遠 read-only；單字母回覆只一次性授權選項明列的 action 與 targets，不需重複確認，也不得擴張或沿用權限。
- 2026-08-15: 拍板前三名先依 intervention leverage 排序，找出使用者小動作最能改變結果的 tasks，再用 project impact 與 interest 破同分；需解釋排名，不用假精準總分。
- 2026-08-15: 實機發現 visualize inline reference 在目前 iOS client 會顯示成 raw control text，Mac 可正常呈現；Chief of Staff 的預設 brief 因此不能依賴 visualize，需採跨 surface 可讀的 plain Markdown。
- 2026-08-15: 拍板最多三段直排 plain Markdown task cards；mobile label 固定使用 `**Why now:** text` 這類 ASCII colon 加空格格式，避免 fullwidth colon 使 emphasis delimiter 被原樣顯示。
- 2026-08-15: 新增 focus-debt 需求：bare invocation 也要指出可立即 archive 與接近可 archive 的 tasks，藉由小勝利持續降低 sidebar 噪音與注意力負擔。
- 2026-08-15: 拍板在策略 Top 3 之後另設僅於有候選時出現的 `Focus cleanup` lane，區分 `Archive now` 與 `Close to archive`，不把整理價值混入 intervention leverage 排名。
- 2026-08-15: 拍板 split namespace：letters 表示高槓桿策略 shotcall，bare numbers 表示 focus-cleanup actions，並可用如 `B 1 3` 的單次回覆合併授權。
- 2026-08-15: 拍板只有剩下一個明確 permission gate 的 `Close to archive` 候選可編號；選號代表使用者授予該項明列的精確權限，由 Chief of Staff fresh-read 後轉達給 owning thread，授權不得擴張。
- 2026-08-15: 拍板 fresh-read 發現 drift 時，舊授權立即失效；Chief of Staff 必須依最新狀態重新提出 MCQ，不得自行推定使用者仍同意。
- 2026-08-15: 拍板複合回覆遇到 partial drift 時，先執行能證明互相獨立且未 drift 的 actions；只對 drift 項目與其相依項重開 MCQ，無法證明獨立則相關項目一起暫停。
- 2026-08-15: 拍板 `Focus cleanup` 每批最多五個 numbered actions，先列 `Archive now`、再列最近可完成的 permission gates；有更多候選時顯示數量，`0` 取得下一批，舊批次 numbers 隨即失效。
- 2026-08-15: `closed loop`／`open loop` 術語本身不夠直覺；需用「使用者只和 Chief of Staff 對話」對比「使用者仍要自己查看 owning thread」來說明 follow-through 邊界。
- 2026-08-15: 拍板 Chief of Staff 作為 single front door：授權後負責 fresh-read、relay／執行、poll、驗證與安全 archive；新決策回到本 thread，長時間外部等待則精確回報，不假裝會背景自動醒來。
- 2026-08-15: Fresh forward-tests 正確執行 shortcut partial drift，並揭露 fullwidth-colon、跨 lane 重複與無介入 task 補滿 Top 3；實作已改成全域 ASCII bold labels、跨 lane 去重及不補滿策略卡。
- 2026-08-15: Fresh safety review 揭露 follow-through 不能把「完成 permission gate」擴張成未明列的 archive 授權；修正為只有選項明列 archive 或 Chief of Staff 自建 disposable worker 才可直接封存。

## Known Gaps
- 尚待下一次真實 multi-thread pile dogfood 驗證 Codex app end-to-end thread operations。

## Teaching Notes
- 沿用 Vainglory shotcaller 類比；一次只處理一個真實 design decision。
- UI demo 要區分 fragment responsive test 與 Codex client ingestion end-to-end；前者通過不能證明 mobile app 會 render。
- 避免只用 `closed loop`／`open loop` 作為選項名稱；先描述誰負責追蹤與回報。

## Next Suggested Levels
- 實作後以 realistic thread scenarios 驗證 single-front-door contract。
