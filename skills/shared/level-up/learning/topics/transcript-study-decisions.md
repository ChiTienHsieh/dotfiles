# Transcript 低效研究・設計決策關（level-up 決策走廊）

## Learner Goal
- 搞懂每個設計決策的取捨後自己拍板；每拍板一關，CC 就 dispatch 對應 Codex 實作。

## Status
- mastered（決策走廊全通，MCQ 6/6，兩次主動質疑均高品質）。

## Analogy
- Vainglory・shotcaller —— 8 分析員=分路隊友、quota=資源條、marker=不 ping 隊友、對抗驗證=開團前探視野。

## 已拍板的決策（每關拍板即 dispatch，operational）
- **分支策略**：疊同分支（與 %96 共用 tree，local merge 會害到對方 —— user 主動要求跨 pane 協調）。
- **arbitrage 硬門檻**：>20 tool loop → Codex；驗收/放行是 CC 不可外包的職責。
- **marker-only 硬預設 + compaction 停損線**：只有 marker 逾時/blocked 才讀 stream。監看分三層：bash watcher（免費）< Haiku babysitter（要眼睛的等待）< controller 親看（僅 steering）。
- **deterministic helpers 三件裝**（agent-safe-read / agent-rg / agent-send-prompt）vs 再寫十條規則。保證 agent 真的用 helper 三層：內建工具不走 shell、寫進動線勝過寫規則、hook 才是強制層。
- **新 skill 分層**：description 搶觸發會稀釋 → gu-log SOP 放 gu-log repo、dotfiles 只留薄入口（自己推導出 repo-domain 分層）。
- **不碰 orca**：16GB 無風扇 + Electron 底噪 + 多工體驗；解封條件=買 mac-mini/studio 才重評。偵察報告存 ~/scratch/transcript-study-20260703/orca-eval。
- **出兵**：兩路 tmux Codex worker（dotfiles 批次 / gu-log SOP worktree 隔離）。gu-log SOP ×2 過 codex review（修 P2：deploy `--file` 不存在，ground-truth 驗出 `--active-file`）→ PR #541 CI 8/8 全綠、merge 留 user。dotfiles 尾款：arbitrage Token Guardrails、lessons.md commit mutex、gu-log skill 薄入口。

## 已掌握（概念）
- working tree 已生效 vs merge 讓未來環境繼承的區分。
- 規則會稀釋、script 把正確行為變預設路徑；追問「alias 蓋 rg 怎辦」→ 內建工具不走 shell、hook 才是強制層。
- 學習遷移能力強：主動提「Haiku subagent 監看 pane」、把新 skill 決策自己推導成 repo-domain 分層。

## 教訓
- 險案：send-keys 打進 %3 的 AskUserQuestion 對話框差點代按 → 已列入 lessons.md。

## Teaching Notes
- 90% 劇情 10% 錨點；MCQ anti-tell（位置分散、等長選項、一個純搞笑）。
- 背景脈絡：study 資料在 session scratchpad study/（findings/verify/state.md）。
- 拍板即出兵：每關決策完立即 dispatch 對應實作，不等全部關卡結束。
