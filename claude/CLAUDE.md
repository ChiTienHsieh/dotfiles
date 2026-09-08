@SOUL.md
@USER.md
@~/dotfiles/agents/AGENTS.md

## Terminology
- "Claude Code" 可縮寫為 "CC"。跨 agent 共用規則在 `~/dotfiles/agents/AGENTS.md`；本檔只放 Claude 專屬行為與更嚴的覆蓋，不重複共用規則。

## Proactivity
- 幫 user 擬訊息（Slack/Discord/email）：精簡、展現主動；用 `pbcopy` 進剪貼簿。

## `.claude/` writes — 高摩擦，整併再動
- 修改 Claude Code 設定或處理可由設定根治的摩擦前，先讀 `~/dotfiles/claude/notes/settings-friction.md`。
- 使用者要求逐關理解或以 preflight 共同決策時，用 `level-up`；一般實作規劃不啟動教學流程。
- 臨時筆記 / WIP 放 `~/scratch/`、`/tmp/` 或 repo 內 notes 資料夾，不往 `.claude/` 倒（`.claude/plans/` 是 Plan Mode 專屬）。
