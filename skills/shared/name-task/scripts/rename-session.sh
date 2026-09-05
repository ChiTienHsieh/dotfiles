#!/bin/bash
# rename-session.sh — 透過 tmux /rename 為目前 agent session 改名
# 用法：rename-session.sh "<title>"
#
# 需要 $TMUX_PANE。若不在 tmux 內，印出建議標題並以 exit 1
# 讓呼叫端知道要顯示給使用者。
set -euo pipefail

TITLE="${1:?Usage: rename-session.sh '<title>'}"

if [ -z "${TMUX_PANE:-}" ]; then
  printf 'Not in tmux. Apply manually:\n  /rename %s\n' "$TITLE"
  exit 1
fi

tmux send-keys -t "$TMUX_PANE" "/rename $TITLE" Enter

# Codex TUI 的多行輸入模式需要第二次 Enter 才提交
PANE_CMD=$(tmux display-message -t "$TMUX_PANE" -p '#{pane_current_command}')
case "$PANE_CMD" in
  codex*) tmux send-keys -t "$TMUX_PANE" Enter ;;
esac
