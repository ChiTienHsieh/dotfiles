# Grok

只有目前 human 指令明確要求改名，才可執行 `scripts/rename-session.sh "<title>"` 操作 tmux；否則只提供建議標題。

- Grok 支援 `/rename`（別名 `/title`）。
- 非 tmux 時 script 會印出建議標題並以 exit 1 結束，由使用者用 `/rename` 套用。
