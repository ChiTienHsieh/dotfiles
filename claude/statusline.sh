#!/bin/bash
# Custom Claude Code statusline
# Line 1: dir [git branch] model (context size)
# Line 2: context tokens (%) │ 5h: usage% ↻HH:MM │ 7d: usage% ↻Day HH:MM
#         │ <Model>: usage% ↻Day HH:MM  (per-model weekly bucket, OAuth usage API)
# Cache state is NOT displayed here (lives in tmux status-right, single home);
# this script only registers the pane→transcript map that tmux reads.

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
    (.transcript_path // ""),
    (.version // "")
  ] | .[]
')
IFS=$'\n' read -r -d '' MODEL DIR CTX_TOKENS CTX_PCT CTX_SIZE \
  FIVE_PCT FIVE_RESET SEVEN_PCT SEVEN_RESET TRANSCRIPT CC_VERSION <<< "$DATA" || true

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

if [ "$SEVEN_PCT" != "-1" ] && [ -n "$SEVEN_PCT" ]; then
  SP=$(printf '%.0f' "$SEVEN_PCT")
  L2+=" ${GRAYD}│${R} $(pct_color "$SP")7d: ${SP}%${R}"
  if [ "$SEVEN_RESET" != "-1" ] && [ -n "$SEVEN_RESET" ]; then
    SR=$(ts_fmt "${SEVEN_RESET%%.*}" "%a %H:%M")
    [ -n "$SR" ] && L2+=" $(pct_dim "$SP")↻${SR}${R}"
  fi
fi

# Per-model weekly bucket (e.g. Fable): not in the statusline stdin payload, so
# pull it from the OAuth usage API the /usage panel uses. Cached 60s; any failure
# (no keychain, no network, non-200, no scoped bucket) falls back to the cached
# value, else the segment is silently omitted. Only {name, pct, epoch} is cached.
WK_CACHE=/tmp/claude/weekly-model
wk_fetch() {
  local tok resp
  tok=$(security find-generic-password -s "Claude Code-credentials" -w 2>/dev/null \
    | jq -r '.claudeAiOauth.accessToken // empty' 2>/dev/null)
  [ -n "$tok" ] || return 1
  # The client User-Agent matters: without it this endpoint starts answering 429.
  resp=$(curl -s --max-time 2 \
    -H "Authorization: Bearer $tok" \
    -H "anthropic-beta: oauth-2025-04-20" \
    -H "User-Agent: claude-code/${CC_VERSION:-2.1.260}" \
    'https://api.anthropic.com/api/oauth/usage?at_wall=1&skip_spend=1' 2>/dev/null) || return 1
  printf '%s' "$resp" | jq -r '
    .limits[]?
    | select(.kind == "weekly_scoped" and .percent != null
             and (.scope.model.display_name // null) != null)
    | [ .scope.model.display_name,
        (.percent | tostring),
        ((.resets_at // "") | sub("\\.[0-9]+"; "") | sub("\\+00:00$"; "Z")
         | (try fromdateiso8601 catch 0) | tostring) ]
    | @tsv
  ' 2>/dev/null | head -1
}

WK_LINE="" WK_MTIME=""
if [ -r "$WK_CACHE" ]; then
  # GNU stat wants -c, BSD stat wants -f; GNU's -f means "filesystem status" and
  # exits 0 with unrelated output, so try -c first and require a plain number.
  WK_MTIME=$(stat -c %Y "$WK_CACHE" 2>/dev/null || stat -f %m "$WK_CACHE" 2>/dev/null)
  case $WK_MTIME in '' | *[!0-9]*) WK_MTIME= ;; esac
  WK_LINE=$(head -1 "$WK_CACHE" 2>/dev/null)
fi
if [ -z "$WK_MTIME" ] || [ $(( $(date +%s) - WK_MTIME )) -ge 60 ] 2>/dev/null; then
  WK_NEW=$(wk_fetch)
  if [ -n "$WK_NEW" ]; then
    WK_LINE=$WK_NEW
    mkdir -p /tmp/claude 2>/dev/null
    if WK_TMP=$(mktemp "${WK_CACHE}.XXXXXX" 2>/dev/null); then
      printf '%s\n' "$WK_NEW" > "$WK_TMP" 2>/dev/null
      mv -f "$WK_TMP" "$WK_CACHE" 2>/dev/null || rm -f "$WK_TMP" 2>/dev/null
    fi
  fi
fi
if [ -n "$WK_LINE" ]; then
  IFS=$'\t' read -r WK_NAME WK_PCT WK_RESET <<< "$WK_LINE"
  if [ -n "$WK_NAME" ] && [ -n "$WK_PCT" ]; then
    WP=$(printf '%.0f' "$WK_PCT" 2>/dev/null)
    if [ -n "$WP" ]; then
      L2+=" ${GRAYD}│${R} $(pct_color "$WP")${WK_NAME}: ${WP}%${R}"
      if [ -n "$WK_RESET" ] && [ "$WK_RESET" != "0" ]; then
        WR=$(ts_fmt "${WK_RESET%%.*}" "%a %H:%M")
        [ -n "$WR" ] && L2+=" $(pct_dim "$WP")↻${WR}${R}"
      fi
    fi
  fi
fi

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
