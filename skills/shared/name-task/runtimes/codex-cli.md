# Codex CLI（TUI）

執行 `scripts/rename-session.sh "<title>"`。

- Script 會偵測 Codex TUI，補上多行輸入模式需要的第二次 Enter。
- tmux 指令在 Codex 權限模型下走 scoped escalation（Guardian 審批）。
- 非 tmux 時印出手動指令並以 exit 1 結束，表示尚未套用。
