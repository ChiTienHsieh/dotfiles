# Dotfiles cross-session message guard debrief

## Learner Goal
- 在 push 前確認完整 commit range，連同原始 dirty worktree 一起審查，理解哪些變更值得納入同一批出貨。

## Current Level
- Status: mastered
- Last updated: 2026-07-22
- Confidence: 深度 2 三關完成

## Evidence
- 2026-07-22：選擇航空乘客名單類比、深度 2、Chat Markdown。
- 2026-07-22：選擇把 reviewed dirty changes 搬到最新 origin/main 的隔離 branch，依行為規則與學習紀錄拆成 atomic commits，避免在落後 main 上混合提交。
- 2026-07-22：確認所有跨 task/session 訊息都採緊鄰 send 的 fresh read；無法確認收件方現況時 fail closed，pause、提醒與狀態同步不設例外。
- 2026-07-22：拍板 final gate 必須由 fresh reviewer 審完整 origin/main..HEAD；behavior rules 做 safety+simplify、learning records 做 public-safe+一致性，只有 SAFE TO PUSH 才出貨。

## Known Gaps
- 尚未在下一次真實跨 session 傳訊中觀察 agent 是否能穩定遵守 fresh-read timing。

## Teaching Notes
- 使用航空 debrief 外殼，一次一關一題。
- 聚焦完整 push boundary、fail-closed guardrail、dirty learning records 的 commit grouping 與 review evidence。

## Next Suggested Levels
- 後續可抽查一次真實跨 session handoff，確認 guardrail 沒有被舊 snapshot 或摘要繞過。
