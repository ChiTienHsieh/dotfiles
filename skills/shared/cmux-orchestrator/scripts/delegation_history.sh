#!/usr/bin/env bash
# Track cmux delegation surfaces in a local temp file.
set -euo pipefail

history_file() {
  if [ -n "${CMUX_DELEGATION_HISTORY:-}" ]; then
    printf '%s\n' "$CMUX_DELEGATION_HISTORY"
  else
    printf '%s\n' "${TMPDIR:-/tmp}/cmux-delegations-${USER:-user}.tsv"
  fi
}

sanitize() {
  printf '%s' "${1:-}" | tr '\t\r\n' '   '
}

abs_path_or_empty() {
  local path="${1:-}"
  [ -n "$path" ] || return 0
  local dir base
  dir="$(cd "$(dirname "$path")" 2>/dev/null && pwd -P)" || {
    printf '%s\n' "$path"
    return 0
  }
  base="$(basename "$path")"
  printf '%s/%s\n' "$dir" "$base"
}

record() {
  local surface="${1:?surface is required}"
  local prompt="${2:-}"
  local marker="${3:-}"
  local report="${4:-}"
  local note="${5:-}"
  local file ts cwd workspace prompt_abs report_abs

  file="$(history_file)"
  mkdir -p "$(dirname "$file")"
  ts="$(date -u '+%Y-%m-%dT%H:%M:%SZ')"
  cwd="$(pwd -P)"
  workspace="${CMUX_WORKSPACE_ID:-}"
  prompt_abs="$(abs_path_or_empty "$prompt")"
  report_abs="$(abs_path_or_empty "$report")"

  if [ ! -f "$file" ]; then
    printf '# timestamp\tcwd\tworkspace\tsurface\tprompt\tmarker\treport\tnote\n' >"$file"
  fi

  printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$(sanitize "$ts")" \
    "$(sanitize "$cwd")" \
    "$(sanitize "$workspace")" \
    "$(sanitize "$surface")" \
    "$(sanitize "$prompt_abs")" \
    "$(sanitize "$marker")" \
    "$(sanitize "$report_abs")" \
    "$(sanitize "$note")" >>"$file"

  printf '%s\n' "$file"
}

list_records() {
  local file
  file="$(history_file)"
  [ -f "$file" ] || {
    printf 'No cmux delegation history found at %s\n' "$file" >&2
    return 0
  }
  cat "$file"
}

# One line per surface, keeping the latest record (a surface may be re-delegated).
latest_records() {
  awk -F '\t' 'NF >= 4 && $1 !~ /^#/ {
    if (!($4 in rec)) order[++n] = $4
    rec[$4] = $0
  } END { for (i = 1; i <= n; i++) print rec[order[i]] }' "$1"
}

active_records() {
  local file
  file="$(history_file)"
  [ -f "$file" ] || {
    printf 'No cmux delegation history found at %s\n' "$file" >&2
    return 0
  }

  latest_records "$file" | while IFS=$'\t' read -r ts cwd workspace surface prompt marker report note; do
    if cmux read-screen --surface "$surface" --lines 1 >/dev/null 2>&1; then
      printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' "$ts" "$cwd" "$workspace" "$surface" "$prompt" "$marker" "$report" "$note"
    fi
  done
}

case "${1:-}" in
  record)
    shift
    record "$@"
    ;;
  list)
    list_records
    ;;
  active)
    active_records
    ;;
  path)
    history_file
    ;;
  *)
    cat <<'USAGE'
Usage:
  delegation_history.sh record SURFACE [PROMPTFILE] [MARKER] [REPORT] [NOTE]
  delegation_history.sh list
  delegation_history.sh active
  delegation_history.sh path

History file:
  ${CMUX_DELEGATION_HISTORY:-${TMPDIR:-/tmp}/cmux-delegations-$USER.tsv}
USAGE
    exit 2
    ;;
esac
