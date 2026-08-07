# gu-log agent instructions cleanup debrief

## Learner Goal
- 確認規則符合原意、未來 agent 不會誤解，以及 branch cleanup 沒有誤刪有價值的工作。

## Current Level
- Status: mastered
- Last updated: 2026-07-24
- Confidence: high

## Evidence
- 2026-07-24: 選擇航空事故回放類比、紮實打底深度、Chat Markdown。
- 2026-07-24: 拍板 `issue this:` 維持低摩擦 dictation normalization、語意改變才確認、issue-only 後停止；並新增 1–2 句 intention brief，讓使用者以最低注意力先核對核心意圖，再自行決定是否細讀 issue。
- 2026-07-24: 確認 intention brief 放在 issue 建立／更新後的完成回覆，不新增建立前 approval gate；理由是錯誤 issue 可低成本修正，而省掉每次往返確認的收益很大。
- 2026-07-24: 拍板薄 `AGENTS.md` 作為 universal rules 與 canonical pointers 的 Tier-0，`CLAUDE.md` 維持單向 import，低頻細節留在 lazy references。
- 2026-07-24: 用既有 task 驗證 `issue this:` 必須同時支援建立新 issue 與更新 canonical issue；完成回覆先給 1–2 句 intention brief，再讓使用者決定是否點進 issue 細讀。
- 2026-07-24: 正確選擇 value-based branch pruning：只有已合併／等價取代、未被使用且可復原的 local branch 才能刪除；不能依 branch 數量或年齡 bulk delete。

## Known Gaps
- 無。

## Teaching Notes
- Use these examples: 改航決策、飛行手冊、黑盒子與航班封存。
- Avoid assuming: branch 數量本身等於可刪除性。

## Next Suggested Levels
- 後續可在真實 `issue this:` 使用情境抽查 intention brief 是否足以讓使用者低成本辨認方向。

## Workflow Events
- 2026-07-25: 跳過 global `issue this:` backlog routing 的 post-implementation debrief。
