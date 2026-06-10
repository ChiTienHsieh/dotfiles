#!/bin/bash
# 驅動一個互動式 approve-for-me codex（在 cmux surface 裡），等它把報告寫到帶 marker 的檔案。
# 用法: drive_codex.sh SURFACE PROMPTFILE MARKER OUTFILE TIMEOUT NEWSURF
#   NEWSURF 非空 -> 開新 cmux surface 跑 codex（ref 由 new-surface 回傳）；空 -> 用既有 SURFACE。
set -o pipefail
SURF="$1"; PF="$2"; MARK="$3"; OUT="$4"; TO="${5:-420}"; NEWSURF="$6"
mkdir -p "$(dirname "$OUT")" || exit 1
PF_DIR="$(cd "$(dirname "$PF")" && pwd -P)" || exit 1
OUT_DIR="$(cd "$(dirname "$OUT")" && pwd -P)" || exit 1
PF_ABS="$PF_DIR/$(basename "$PF")"
OUT_ABS="$OUT_DIR/$(basename "$OUT")"

wait_ready(){ for i in $(seq 1 45); do
  cmux read-screen --surface "$1" --lines 40 2>/dev/null | grep -qE "OpenAI Codex|gpt-5|Approve for me|esc to interrupt" && return 0
  sleep 1; done; return 1; }

if [ -n "$NEWSURF" ]; then
  SURF=$(cmux new-surface --type terminal --no-focus 2>/dev/null | grep -oE 'surface:[0-9]+' | head -1)
  [ -z "$SURF" ] && { echo "new-surface 失敗"; exit 1; }
  echo "[new] codex surface = $SURF"
  cmux send --surface "$SURF" "codex\n"
  wait_ready "$SURF" || { echo "[$SURF] codex 沒起來"; exit 1; }
  sleep 2
fi

# 送單行 prompt（不含換行避免提早送出），再單獨送 Enter
cmux send --surface "$SURF" -- "Read $PF_ABS and follow it exactly. Write the report to $OUT_ABS and end the file with a line containing only $MARK."
sleep 0.6
cmux send --surface "$SURF" "\n"

start=$SECONDS
while [ $((SECONDS-start)) -lt "$TO" ]; do
  if [ -f "$OUT" ] && [ "$(tail -n 1 "$OUT" 2>/dev/null)" = "$MARK" ]; then
    echo "[$SURF] DONE (marker=$MARK)"
    echo "----- $OUT -----"; tail -45 "$OUT"
    exit 0
  fi
  sleep 5
done
echo "[$SURF] TIMEOUT ${TO}s — 可能卡在 approve 或還在跑，需人工看一眼"
echo "----- surface tail -----"
cmux read-screen --surface "$SURF" --lines 25 2>/dev/null
exit 2
