# Dotfiles 10x 審計補進度（level-up 敘事回放）

## Learner Goal
- 純娛樂追劇式補進度：知道發生什麼、哪些很酷、清了什麼。選 depth 3 是信任教學者「能把深知識講得好玩」。
- 結尾兩個實戰關：設計決策拍板 + branch 合回 main。
- user 自陳核心痛點：skill 太多、不知道自己有什麼（discoverability）。

## Analogy
- 楓之谷・倉庫大掃除（永久存檔不重置 → dotfiles）。單一世界觀扛到底，不混 Vainglory。

## Status
- mastered — 全通關。PR #1 已 merge 進 main（3c5daa6，merge commit 保留 15 筆故事線）。全程能自行延伸洞見。

## Resume Point（operational）
- main HEAD=3c5daa6；PR https://github.com/ChiTienHsieh/dotfiles/pull/1。
- 未清尾巴（非 blocking）：user 手動移除 playwright-cli plugin（/plugin UI）；output/audit-2026-07-03/ 是 gitignored 工作區可保留當 audit trail。
- Codex 分析報告在 ~/dotfiles/output/audit-2026-07-03/session2-analysis/；舊審計全紀錄在同 dir 的 audit-main/。

## 已掌握 / 誤解修正
- oracle ≠ arbitrage：oracle=找第二個 frontier model 要意見（顧問）；arbitrage=Claude 出判斷、Codex 出勞力的派工規則（工頭）。
- dangling symlink 成因（ln -sf 不驗證 target）。
- 過期 skill 內容會把 AI 引到錯的路上（stale guidance = 主動破壞，不只死重）。
- seed-if-missing：範本只在 live 不存在時發放。
- marker file 是「訊號正確性」不是「成本考量」；暗號行證明報告完整寫完，檔案存在 ≠ 寫完。自行推出：capture-pane 是靜態快照、agent 看不到動畫，agent 與人類在 liveness 訊號上有資訊差，這是 agent 需要 marker 而人類不用的根本原因。
- persona skill 掛 disable-model-invocation 的理由 = 開戲的決定權屬於 user，模型代開永遠是打擾。
- simplify 審查視角 = 規則庫的反向壓力，防規則只增不減。主動提案 pre-commit secret-scan hook（deterministic gate 補足語意 review）。

## L7 決策全數拍板並施工（operational）
- craft-goal 升級成 CC/Codex 雙向（依任務性質+quota 選接棒者）。
- nvim-tutor + 進度檔；hatch-pet 退役進垃圾桶（pets 素材留）。
- codex/bin/ssh 改名 clawd-ssh 解 PATH 遮蔽。
- pre-commit 裝 gitleaks 秘密掃描（實彈測過）。
- trim 8 skills −227 行（Codex 打手 + CC 驗收）。
- instructions-diet 激進版 371→154 行（教學框架移到 level-up learning/user-profile.md）。
- html duo 判決 SEPARATE（user 上完迷你課親自下判決）＋改字彙根治品名搶字眼（Research synthesis / Diff review walkthrough，explainer 一詞專屬 html-explainer）。詳見 topics/html-duo.md。

## Teaching Notes
- 90% 劇情 10% 技術錨點；MCQ 遵守 anti-tell（位置分散、長度一致、一個純搞笑選項）。
- user 回饋：不要記選項字母，記「答對了什麼概念」。
