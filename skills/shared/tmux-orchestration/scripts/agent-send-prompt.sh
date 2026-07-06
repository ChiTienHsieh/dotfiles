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
  [ "$(prompt_occurrences "$screen")" -gt "$prompt_baseline_count" ]
}

prompt_occurrences() {
  local screen="$1"
  local normalized_screen
  local normalized_prompt
  # Long prompts can wrap inside tokens or with indentation. Remove all
  # whitespace before fallback matching so display wrapping does not look like
  # a failed paste.
  # LC_ALL=C throughout: macOS tr in a UTF-8 locale treats [:space:] as
  # including U+00A0/U+0085 but deletes them BYTE-wise, ripping continuation
  # bytes (0xA0/0x85) out of CJK characters (e.g. 報 = E5 A0 B1). The mangled
  # text then makes grep fail with "illegal byte sequence", the count reads 0,
  # and the caller re-pastes a prompt that actually arrived fine. C locale
  # makes both tools byte-oriented and deterministic.
  normalized_screen="$(printf '%s\n' "$screen" | LC_ALL=C tr -d '[:space:]')"
  normalized_prompt="$(printf '%s\n' "$prompt" | LC_ALL=C tr -d '[:space:]')"
  if [ -z "$normalized_prompt" ]; then
    echo 0
    return
  fi
  printf '%s\n' "$normalized_screen" | LC_ALL=C grep -oF -- "$normalized_prompt" | wc -l | LC_ALL=C tr -d '[:space:]'
}

busy_or_sent() {
  local screen="$1"
  [ "$(prompt_occurrences "$screen")" -le "$prompt_baseline_count" ] && return 0
  # Codex TUI busy signals.
  printf '%s\n' "$screen" | grep -qiE 'Working|esc to interrupt|interrupt' && return 0
  # Claude Code TUI: submitted prompts stay echoed in the transcript, so
  # prompt_visible alone cannot distinguish input-box from history. Two
  # CC-specific "it was sent" signals:
  # 1) the last input-marker line is empty (input box cleared after submit);
  printf '%s\n' "$screen" | grep -E '^❯' | tail -1 | grep -qE '^❯[[:space:]]*$' && return 0
  # 2) a spinner line like "✻ Germinating…" is present (turn in flight).
  printf '%s\n' "$screen" | grep -qE '^[[:space:]]*[✻✽✢✳✶∗·][[:space:]].+…' && return 0
  return 1
}

send_enter() {
  tmux send-keys -t "$pane" Enter
}

# An approval/selection dialog steals keyboard focus: pasted text is swallowed
# and any '1'/'2' character in the prompt can SELECT an option on the user's
# behalf. Detect an active dialog anywhere on the VISIBLE screen (no
# scrollback: answered dialogs disappear from the repaint but linger in
# history, so -S would false-positive).
dialog_active() {
  tmux capture-pane -p -t "$pane" 2>/dev/null \
    | LC_ALL=C grep -qE 'Esc to cancel|Do you want to (proceed|allow)|Enter to confirm'
}

# Paste via a tmux buffer instead of send-keys -l: send-keys types the string
# key-by-key, which can outrun the TUI on long CJK prompts (head-truncation,
# double-paste on retry). paste-buffer delivers the text atomically; -p uses
# bracketed paste when the app supports it.
paste_prompt() {
  printf '%s' "$prompt" | tmux load-buffer -b __agent_send_prompt - \
    && tmux paste-buffer -p -t "$pane" -b __agent_send_prompt -d
}

if [ "$#" -ne 2 ]; then
  usage
  exit 2
fi

pane="$1"
prompt="$2"
prompt_baseline_count=0

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

if dialog_active; then
  echo "agent-send-prompt.sh: pane $pane is showing an approval/selection dialog; refusing to paste (text could select an option). Resolve the dialog first (e.g. tmux send-keys -t $pane 1), then resend." >&2
  exit 3
fi

prompt_baseline_count="$(prompt_occurrences "$(pane_tail)")"

paste_prompt
sleep 0.4
screen="$(pane_tail)"

if ! prompt_visible "$screen"; then
  # Clear the input box before re-pasting: a false-negative verification must
  # not stack a second copy on top of a paste that actually landed.
  tmux send-keys -t "$pane" C-u
  sleep 0.2
  paste_prompt
  sleep 0.4
  screen="$(pane_tail)"
  if ! prompt_visible "$screen"; then
    # Leave the pane clean instead of abandoning half-pasted text.
    tmux send-keys -t "$pane" C-u
    echo "agent-send-prompt.sh: prompt did not appear in pane input; cleared input and refusing to press Enter." >&2
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
