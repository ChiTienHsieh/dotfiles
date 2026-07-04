#!/usr/bin/env bash
# Safely send a one-line prompt to an existing tmux pane.
# Usage: agent-send-prompt.sh PANE 'ONE-LINE PROMPT'

set -o pipefail

usage() {
  echo "usage: agent-send-prompt.sh PANE 'ONE-LINE PROMPT'" >&2
}

pane_tail() {
  tmux capture-pane -p -t "$pane" -S -40 2>/dev/null || true
}

prompt_visible() {
  local screen="$1"
  local normalized_screen
  local normalized_prompt
  printf '%s\n' "$screen" | grep -Fq -- "$prompt" && return 0
  # Long prompts can wrap inside tokens or with indentation. Remove all
  # whitespace before fallback matching so display wrapping does not look like
  # a failed paste.
  normalized_screen="$(printf '%s\n' "$screen" | tr -d '[:space:]')"
  normalized_prompt="$(printf '%s\n' "$prompt" | tr -d '[:space:]')"
  printf '%s\n' "$normalized_screen" | grep -Fq -- "$normalized_prompt"
}

busy_or_sent() {
  local screen="$1"
  ! prompt_visible "$screen" && return 0
  printf '%s\n' "$screen" | grep -qiE 'Working|esc to interrupt|interrupt' && return 0
  return 1
}

send_enter() {
  tmux send-keys -t "$pane" Enter
}

if [ "$#" -ne 2 ]; then
  usage
  exit 2
fi

pane="$1"
prompt="$2"

case "$prompt" in
  *$'\n'*|*$'\r'*)
    echo "agent-send-prompt.sh: prompt must be one line; put long/multiline instructions in a file and send one read-file instruction." >&2
    exit 2
    ;;
esac

if ! tmux capture-pane -p -t "$pane" -S -1 >/dev/null 2>&1; then
  echo "agent-send-prompt.sh: tmux target not found: $pane" >&2
  exit 2
fi

tmux send-keys -t "$pane" -l "$prompt"
sleep 0.4
screen="$(pane_tail)"

if ! prompt_visible "$screen"; then
  tmux send-keys -t "$pane" -l "$prompt"
  sleep 0.4
  screen="$(pane_tail)"
  if ! prompt_visible "$screen"; then
    echo "agent-send-prompt.sh: prompt did not appear in pane input; refusing to press Enter." >&2
    echo "----- pane tail -----" >&2
    printf '%s\n' "$screen" >&2
    exit 1
  fi
fi

send_enter
sleep 0.6
screen="$(pane_tail)"

if busy_or_sent "$screen"; then
  exit 0
fi

send_enter
sleep 0.6
screen="$(pane_tail)"

if busy_or_sent "$screen"; then
  exit 0
fi

echo "agent-send-prompt.sh: prompt still appears unsent after retrying Enter." >&2
echo "----- pane tail -----" >&2
printf '%s\n' "$screen" >&2
exit 1
