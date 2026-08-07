# tmux Guardian guardrail debrief

## Learner Goal
- 確認 2026-07-29 完成的 tmux Guardian guardrail 決策合理，能在 push 前判斷主要取捨與殘餘邊界。

## Current Level
- Status: learning
- Last updated: 2026-08-07
- Confidence: 待逐關驗證

## Evidence
- 2026-07-30: 選擇 Vainglory 類比、紮實打底、Chat Markdown。
- 2026-07-30: 初步選擇所有明示 tmux command 都經 Guardian，但要求進一步釐清「只審 mutating subcommand」為何主要依賴 agent 自律。
- 2026-08-07: 在 tmux worker lifecycle debrief 中，維持「hook 只記帳、提醒與擋一次；實際 cleanup 仍逐一經 Guardian」的設計，明確不採自動 kill 或純文字規則。

## Known Gaps
- 尚未完全理解：socket permission 只能決定能否連線，不能限制連線後只能使用 read-only tmux subcommand。
- 待驗證能否區分 sandbox socket hard boundary、execpolicy prompt、wrapper bypass 與 transitive child-process 邊界。

## Teaching Notes
- Use these examples: Vainglory shotcaller、進場 call、隊長放行與技能連鎖效果。
- Avoid assuming: prefix rule 能攔截已核准程式內部的任意 child process。

## Next Suggested Levels
- 重演「所有 read-only tmux 也要 Guardian」的決策。
- 判斷 socket allowlist 與 execpolicy 各自負責哪一層。
- 驗證 `uv run` wrapper bypass 與 A-scope 邊界。
