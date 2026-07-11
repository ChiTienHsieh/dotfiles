#!/bin/bash
# Custom Claude Code statusline
# Line 1: dir [git branch] model (context size)
# Line 2: context tokens (%) │ 5h: usage% ↻HH:MM │ 7d: usage% ↻Day HH:MM │ ♨ ↻HH:MM (cache)

input=$(cat)

# ── Tokyo Night Colors ──
R='\033[0m'
D='\033[2m'
CYAN='\033[38;2;125;207;255m'
GREEN='\033[38;2;158;206;106m'
MAG='\033[38;2;187;154;247m'
RED='\033[38;2;247;118;142m'
YEL='\033[38;2;224;175;104m'
ORA='\033[38;2;255;158;100m'
GRAY='\033[38;2;178;189;220m'
GRAYD='\033[38;2;116;128;164m'
BLUE='\033[38;2;162;190;249m'
BLUED='\033[38;2;130;152;199m'
PINK='\033[38;2;255;100;164m'

# ── Parse JSON (single jq call) ──
DATA=$(echo "$input" | jq -r '
  [
    (.model.display_name // "?"),
    ((.workspace.current_dir // "") | split("/") | last // ""),
    (if .context_window.current_usage then
      ((.context_window.current_usage.input_tokens // 0) + (.context_window.current_usage.output_tokens // 0) + (.context_window.current_usage.cache_creation_input_tokens // 0) + (.context_window.current_usage.cache_read_input_tokens // 0))
    else
      ((.context_window.context_window_size // 0) * ((.context_window.used_percentage // 0) / 100) | round)
    end | tostring),
    (.context_window.used_percentage // 0 | floor | tostring),
    (.context_window.context_window_size // 0 | tostring),
    (.rate_limits.five_hour.used_percentage // -1 | tostring),
    (.rate_limits.five_hour.resets_at // -1 | tostring),
    (.rate_limits.seven_day.used_percentage // -1 | tostring),
    (.rate_limits.seven_day.resets_at // -1 | tostring),
    (.transcript_path // "")
  ] | .[]
')
IFS=$'\n' read -r -d '' MODEL DIR CTX_TOKENS CTX_PCT CTX_SIZE \
  FIVE_PCT FIVE_RESET SEVEN_PCT SEVEN_RESET TRANSCRIPT <<< "$DATA" || true

# ── Helpers ──
fmt_tokens() {
  local t=$1
  if [ "$t" -ge 1000 ] 2>/dev/null; then echo "$((t / 1000))k"
  else echo "$t"; fi
}

fmt_ctx_size() {
  local s=$1
  if [ "$s" -ge 1000000 ] 2>/dev/null; then echo "$((s / 1000000))M"
  elif [ "$s" -ge 1000 ] 2>/dev/null; then echo "$((s / 1000))k"
  else echo "$s"; fi
}

pct_color() {
  local p=${1:-0}
  if [ "$p" -ge 50 ] 2>/dev/null; then echo -ne "$BLUE"
  else echo -ne "$GRAY"; fi
}

pct_dim() {
  local p=${1:-0}
  if [ "$p" -ge 50 ] 2>/dev/null; then echo -ne "$BLUED"
  else echo -ne "$GRAYD"; fi
}

ts_fmt() {
  local ts=$1 fmt=$2
  date -d "@$ts" "+$fmt" 2>/dev/null || /bin/date -r "$ts" "+$fmt" 2>/dev/null
}

# ── Git ──
GITPART=""
if git rev-parse --is-inside-work-tree &>/dev/null; then
  BRANCH=$(git symbolic-ref --short HEAD 2>/dev/null || git rev-parse --short HEAD 2>/dev/null)
  if git diff --quiet HEAD 2>/dev/null && git diff --cached --quiet HEAD 2>/dev/null; then
    GITPART=" ${GREEN}⌥ ${BRANCH} ●${R}"
  else
    GITPART=" ${YEL}⌥ ${BRANCH} ●${R}"
  fi
fi

# ── Line 1 ──
SIZE_FMT=$(fmt_ctx_size "${CTX_SIZE:-0}")
L1="${CYAN}${DIR}${R}${GITPART} ${PINK}❋${R} ${MAG}${MODEL}${R}"
# Only append context size if display_name doesn't already include it
if [[ "$MODEL" != *"context"* ]] && [ "$SIZE_FMT" != "0" ]; then
  L1+=" ${D}(${SIZE_FMT} context)${R}"
fi

# ── Line 2 ──
TOKENS_FMT=$(fmt_tokens "${CTX_TOKENS:-0}")
CTX_CLR=$(pct_color "${CTX_PCT:-0}")
L2="${CTX_CLR}◷${R} ${CTX_CLR}${TOKENS_FMT}/${SIZE_FMT}${R} $(pct_dim "${CTX_PCT:-0}")(${CTX_PCT}%)${R}"

if [ "$FIVE_PCT" != "-1" ] && [ -n "$FIVE_PCT" ]; then
  FP=$(printf '%.0f' "$FIVE_PCT")
  L2+=" ${GRAYD}│${R} $(pct_color "$FP")5h: ${FP}%${R}"
  if [ "$FIVE_RESET" != "-1" ] && [ -n "$FIVE_RESET" ]; then
    FR=$(ts_fmt "${FIVE_RESET%%.*}" "%H:%M")
    [ -n "$FR" ] && L2+=" $(pct_dim "$FP")↻${FR}${R}"
  fi
fi

# ── Prompt cache (♨ hot with expiry time / ❄ cold) ──
# Ephemeral cache resets its TTL on every request; transcript mtime ≈ last request.
# TTL is read from the transcript's usage.cache_creation buckets (5m vs 1h), not hardcoded.
CACHE_TTL=300
cache_part() {
  local f=$1 mtime now ttl=$CACHE_TTL
  [ -n "$f" ] && [ -f "$f" ] || return
  # GNU first: BSD stat rejects -c and falls through; GNU stat -f would "succeed" with fs info
  mtime=$(stat -c %Y "$f" 2>/dev/null || stat -f %m "$f" 2>/dev/null) || return
  tail -c 65536 "$f" 2>/dev/null | grep -q '"ephemeral_1h_input_tokens":[1-9]' && ttl=3600
  now=$(date +%s)
  if [ $(( mtime + ttl - now )) -le 0 ]; then
    echo -ne " ${GRAYD}│${R} ${BLUE}❄ cold${R}"
  else
    echo -ne " ${GRAYD}│${R} ${ORA}♨ ↻$(ts_fmt $(( mtime + ttl )) "%H:%M")${R}"
  fi
}

if [ "$SEVEN_PCT" != "-1" ] && [ -n "$SEVEN_PCT" ]; then
  SP=$(printf '%.0f' "$SEVEN_PCT")
  L2+=" ${GRAYD}│${R} $(pct_color "$SP")7d: ${SP}%${R}"
  if [ "$SEVEN_RESET" != "-1" ] && [ -n "$SEVEN_RESET" ]; then
    SR=$(ts_fmt "${SEVEN_RESET%%.*}" "%a %H:%M")
    [ -n "$SR" ] && L2+=" $(pct_dim "$SP")↻${SR}${R}"
  fi
fi

L2+=$(cache_part "$TRANSCRIPT")

echo -e "$L1"
echo -e "$L2"

# ── Per-pane cache map for tmux status (read by tmux/claude-cache-status.sh) ──
# $TMUX_PANE can go stale (inherited env survives pane moves); the controlling
# tty always belongs to the pane this CC is displayed in, so match by tty.
if [ -n "$TMUX" ] && [ -n "$TRANSCRIPT" ]; then
  # This process is spawned detached (tty = ??); the claude ancestor is the
  # pane's foreground process and owns the pane tty, so walk up to it.
  PID=$$ MYTTY=
  for _ in 1 2 3 4 5 6; do
    read -r PPID_ TTY_ <<< "$(ps -o ppid=,tty= -p "$PID" 2>/dev/null)"
    [ -n "$TTY_" ] || break
    if [ "$TTY_" != "??" ]; then MYTTY=$TTY_; break; fi
    PID=$PPID_
    [ "$PID" -gt 1 ] 2>/dev/null || break
  done
  if [ -n "$MYTTY" ] && [ "$MYTTY" != "??" ]; then
    PANE_INFO=$(tmux list-panes -a -F '#{pane_tty} #{pane_id} #{pane_current_command}' 2>/dev/null \
      | grep "^/dev/${MYTTY} ")
    if [ -n "$PANE_INFO" ]; then
      read -r _ PANE_ID PANE_CMD <<< "$PANE_INFO"
      mkdir -p /tmp/claude/pane-cache
      printf '%s\n%s\n' "$TRANSCRIPT" "$PANE_CMD" > "/tmp/claude/pane-cache/${PANE_ID#%}"
    fi
  fi
fi
