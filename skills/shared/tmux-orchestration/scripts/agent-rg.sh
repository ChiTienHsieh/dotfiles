#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: agent-rg.sh PATTERN [PATH...] [--files] [--sample N] [--full REASON]" >&2
}

mode=count
sample=""
full_reason=""
args=()

while [ "$#" -gt 0 ]; do
  case "$1" in
    --files) mode=files; shift ;;
    --sample) mode=sample; sample="${2:?}"; shift 2 ;;
    --full) mode=full; full_reason="${2:?}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) args+=("$1"); shift ;;
  esac
done

[ "${#args[@]}" -ge 1 ] || { usage; exit 2; }

case "$mode" in
  count) rg --count-matches "${args[@]}" ;;
  files) rg --files-with-matches "${args[@]}" ;;
  sample) rg -m "$sample" "${args[@]}" ;;
  full)
    [ -n "$full_reason" ] || { echo "--full requires a reason" >&2; exit 2; }
    echo "agent-rg full output reason: $full_reason" >&2
    rg "${args[@]}"
    ;;
esac
