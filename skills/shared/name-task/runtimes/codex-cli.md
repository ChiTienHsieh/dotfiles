# Codex CLI（TUI）

只有目前 human 指令明確要求改名，才可執行 `scripts/rename-session.sh "<title>"` 操作 tmux；否則只提供建議標題。

- Script 會自動偵測 Codex TUI 並處理多行輸入的雙 Enter 提交。
- tmux 指令在 Codex 權限模型下會觸發 Guardian 審批（scoped escalation）。
- 非 tmux 時 script 會印出建議標題並 exit 1，由使用者手動 `/rename`。
