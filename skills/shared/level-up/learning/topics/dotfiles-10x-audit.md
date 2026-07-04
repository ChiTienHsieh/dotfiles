# Dotfiles 10x 審計補進度（level-up 敘事回放）

## Learner Goal
- 純娛樂追劇式補進度：知道發生什麼、哪些很酷、清了什麼。選 depth 3 是信任教學者「能把深知識講得好玩」。
- 結尾兩個實戰關：設計決策拍板（craft-goal/nvim-tutor/codex-bin-ssh/hatch-pet/playwright-cli/html* 融合）+ branch 合回 main。

## Analogy
- A3：楓之谷・倉庫大掃除（永久存檔不重置 → dotfiles）。單一世界觀一路扛到底，不混 Vainglory。

## Current Level
- Status: mastered — L1-L8 全通關。PR #1 已 merge 進 main（3c5daa6，merge commit 保留 15 筆故事線）。
- Last updated: 2026-07-04
- Confidence: 高（6/7 一次過 + L4 補考過，全程能自行延伸洞見）

## Resume Point
- 課程完結。若 user 想回顧：main HEAD=3c5daa6；PR https://github.com/ChiTienHsieh/dotfiles/pull/1。
- 未清尾巴（非 blocking）：user 手動移除 playwright-cli plugin（/plugin UI）；output/audit-2026-07-03/ 是 gitignored 工作區可保留當 audit trail。
- 三份 Codex 分析報告在 ~/dotfiles/output/audit-2026-07-03/session2-analysis/；舊審計全紀錄在同 dir 的 audit-main/。

## Level Map
- L1 十小時的裸裝時代 — ~/.claude/skills 斷鏈 + symlink 深知識（dangling link 成因）
- L2 背包大爆倉 — 刪 33k 行：plugin-dev 快照、死 agent、shims
- L3 舊存檔覆蓋危機 — seed vs live clobber、seed-if-missing、install.sh 防呆
- L4 雇打手代練 — Codex tmux 委派合約、marker、cushion、quota governor 慢燒
- L5 詐騙招牌整頓 — trigger descriptions 修理 + tmux-orchestration 三合一
- L6 守門人 — codex review gate（安全+simplify）
- L7 決策關 — 4 個 ask_user + playwright-cli + html* 融合（背景 Codex 分析回報）
- L8 BOSS — merge skill/effective-html-explainer → main

## Evidence
- 2026-07-03: 誤解修正 — user 以為 oracle ≈ arbitrage。已澄清：oracle = 找第二個 frontier model 要意見（顧問）；arbitrage = Claude 出判斷、Codex 出勞力的派工規則（工頭）。
- user 自陳核心痛點：skill 太多、不知道自己有什麼（discoverability）→ L7 加「技能圖鑑」總覽。
- 2026-07-03 L1 ✅：答對 dangling symlink 成因（ln -sf 不驗證 target），一次過。
- 2026-07-03 L2 ✅：答對 plugin 快照撞名雙載題，且自己延伸出正確洞見：過期 skill 內容會把 AI 引到錯的路上（stale guidance = 主動破壞，不只是死重）。
- 2026-07-03 user 提案：效法「smart model 少吃指令」思路，大幅精簡 always-loaded 的 CLAUDE.md/AGENTS.md → 已派 Codex 分析（instructions-diet），L7 一併拍板。
- 2026-07-03 L3 ✅：答對 seed-if-missing 概念（範本只在 live 不存在時發放），一次過。中途經歷兩輪 %104 跨 agent 協調插播仍接得回來。
- 2026-07-03 L4 ❌（第一次失手）：marker file 題選了「省 quota」— 被本關的慢燒主題帶走，把「訊號正確性」誤讀成「成本考量」。已換角度重教（畫面靜止的四種狀態不可分辨），補一題「暗號行 vs 檔案存在」檢核中。
- 2026-07-03 L4 補考 ✅：答對「暗號行證明報告完整寫完，檔案存在≠寫完」。並自行提出高品質洞見：capture-pane 是靜態快照，agent 看不到動畫；人類看 Codex TUI 的 spinner 動畫就能判斷還在不在跑 — 正確指出 agent 與人類在「liveness 訊號」上的資訊差，這正是 agent 需要 marker 而人類不用的根本原因。L4 判 mastered。
- 2026-07-03 L5 ✅：答對「persona skill 掛 disable-model-invocation 的理由 = 開戲的決定權屬於 user，模型代開永遠是打擾」，一次過。
- 2026-07-03 L6 ✅：答對「simplify 審查視角 = 規則庫的反向壓力，防規則只增不減」，一次過。並主動提案 pre-commit secret-scan hook（deterministic gate 補足語意 review）— 好直覺，排入 L7。
- user 對紀錄格式的回饋：不要記選項字母（如「答 C」），記「答對了什麼概念」；MCQ 位置輪替另外用 Teaching Notes 一行追蹤。
- 2026-07-04 L7 ✅ 決策全數拍板並施工：craft-goal 升級成 CC/Codex 雙向（依任務性質+quota 選接棒者）；nvim-tutor+進度檔、hatch-pet 退役進垃圾桶（pets 素材留）；codex/bin/ssh 改名 clawd-ssh 解 PATH 遮蔽；pre-commit 裝 gitleaks 秘密掃描（實彈測過）；trim 8 skills -227 行（Codex 打手+CC 驗收）；instructions-diet 激進版 371→154 行（教學框架移到 level-up learning/user-profile.md）；html duo 判決 SEPARATE（user 上完 3 關迷你課親自下判決）＋改字彙根治品名搶字眼（Research synthesis / Diff review walkthrough，explainer 一詞專屬 html-explainer）。
- 2026-07-04 html-duo 迷你課：user 3 關全通，展現能用自己的話重構「work artifact vs 教學配方」分界（詳見 topics/html-duo.md，教學 CC 記錄）。

## Teaching Notes
- 90% 劇情 10% 技術錨點；MCQ 遵守 anti-tell（位置分散、長度一致、一個純搞笑選項）。
- MCQ 正解位置紀錄（僅供輪替用）：L1=C, L2=D, L3=A, L4=B(未答中,選C), L4補=D, L5=B, L6=A
- 跨 session 協調：pane %104（另一個 orchestrator CC，同 tree 同分支）負責 skills/*+codex/notes；%96 負責 always-loaded。HOLD 清單（等 user L7 拍板才解鎖給 %104）：html-artifacts、html-explainer、craft-goal、nvim-tutor、hatch-pet、arbitrage、daily-loop/SKILL.md、一切 skill 本文瘦身。commit 前互相 send-keys 錯開。推 main = user 保留。
- 背景並行：Codex read-only 分析 html* 融合 + 全 skill trim-lens，報告餵 L7。
