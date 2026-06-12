#!/usr/bin/env bash
# List or peacefully close cmux surfaces created for delegated Codex work.
set -euo pipefail

history_file() {
  if [ -n "${CMUX_DELEGATION_HISTORY:-}" ]; then
    printf '%s\n' "$CMUX_DELEGATION_HISTORY"
  else
    printf '%s\n' "${TMPDIR:-/tmp}/cmux-delegations-${USER:-user}.tsv"
  fi
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

list_active() {
  active_records | while IFS=$'\t' read -r ts cwd workspace surface prompt marker report note; do
    printf '%s\t%s\t%s\t%s\t%s\n' "$surface" "$ts" "$cwd" "$report" "$note"
  done
  return 0
}

surface_in_history() {
  local surface="$1" file
  file="$(history_file)"
  [ -f "$file" ] || return 1
  awk -F '\t' -v s="$surface" \
    'NF >= 4 && $1 !~ /^#/ && $4 == s { found = 1; exit } END { exit !found }' "$file"
}

# Drop records for a closed surface so a reused surface id is not later
# mistaken for a delegated worker.
prune_surface() {
  local surface="$1" file tmp
  file="$(history_file)"
  [ -f "$file" ] || return 0
  tmp="${file}.tmp.$$"
  awk -F '\t' -v s="$surface" '$1 ~ /^#/ || $4 != s' "$file" >"$tmp" && mv "$tmp" "$file"
}

close_surface() {
  local surface="${1:?surface is required}"
  if ! surface_in_history "$surface"; then
    printf 'Refusing to close %s: not in delegation history (%s)\n' \
      "$surface" "$(history_file)" >&2
    return 3
  fi
  printf 'Sending /quit to %s\n' "$surface"
  if cmux send --surface "$surface" -- "/quit"; then
    sleep 0.3
    cmux send --surface "$surface" "\n" || true
    sleep "${CMUX_DELEGATION_QUIT_WAIT:-2}"
  else
    printf '%s not reachable; skipping /quit\n' "$surface" >&2
  fi
  printf 'Closing %s\n' "$surface"
  if cmux close-surface --surface "$surface"; then
    prune_surface "$surface"
  else
    printf 'Failed to close %s\n' "$surface" >&2
    return 1
  fi
}

close_all_active() {
  local surfaces=()
  while IFS=$'\t' read -r ts cwd workspace surface prompt marker report note; do
    surfaces+=("$surface")
  done < <(active_records)

  if [ "${#surfaces[@]}" -eq 0 ]; then
    printf 'No active delegated cmux surfaces found.\n'
    return 0
  fi

  local surface rc=0
  for surface in "${surfaces[@]}"; do
    close_surface "$surface" || rc=1
  done
  return "$rc"
}

case "${1:-}" in
  list)
    list_active
    ;;
  close)
    shift
    if [ "$#" -eq 0 ]; then
      echo "Usage: cmux_delegation_cleanup.sh close SURFACE [SURFACE ...]" >&2
      exit 2
    fi
    rc=0
    for surface in "$@"; do
      close_surface "$surface" || rc=1
    done
    exit "$rc"
    ;;
  close-all-active)
    close_all_active
    ;;
  path)
    history_file
    ;;
  *)
    cat <<'USAGE'
Usage:
  cmux_delegation_cleanup.sh list
  cmux_delegation_cleanup.sh close SURFACE [SURFACE ...]
  cmux_delegation_cleanup.sh close-all-active
  cmux_delegation_cleanup.sh path

Close flow:
  sends /quit to Codex, sends Enter, waits briefly, then runs cmux close-surface.
  Only surfaces recorded in the delegation history can be closed; successfully
  closed surfaces are pruned from the history file.
USAGE
    exit 2
    ;;
esac
