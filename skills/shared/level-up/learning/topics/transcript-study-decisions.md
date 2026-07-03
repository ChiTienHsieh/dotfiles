# Transcript 低效研究・設計決策關（level-up 決策走廊）

## Learner Goal
- 搞懂每個設計決策的取捨後自己拍板；每拍板一關，CC 就 dispatch 對應 Codex 實作。A2（Vainglory 開黑指揮官、紮實打底）。

## Analogy
- A：Vainglory・shotcaller — 8 分析員=分路隊友、quota=資源條、marker=不 ping 隊友、對抗驗證=開團前探視野。單一世界觀扛到底。

## Current Level
- Status: learning
- Last updated: 2026-07-03
- Confidence: n/a（剛開課）

## Level Map（每關 = 一個拍板點）
- L1 把 build 寫回公會攻略 — 分支策略（merge main vs 疊分支 vs 不 commit）
- L2 資源讓給後期核心 — arbitrage 硬門檻（>20 tool loop → Codex）
- L3 別一直 ping 隊友 — marker-only 硬預設 + compaction 停損線
- L4 出裝取代嘴砲 — deterministic helpers（agent-safe-read / agent-rg / drive_codex 加固）vs 再寫十條規則
- L5 要不要練新英雄 — 新 skill 候選（gu-log SP pipeline / backlog-sweep / guardrail-review-gate）
- L6 BOSS：出兵 — dispatch Codex workers → commit → codex review → push

## Evidence
- （待補：MCQ + 拍板結果）

## Teaching Notes
- 90% 劇情 10% 錨點；MCQ anti-tell（位置分散、等長選項、一個純搞笑）。
- 背景脈絡：study 資料在 session scratchpad study/（findings-1..8、verify-1..8、state.md）。
- 拍板即出兵：每關決策完立即 dispatch 對應實作，不等全部關卡結束。
