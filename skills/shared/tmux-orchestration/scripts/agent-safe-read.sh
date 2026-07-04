#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: agent-safe-read.sh FILE [--range START:END]" >&2
}

[ "$#" -ge 1 ] || { usage; exit 2; }

file="$1"
shift
range=""

while [ "$#" -gt 0 ]; do
  case "$1" in
    --range) range="${2:?}"; shift 2 ;;
    *) echo "Unknown option: $1" >&2; usage; exit 2 ;;
  esac
done

[ -f "$file" ] || { echo "File not found: $file" >&2; exit 1; }

lines="$(wc -l < "$file" | tr -d ' ')"
size="$(wc -c < "$file" | tr -d ' ')"
echo "$lines lines, $size bytes"

if [ -n "$range" ]; then
  start="${range%%:*}"
  end="${range#*:}"
  case "$start" in ""|*[!0-9]*) echo "Invalid range: $range" >&2; exit 2 ;; esac
  case "$end" in ""|*[!0-9]*) echo "Invalid range: $range" >&2; exit 2 ;; esac
  sed -n "${start},${end}p" "$file"
else
  sed -n '1,200p' "$file"
  if [ "$lines" -gt 200 ]; then
    echo "... use --range to read more"
  fi
fi
