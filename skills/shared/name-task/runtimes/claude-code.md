# Claude Code

執行 `scripts/rename-session.sh "<title>"`。

- 自己的 pane 送 `/rename` 視同使用者明確要求，不違反 tmux 預設唯讀規則。
- 非 tmux 時 script 會印出建議標題並以 exit 1 結束，由使用者用 `/rename` 套用。
