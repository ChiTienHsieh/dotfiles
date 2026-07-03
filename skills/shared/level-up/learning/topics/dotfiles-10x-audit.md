# Dotfiles 10x 審計補進度（level-up 敘事回放）

## Learner Goal
- 純娛樂追劇式補進度：知道發生什麼、哪些很酷、清了什麼。選 depth 3 是信任教學者「能把深知識講得好玩」。
- 結尾兩個實戰關：設計決策拍板（craft-goal/nvim-tutor/codex-bin-ssh/hatch-pet/playwright-cli/html* 融合）+ branch 合回 main。

## Analogy
- A3：楓之谷・倉庫大掃除（永久存檔不重置 → dotfiles）。單一世界觀一路扛到底，不混 Vainglory。

## Current Level
- Status: learning — L1-L3 通關，L4 的 MCQ 已出題**尚未作答**（marker file vs 盯畫面）。重開機後從「收 L4 答案」續跑。
- Last updated: 2026-07-03（user 重開機前 wrap）
- Confidence: 高（3/3 一次過，且能自行延伸洞見）

## Resume Point（重開機後讀這裡）
- 下一步：收 L4 MCQ 答案（正解=「畫面安靜≠完工，marker 檔才是主動完工宣告」，位置 B）→ L5 詐騙招牌整頓。
- 三份 Codex 分析報告已從 /tmp 搶救到 ~/dotfiles/output/audit-2026-07-03/session2-analysis/（html-fusion 判決 SEPARATE；trim-sweep 省 372-493 行 top5；instructions-diet 已完成待讀）。舊審計全紀錄在同 dir 的 audit-main/。
- L7 議程：4 個 ask_user + playwright-cli 手動移除 + html* 融合判決 + trim 清單 + instructions-diet + %104 的兩條規則候選 + 技能圖鑑。L8 = merge main 方式。
- 跨 session HOLD 清單與 %104 分工見 Teaching Notes。

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
- user 對紀錄格式的回饋：不要記選項字母（如「答 C」），記「答對了什麼概念」；MCQ 位置輪替另外用 Teaching Notes 一行追蹤。

## Teaching Notes
- 90% 劇情 10% 技術錨點；MCQ 遵守 anti-tell（位置分散、長度一致、一個純搞笑選項）。
- MCQ 正解位置紀錄（僅供輪替用）：L1=C, L2=D, L3=A
- 跨 session 協調：pane %104（另一個 orchestrator CC，同 tree 同分支）負責 skills/*+codex/notes；%96 負責 always-loaded。HOLD 清單（等 user L7 拍板才解鎖給 %104）：html-artifacts、html-explainer、craft-goal、nvim-tutor、hatch-pet、arbitrage、daily-loop/SKILL.md、一切 skill 本文瘦身。commit 前互相 send-keys 錯開。推 main = user 保留。
- 背景並行：Codex read-only 分析 html* 融合 + 全 skill trim-lens，報告餵 L7。
