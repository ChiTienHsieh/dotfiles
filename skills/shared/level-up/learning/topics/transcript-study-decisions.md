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
- 2026-07-03 L1: MCQ 答 C 正確（working tree 已生效 vs merge 讓未來環境繼承的區分）。拍板=疊同分支（因與 %96 共用 tree，local merge 會害到對方 — user 主動要求跨 pane 協調，指揮意識好）。
- 2026-07-03 L2: MCQ 答 A 正確（驗收/放行 = CC 不可外包職責）。拍板=照推薦寫 Guardrails（>20 tool loop 門檻）。
- 2026-07-04 L3: MCQ 答 B 正確（只有 marker 逾時/blocked 才讀 stream）。並主動提出「用 Haiku subagent 監看 pane」— 方向對（隔離污染），經討論細化成三層：bash watcher（免費）< Haiku babysitter（要眼睛的等待）< controller 親看（僅 steering）。學習遷移能力強。
- 2026-07-04 L4: MCQ 答 A 正確（規則會稀釋、script 把正確行為變預設路徑）。追問「怎麼保證 agent 真的用 helper？alias 蓋 rg？」— 高品質質疑，答案三層：內建工具不走 shell、寫進動線勝過寫規則、hook 才是強制層。拍板=三件裝+drive_codex 強化（hook 另案）。
- 2026-07-04 L5: MCQ 答 B 正確（description 搶觸發稀釋），且直接應用到分層決策：gu-log SOP 放 gu-log repo、dotfiles 只留薄入口 — 自己推導出 repo-domain 分層，mastered 級表現。
- 2026-07-04 L5.5: 拍板不碰 orca — 理由自己給得精準（16GB 無風扇 + Electron 底噪 + 多工體驗），並設了解封條件（買 mac-mini/studio 才重評）。orca 偵察報告存 ~/scratch/transcript-study-20260703/orca-eval。
- 2026-07-04 L6: 出兵。兩路 tmux Codex worker（dotfiles 批次 / gu-log SOP worktree 隔離）；arbitrage 續 HOLD（%3 的 user L7 拍板前不動）。險案教訓：send-keys 打進 %3 的 AskUserQuestion 對話框差點代按 — 已列入 lessons.md 出貨清單。

## Teaching Notes
- 90% 劇情 10% 錨點；MCQ anti-tell（位置分散、等長選項、一個純搞笑）。
- 背景脈絡：study 資料在 session scratchpad study/（findings-1..8、verify-1..8、state.md）。
- 拍板即出兵：每關決策完立即 dispatch 對應實作，不等全部關卡結束。
