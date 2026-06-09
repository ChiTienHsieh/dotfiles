#!/bin/bash
# 驅動一個互動式 approve-for-me codex（在 tmux 裡），等它把報告寫到帶 marker 的檔案。
# 用法: drive_codex.sh TARGET PROMPTFILE MARKER OUTFILE TIMEOUT NEWWIN
#   NEWWIN 非空 -> 開新 window 跑 codex；空 -> 用既有 TARGET pane。
set -o pipefail
SESS=cc-cdx-pit
TARGET="$1"; PF="$2"; MARK="$3"; OUT="$4"; TO="${5:-420}"; NEWWIN="$6"

wait_ready(){ for i in $(seq 1 45); do
  tmux capture-pane -p -t "$1" 2>/dev/null | grep -qE "OpenAI Codex|gpt-5|to change|Approve for me|esc to interrupt" && return 0
  sleep 1; done; return 1; }

if [ -n "$NEWWIN" ]; then
  tmux new-window -t "$SESS" -n "$NEWWIN" -c "$HOME" || { echo "[$NEWWIN] new-window 失敗"; exit 1; }
  TARGET="$SESS:$NEWWIN"
  tmux send-keys -t "$TARGET" "codex" Enter
  wait_ready "$TARGET" || { echo "[$NEWWIN] codex 沒起來"; exit 1; }
  sleep 2
fi

tmux send-keys -t "$TARGET" -l "$(cat "$PF")"
sleep 0.6
tmux send-keys -t "$TARGET" Enter

start=$SECONDS
while [ $((SECONDS-start)) -lt "$TO" ]; do
  if [ -f "$OUT" ] && grep -q "$MARK" "$OUT" 2>/dev/null; then
    echo "[$TARGET] DONE (marker=$MARK)"
    echo "----- $OUT -----"; tail -45 "$OUT"
    exit 0
  fi
  sleep 5
done
echo "[$TARGET] TIMEOUT ${TO}s — 可能卡在 approve 或還在跑，需人工看一眼"
echo "----- pane tail -----"
tmux capture-pane -p -t "$TARGET" 2>/dev/null | sed 's/[[:space:]]*$//' | grep -v '^$' | tail -25
exit 2
