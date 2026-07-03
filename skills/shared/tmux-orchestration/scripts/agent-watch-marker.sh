#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: agent-watch-marker.sh REPORT_PATH [MARKER] [--timeout SECS] [--interval SECS]" >&2
}

[ "$#" -ge 1 ] || { usage; exit 2; }

report_path="$1"
shift
marker=""
timeout=0
interval=""

if [ "$#" -gt 0 ] && [ "${1#--}" = "$1" ]; then
  marker="$1"
  shift
fi

while [ "$#" -gt 0 ]; do
  case "$1" in
    --timeout) timeout="${2:?}"; shift 2 ;;
    --interval) interval="${2:?}"; shift 2 ;;
    *) echo "Unknown option: $1" >&2; usage; exit 2 ;;
  esac
done

start=$SECONDS
current_interval="${interval:-5}"
file_seen=0

while :; do
  if [ -f "$report_path" ]; then
    file_seen=1
    if [ -z "$marker" ] || [ "$(tail -n 1 "$report_path" 2>/dev/null || true)" = "$marker" ]; then
      echo "DONE"
      exit 0
    fi
  fi

  if [ "$timeout" -gt 0 ] && [ $((SECONDS - start)) -ge "$timeout" ]; then
    if [ "$file_seen" -eq 1 ]; then
      echo "TIMEOUT_NO_MARKER"
    else
      echo "TIMEOUT_NO_FILE"
    fi
    exit 1
  fi

  sleep "$current_interval"
  if [ -z "$interval" ]; then
    case "$current_interval" in
      5) current_interval=15 ;;
      15) current_interval=45 ;;
      45) current_interval=60 ;;
    esac
  fi
done
