#!/bin/bash
# rename-session.sh — 在自己的 tmux pane 套用單行 /rename
# 用法：rename-session.sh "<title>"
set -euo pipefail

TITLE="${1:?Usage: rename-session.sh '<title>'}"
if [[ "$TITLE" =~ [[:cntrl:]] ]]; then
  printf 'Title must be a single line without control characters.\n' >&2
  exit 1
fi

if [ -z "${TMUX_PANE:-}" ]; then
  printf 'Not in tmux. Apply manually:\n  /rename %s\n' "$TITLE"
  exit 1
fi
if [[ ! "$TMUX_PANE" =~ ^%[0-9]+$ ]]; then
  printf 'TMUX_PANE must be an exact pane ID (%%number).\n' >&2
  exit 1
fi

# 先確認自己的 pane 仍存在；literal 模式保留標題中的按鍵名稱與標點。
PANE_CMD=$(tmux display-message -t "$TMUX_PANE" -p '#{pane_current_command}')
tmux send-keys -t "$TMUX_PANE" -l "/rename $TITLE" \; send-keys -t "$TMUX_PANE" Enter

# 保留 Codex TUI 多行輸入模式所需的第二次 Enter。
case "$PANE_CMD" in
  codex*) tmux send-keys -t "$TMUX_PANE" Enter ;;
esac
