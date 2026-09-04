# Codex CLI

執行 `scripts/rename-session.sh "<title>"`。tmux 指令在 Codex 的權限模型下需要 Guardian scoped escalation。

- TUI 的多行輸入需要在 script 執行後額外送一次 Enter：
  `tmux send-keys -t "$TMUX_PANE" Enter`
- 非 tmux 時 script 會印出建議標題並以 exit 1 結束，由使用者用 `/rename` 套用。
