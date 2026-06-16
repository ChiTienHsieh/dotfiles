# AgentFlow（popo-agent-flow）專案商業邏輯

> 這份記「**這包 repo 本身**怎麼運作」的學習狀態（專案商業邏輯）。通用底子另記於 [[llm-app-foundations]]。

## Current Level
- Status: learning（2026-06-17 開課，尚在第一輪）
- Last updated: 2026-06-17
- Confidence: 低（剛開始）

## 專案是什麼（教學者參考，不是學習者已會）
- AgentFlow = Claude Code 的結構化多代理 pipeline，口號「用結構攔截幻覺，不信任任何單一 agent」。
- 8 個 phase：機械前置 → 需求(PRD-Intake) → 探索(Explorer) → 計畫+挑戰(Planner+Challenger，人工關卡) → 驗收測試先行(Spec-Tester) → 實作(Coder) → 並行驗證+smoke(Reviewer+Tester) → 銷帳歸檔(Planner)。
- 10 個角色 + 一堆 shell 腳本（new-run/check-map/lock/metrics/opt-next/opt-dedup/notify-slack）+ 自我回歸網(tests/)。

## Evidence
- 2026-06-17: 使用者已能秒懂 **MAP「路標不是證據、fail-safe」** 的設計（經一次解說後正確複述）→ MAP 概念 familiar。
- 2026-06-17: 使用者自述**已懂「不信單一 agent」前提**（見 [[llm-app-foundations]]），故此前提關卡跳過。

## Known Gaps
- 尚不熟：pipeline 8 phase 的整體流動、各角色分工、shell 腳本機械化關卡、各設計取捨（worktree 隔離、計畫是探索產物、驗收測試先行+禁改測試、申報互核、Warnings 銷帳、自我優化停人關卡）。

## Teaching Notes
- **框架**：舊版楓之谷（Big Bang 改版前），台灣用語。最大化搞笑、九成劇情一成技術錨點。
- **跳過**：通用 loop engineering 理論、不信單一 agent 前提（已懂）。聚焦**這個 repo 具體怎麼運作**。
- **鉤子**：把每關對應到使用者自己寫的 gu-log loop-engineering 文章（`sp-220-20260610-loop-engineering.mdx`）——「你文章寫的 X，在這 repo 就是 Y」。
- **節奏**：chill，一關一關來；先讀自包含 HTML 再答一題 MCQ。
- 重活（分析 repo / 出計畫）委派 Codex；orchestrator 負責 zh-tw 教學語氣與驗收。

## Next Suggested Levels
- 待 Codex 教學計畫（teaching-plan.md）產出後，依其相依排序開關；MAP 那關可加速帶過（已 familiar）。
