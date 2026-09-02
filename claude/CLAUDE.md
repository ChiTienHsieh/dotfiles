@SOUL.md
@USER.md
@~/dotfiles/codex/AGENTS.md

## Terminology
- "Claude Code" 可縮寫為 "CC"。跨 agent 共用規則在 `~/dotfiles/codex/AGENTS.md`；本檔只放 Claude 專屬行為與更嚴的覆蓋，不重複共用規則。

## Claude-specific language overrides
- **ALWAYS reply in Traditional Chinese (zh-tw).** 不跟隨 user 的語言 —— user 打英文是為了快，英文訊息 ≠ 英文回覆。
- 遇到不確定能否直接用英文的詞，`grep -i "word" ~/dotfiles/hooks/jargon-allowlist.yml` 查它的分級，不必讀全檔。User 抱怨某詞時立即移到 reject；升級詞彙前先問 user。

## File deletion — PREFER `trash` OVER `rm`
- 刪除一般檔案或目錄優先用 `trash`。
- 只有 shell script、CI、本來就短命的 `/tmp`/build 產物、或 user 明確要硬刪時才用 `rm` / `rm -rf`。

## Proactivity
- 需要確認時直接在聊天裡列編號選項＋標推薦，不要開放式乾問；不用 AskUserQuestion（已 deny —— 選項欄位固定長度，內容被截斷看不懂）。
- 幫 user 擬訊息（Slack/Discord/email）：精簡、展現主動；用 `pbcopy` 進剪貼簿。

## `.claude/` writes — 高摩擦，整併再動
- 修改 Claude Code 設定或處理可由設定根治的摩擦前，先讀 `~/dotfiles/claude/notes/settings-friction.md`。
- **絕不寫 plan file 到 `.claude/plans/`**（Plan Mode 專屬路徑）。臨時筆記 / WIP → `~/scratch/`、`/tmp/` 或 repo 內 notes 資料夾，不往 `.claude/` 倒。
