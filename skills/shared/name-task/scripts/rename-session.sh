#!/bin/bash
# rename-session.sh — print a suggested /rename command; never mutates tmux
# 用法：rename-session.sh "<title>"
#
# Does not send-keys into any pane. Skill loading is not human authorization;
# the caller (or user) applies /rename manually. Exit 1 so callers treat the
# title as a suggestion, not an applied rename.
set -euo pipefail

TITLE="${1:?Usage: rename-session.sh '<title>'}"

printf 'Suggested title (apply manually):\n  /rename %s\n' "$TITLE"
if [ -n "${TMUX_PANE:-}" ]; then
  printf 'tmux pane %s is set; this script does not send-keys. Apply /rename in the TUI.\n' "$TMUX_PANE"
fi
exit 1
