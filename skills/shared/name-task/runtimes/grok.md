# Grok

執行 `scripts/rename-session.sh "<title>"`，script 會透過 `tmux send-keys` 對自己的 `$TMUX_PANE` 套用標題。

- 依 `codex/AGENTS.md` 的持續授權，一次呼叫即可，不必逐次確認或由使用者重打；只涵蓋自己的單行 `/rename`。
- 非 tmux 時印出手動指令並以 exit 1 結束，表示尚未套用。

Grok 支援 `/rename`（別名 `/title`）。
