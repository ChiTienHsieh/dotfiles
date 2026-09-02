@SOUL.md
@USER.md
@~/dotfiles/codex/AGENTS.md

## Terminology
- "Claude Code" 可縮寫為 "CC"。跨 agent 共用規則在 `~/dotfiles/codex/AGENTS.md`；本檔只放 Claude 專屬行為與更嚴的覆蓋，不重複共用規則。

## Proactivity
- 需要確認時直接在聊天裡列編號選項＋標推薦，不要開放式乾問；不用 AskUserQuestion（已 deny —— 選項欄位固定長度，內容被截斷看不懂）。
- 幫 user 擬訊息（Slack/Discord/email）：精簡、展現主動；用 `pbcopy` 進剪貼簿。

## `.claude/` writes — 高摩擦，整併再動
- 修改 Claude Code 設定或處理可由設定根治的摩擦前，先讀 `~/dotfiles/claude/notes/settings-friction.md`。
- 規劃與高層對齊用 `level-up` skill 的 preflight，不用 Plan Mode 的 plan file：高層決定會牽動之後一連串低層決定，一份 plan.md 記不住那份共識。
- 臨時筆記 / WIP 放 `~/scratch/`、`/tmp/` 或 repo 內 notes 資料夾，不往 `.claude/` 倒（`.claude/plans/` 是 Plan Mode 專屬）。
