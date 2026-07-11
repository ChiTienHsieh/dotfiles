#!/bin/bash
# Per-pane Claude Code prompt-cache state for tmux formats: ♨ ↻HH:MM (hot) / ❄ cold
# Usage: claude-cache-status.sh '#{pane_id}' '#{pane_current_command}'
# Reads the pane→transcript map that CC's statusline.sh maintains under
# /tmp/claude/pane-cache/. Says nothing for panes without a live CC.
# TTL is read from the transcript's usage.cache_creation buckets (5m vs 1h), not hardcoded.

pane=${1#%}
[ -n "$pane" ] || exit 0
map="/tmp/claude/pane-cache/$pane"
[ -f "$map" ] || exit 0

{ IFS= read -r transcript; IFS= read -r cmd; } < "$map"
# The pane stopped running the CC that wrote this map (CC exited, shell/other
# tool took over) → stale entry, show nothing rather than mislead.
[ -n "$2" ] && [ "$2" != "$cmd" ] && exit 0
[ -f "$transcript" ] || exit 0

# Last request time = timestamp of the last entry IN the file, not file mtime:
# CC background housekeeping touches the file hours after the last message,
# so mtime reads permanently hot (observed 2h drift on an idle session).
ts=$(tail -c 262144 "$transcript" 2>/dev/null | grep -o '"timestamp":"[^"]*"' | tail -1 | cut -d'"' -f4)
last=
if [ -n "$ts" ]; then
  t=${ts%%.*}
  # GNU date parses ISO directly; BSD date needs -j -u -f
  last=$(date -d "${t}Z" +%s 2>/dev/null || date -j -u -f '%Y-%m-%dT%H:%M:%S' "$t" +%s 2>/dev/null)
fi
if [ -z "$last" ]; then
  # GNU first: BSD stat rejects -c and falls through; GNU stat -f would "succeed" with fs info
  last=$(stat -c %Y "$transcript" 2>/dev/null || stat -f %m "$transcript" 2>/dev/null) || exit 0
fi

ttl=300
tail -c 65536 "$transcript" 2>/dev/null | grep -q '"ephemeral_1h_input_tokens":[1-9]' && ttl=3600

# Blue pane id says which pane this cache belongs to (the focused one)
who="#[fg=#82b8ff]%${pane}#[default]"
if [ $(( last + ttl - $(date +%s) )) -le 0 ]; then
  echo "${who} #[fg=#a2bef9]❄ cold#[default]"
else
  # BSD date -r takes epoch seconds; GNU date -r wants a file, so it errs and falls to -d
  exp=$(date -r $(( last + ttl )) +%H:%M 2>/dev/null || date -d "@$(( last + ttl ))" +%H:%M 2>/dev/null)
  echo "${who} #[fg=#ff9e64]♨ ↻${exp}#[default]"
fi
