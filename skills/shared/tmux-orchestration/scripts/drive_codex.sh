#!/bin/bash
# 驅動一個互動式 approve-for-me codex（在 cmux surface 裡），等它把報告寫到帶 marker 的檔案。
# 用法: drive_codex.sh SURFACE PROMPTFILE MARKER OUTFILE TIMEOUT NEWSURF
#   NEWSURF 非空 -> 開新 cmux surface 跑 codex（ref 由 new-surface 回傳）；空 -> 用既有 SURFACE。
set -o pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)" || exit 1
HISTORY_HELPER="$SCRIPT_DIR/delegation_history.sh"

resolve_launcher_workspace(){
  [ -n "${CMUX_SURFACE_ID:-}" ] || return 0
  cmux tree --all --id-format both 2>/dev/null | awk -v target="$CMUX_SURFACE_ID" '
    {
      line = $0
      sub(/^[^[:alpha:]]*/, "", line)
      split(line, fields, /[[:space:]]+/)
      if (fields[1] == "workspace" && fields[2] ~ /^workspace:[0-9]+$/) {
        workspace = fields[2]
      }
      if (fields[1] == "surface" && fields[2] ~ /^surface:[0-9]+$/) {
        if ((fields[2] == target || fields[3] == target) && workspace != "") {
          print workspace
          found = 1
          exit
        }
      }
    }
    END { if (!found) exit 1 }
  '
}

resolve_active_workspace(){
  cmux tree --all --id-format both 2>/dev/null | awk '
    /◀ active/ {
      line = $0
      sub(/^[^[:alpha:]]*/, "", line)
      split(line, fields, /[[:space:]]+/)
      if (fields[1] == "workspace" && fields[2] ~ /^workspace:[0-9]+$/) {
        print fields[2]
        found = 1
        exit
      }
    }
    END { if (!found) exit 1 }
  '
}

# Claude Code runs its Bash tool in a helper surface that can be in a
# different workspace from the visible Claude Code agent TUI. That makes
# $CMUX_SURFACE_ID alone unreliable for Claude Code controllers: resolving the
# helper surface would place delegated workers next to the helper, not next to
# the controller the user is actually watching.
resolve_target_workspace(){
  local workspace
  if [ -n "${CMUX_ORCH_WORKSPACE:-}" ]; then
    printf '%s\n' "$CMUX_ORCH_WORKSPACE"
    return 0
  fi

  workspace="$(resolve_launcher_workspace || true)"
  if [ -n "$workspace" ]; then
    printf '%s\n' "$workspace"
    return 0
  fi

  # Fallback for interactive controller sessions where the user is focused on
  # the controller workspace; this is only meaningful when the active cmux
  # workspace is the workspace intended to receive delegated workers.
  workspace="$(resolve_active_workspace || true)"
  if [ -n "$workspace" ]; then
    printf '%s\n' "$workspace"
    return 0
  fi

  if [ -n "${CMUX_WORKSPACE_ID:-}" ]; then
    printf '%s\n' "$CMUX_WORKSPACE_ID"
  fi
}

CMUX_WORKSPACE_ARGS=()

configure_workspace_args(){
  local target_workspace
  target_workspace="$(resolve_target_workspace || true)"
  CMUX_WORKSPACE_ARGS=()
  [ -n "$target_workspace" ] && CMUX_WORKSPACE_ARGS=(--workspace "$target_workspace")
}

cmux_read_screen(){
  local surface="$1"
  local lines="$2"
  cmux read-screen "${CMUX_WORKSPACE_ARGS[@]}" --surface "$surface" --lines "$lines"
}

cmux_send_surface(){
  local surface="$1"
  shift
  cmux send "${CMUX_WORKSPACE_ARGS[@]}" --surface "$surface" "$@"
}

prompt_visible(){
  local screen="$1"
  local prompt="$2"
  local out_path="$3"
  local marker="$4"
  printf '%s\n' "$screen" | grep -Fq "$prompt" && return 0
  printf '%s\n' "$screen" | grep -Fq "Read $PF_ABS" \
    && printf '%s\n' "$screen" | grep -Fq "$out_path" \
    && printf '%s\n' "$screen" | grep -Fq "$marker"
}

wait_ready(){
  local surface="$1"
  local trust_enters=0
  local screen
  for i in $(seq 1 45); do
    screen="$(cmux_read_screen "$surface" 40 2>/dev/null || true)"
    printf '%s\n' "$screen" | grep -qE "OpenAI Codex|gpt-5|Approve for me|esc to interrupt" && return 0
    if [ "$trust_enters" -lt 2 ] && printf '%s\n' "$screen" | grep -qiE "Do you trust|Press enter to continue"; then
      cmux_send_surface "$surface" "\n" >/dev/null 2>&1 || true
      trust_enters=$((trust_enters + 1))
    fi
    sleep 1
  done
  return 1
}

main(){
  SURF="$1"; PF="$2"; MARK="$3"; OUT="$4"; TO="${5:-420}"; NEWSURF="$6"
  [ -f "$PF" ] || { echo "prompt file 不存在: $PF"; exit 1; }
  mkdir -p "$(dirname "$OUT")" || exit 1
  PF_DIR="$(cd "$(dirname "$PF")" && pwd -P)" || exit 1
  OUT_DIR="$(cd "$(dirname "$OUT")" && pwd -P)" || exit 1
  PF_ABS="$PF_DIR/$(basename "$PF")"
  OUT_ABS="$OUT_DIR/$(basename "$OUT")"

  configure_workspace_args

  if [ -n "$NEWSURF" ]; then
    SURF=$(cmux new-surface --type terminal --no-focus "${CMUX_WORKSPACE_ARGS[@]}" 2>/dev/null | grep -oE 'surface:[0-9]+' | head -1)
    [ -z "$SURF" ] && { echo "new-surface 失敗"; exit 1; }
    echo "[new] codex surface = $SURF"
    cmux_send_surface "$SURF" "codex\n"
    wait_ready "$SURF" || { echo "[$SURF] codex 沒起來"; exit 1; }
    sleep 2
  fi

  if [ -x "$HISTORY_HELPER" ]; then
    HISTORY_FILE="$("$HISTORY_HELPER" record "$SURF" "$PF_ABS" "$MARK" "$OUT_ABS" "drive_codex")"
    echo "[history] $HISTORY_FILE"
  else
    echo "[history] helper not executable: $HISTORY_HELPER"
  fi

  # 送單行 prompt（不含換行避免提早送出），確認在輸入框後再單獨送 Enter
  PROMPT_TEXT="Read $PF_ABS and follow it exactly. Write the report to $OUT_ABS and end the file with a line containing only $MARK."
  cmux_send_surface "$SURF" -- "$PROMPT_TEXT"
  sleep 0.6
  SCREEN="$(cmux_read_screen "$SURF" 40 2>/dev/null || true)"
  if ! prompt_visible "$SCREEN" "$PROMPT_TEXT" "$OUT_ABS" "$MARK"; then
    cmux_send_surface "$SURF" -- "$PROMPT_TEXT"
    sleep 0.6
    SCREEN="$(cmux_read_screen "$SURF" 40 2>/dev/null || true)"
    if ! prompt_visible "$SCREEN" "$PROMPT_TEXT" "$OUT_ABS" "$MARK"; then
      echo "[$SURF] prompt 未出現在輸入框，停止送出" >&2
      echo "----- surface tail -----" >&2
      printf '%s\n' "$SCREEN" >&2
      exit 1
    fi
  fi
  cmux_send_surface "$SURF" "\n"

  LAST_SCREEN=""
  start=$SECONDS
  while [ $((SECONDS-start)) -lt "$TO" ]; do
    if [ -f "$OUT" ] && [ "$(tail -n 1 "$OUT" 2>/dev/null)" = "$MARK" ]; then
      echo "[$SURF] DONE (marker=$MARK)"
      echo "----- $OUT -----"; tail -45 "$OUT"
      exit 0
    fi
    LAST_SCREEN="$(cmux_read_screen "$SURF" 25 2>/dev/null || true)"
    sleep 5
  done
  if [ ! -f "$OUT" ]; then
    echo "[$SURF] TIMEOUT ${TO}s — OUTFILE 不存在: $OUT"
  else
    echo "[$SURF] TIMEOUT ${TO}s — OUTFILE 存在但 marker 不在最後一行: $OUT"
  fi
  echo "----- last surface tail -----"
  if [ -n "$LAST_SCREEN" ]; then
    printf '%s\n' "$LAST_SCREEN"
  else
    cmux_read_screen "$SURF" 25 2>/dev/null || true
  fi
  exit 2
}

if [ "${BASH_SOURCE[0]}" = "$0" ]; then
  main "$@"
fi
