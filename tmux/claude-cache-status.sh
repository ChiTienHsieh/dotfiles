#!/bin/bash
# Claude Code prompt-cache state for tmux status-right: ♨ ↻HH:MM (hot) / ❄ cold
# Newest transcript under ~/.claude/projects ≈ last CC request machine-wide.
# TTL is read from the transcript's usage.cache_creation buckets (5m vs 1h), not hardcoded.

latest=$(ls -t "$HOME"/.claude/projects/*/*.jsonl 2>/dev/null | head -1)
[ -n "$latest" ] || exit 0

# GNU first: BSD stat rejects -c and falls through; GNU stat -f would "succeed" with fs info
mtime=$(stat -c %Y "$latest" 2>/dev/null || stat -f %m "$latest" 2>/dev/null) || exit 0

ttl=300
tail -c 65536 "$latest" 2>/dev/null | grep -q '"ephemeral_1h_input_tokens":[1-9]' && ttl=3600

if [ $(( mtime + ttl - $(date +%s) )) -le 0 ]; then
  echo "#[fg=#a2bef9]❄ cold#[default]"
else
  # BSD date -r takes epoch seconds; GNU date -r wants a file, so it errs and falls to -d
  exp=$(date -r $(( mtime + ttl )) +%H:%M 2>/dev/null || date -d "@$(( mtime + ttl ))" +%H:%M 2>/dev/null)
  echo "#[fg=#ff9e64]♨ ↻${exp}#[default]"
fi
