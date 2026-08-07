#!/usr/bin/env bash
# mine_transcripts.sh — distill the last N hours of Claude Code + Codex CLI
# transcripts into a compact, token-cheap digest for the daily-loop skill.
#
# This is a DATA EXTRACTOR. It aggregates (counts) and samples (truncated
# snippets); it never proposes changes or touches config. With --checkpoint it
# also records which sessions this run consumed. All judgment stays with the LLM.
#
# macOS-targeted: relies on BSD `date -v` and `find -newermt`. Pure bash + jq.
set -euo pipefail

# ---- defaults ---------------------------------------------------------------
SINCE_HOURS=24
FORMAT=md            # md | json
MAX_SNIPPETS=40      # global cap on verbatim user-message snippets
SNIPPET_CHARS=240    # per-snippet truncation
SOURCE=all           # all | claude | codex
STATE_FILE="${HOME}/scratch/daily-loop/state.jsonl"
CHECKPOINT=0
DEBUG=0

CLAUDE_ROOT="${HOME}/.claude/projects"
CODEX_ROOT="${HOME}/.codex/sessions"
NPER=8               # max snippets kept per session before global capping

usage() {
  cat <<'USAGE'
Usage:
  mine_transcripts.sh [options]

Options:
  --since HOURS        Lookback window in hours (default 24)
  --format md|json     Output format (default md)
  --max-snippets N     Global cap on verbatim user snippets (default 40)
  --snippet-chars N    Truncate each snippet to N chars (default 240)
  --source all|claude|codex   Restrict source (default all)
  --state FILE         State log to read and optionally checkpoint
                       (default ~/scratch/daily-loop/state.jsonl)
  --checkpoint         Append this run's session keys to the state log
  --debug              Print candidate file list + counts to stderr
  -h, --help           Show this help

Emits a compact digest of how you worked in the window. Reads
~/.claude/projects (Claude Code) and ~/.codex/sessions (Codex CLI) jsonl.
USAGE
}

# ---- arg parsing ------------------------------------------------------------
while [ "$#" -gt 0 ]; do
  case "$1" in
    --since)         SINCE_HOURS="${2:?}"; shift 2 ;;
    --format)        FORMAT="${2:?}"; shift 2 ;;
    --max-snippets)  MAX_SNIPPETS="${2:?}"; shift 2 ;;
    --snippet-chars) SNIPPET_CHARS="${2:?}"; shift 2 ;;
    --source)        SOURCE="${2:?}"; shift 2 ;;
    --state)         STATE_FILE="${2:?}"; shift 2 ;;
    --checkpoint)    CHECKPOINT=1; shift ;;
    --debug)         DEBUG=1; shift ;;
    -h|--help)       usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done

command -v jq >/dev/null 2>&1 || { echo "mine_transcripts.sh: jq is required" >&2; exit 1; }

dbg() { [ "$DEBUG" -eq 1 ] && printf '%s\n' "$*" >&2 || true; }

# ---- portable date helpers (BSD `date -v` vs GNU `date -d`) ------------------
# The machine may have GNU coreutils on PATH, so detect at runtime.
if date -v-1H >/dev/null 2>&1; then DATE_FLAVOR=bsd; else DATE_FLAVOR=gnu; fi
dbg "date flavor: $DATE_FLAVOR"

date_ago_utc_iso() { # $1=hours -> UTC ISO8601 with Z
  if [ "$DATE_FLAVOR" = bsd ]; then date -u -v-"$1"H +%Y-%m-%dT%H:%M:%SZ
  else date -u -d "-$1 hours" +%Y-%m-%dT%H:%M:%SZ; fi
}
date_ago_local_find() { # $1=hours -> local "YYYY-MM-DD HH:MM:SS" for find -newermt
  if [ "$DATE_FLAVOR" = bsd ]; then date -v-"$1"H +"%Y-%m-%d %H:%M:%S"
  else date -d "-$1 hours" +"%Y-%m-%d %H:%M:%S"; fi
}
date_ago_day() { # $1=days -> YYYY/MM/DD
  if [ "$DATE_FLAVOR" = bsd ]; then date -v-"$1"d +%Y/%m/%d
  else date -d "-$1 days" +%Y/%m/%d; fi
}

# ---- cutoffs ----------------------------------------------------------------
# UTC ISO for precise per-line timestamp comparison (both sources emit Z).
CUTOFF_UTC="$(date_ago_utc_iso "$SINCE_HOURS")"
NOW_UTC="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
# Local time for find mtime prefilter (file mtimes are local).
CUTOFF_LOCAL="$(date_ago_local_find "$SINCE_HOURS")"

dbg "cutoff_utc=$CUTOFF_UTC now=$NOW_UTC cutoff_local=$CUTOFF_LOCAL"

# ---- candidate file discovery ----------------------------------------------
claude_files=()
codex_files=()

if [ "$SOURCE" = "all" ] || [ "$SOURCE" = "claude" ]; then
  if [ -d "$CLAUDE_ROOT" ]; then
    while IFS= read -r f; do
      [ -n "$f" ] && claude_files+=("$f")
    done < <(find "$CLAUDE_ROOT" -type f -name '*.jsonl' -newermt "$CUTOFF_LOCAL" 2>/dev/null)
  else
    echo "mine_transcripts.sh: $CLAUDE_ROOT not found, skipping Claude source" >&2
  fi
fi

if [ "$SOURCE" = "all" ] || [ "$SOURCE" = "codex" ]; then
  if [ -d "$CODEX_ROOT" ]; then
    # Codex is date-partitioned YYYY/MM/DD. Cover ceil(hours/24)+1 day dirs so a
    # window crossing midnight (or a multi-day window) is fully included; the
    # per-line timestamp filter trims precisely afterwards.
    ndays=$(( SINCE_HOURS / 24 + 1 ))
    d=0
    while [ "$d" -le "$ndays" ]; do
      day_dir="$CODEX_ROOT/$(date_ago_day "$d")"
      if [ -d "$day_dir" ]; then
        while IFS= read -r f; do
          [ -n "$f" ] && codex_files+=("$f")
        done < <(find "$day_dir" -type f -name 'rollout-*.jsonl' 2>/dev/null)
      fi
      d=$(( d + 1 ))
    done
  else
    echo "mine_transcripts.sh: $CODEX_ROOT not found, skipping Codex source" >&2
  fi
fi

dbg "claude candidate files: ${#claude_files[@]}"
for f in "${claude_files[@]:-}"; do [ -n "${f:-}" ] && dbg "  C $f"; done
dbg "codex candidate files: ${#codex_files[@]}"
for f in "${codex_files[@]:-}"; do [ -n "${f:-}" ] && dbg "  X $f"; done

# ---- per-file extractors (jq) ----------------------------------------------
# Each emits ONE compact JSON session-summary object (or nothing if the file
# has no in-window content). Output is collected one-per-line and aggregated.

read -r -d '' CLAUDE_JQ <<'JQ' || true
# args: $cutoff $sid $snipchars $nper
def trunc($n): if (.|length) > $n then (.[0:$n] + "…") else . end;
def is_preamble:
  test("^\\s*(Base directory for this skill:|<system-reminder>|Caveat:|<command-message>|<command-name>|<local-command|<task-notification>|<bash-input>|<bash-stdout>|<bash-stderr>|## Context Usage|\\[Request interrupted|You are running inside|This session is being continued from|Reply with exactly)");
def clean_bin:
  gsub("[\\n\\t]";" ") | gsub("^ +";"") | split(" ")[0]
  | gsub("^[\"']+";"") | gsub("[\"';]+$";"")
  | select(. != "" and (test("=")|not)) | (split("/") | last)
  | select(. != "" and . != "cd" and . != "sudo");
. as $lines
| ( [ $lines[] | select(.timestamp != null and .timestamp >= $cutoff) ] ) as $w
| if ($w | length) == 0 then empty else
  # real user messages: string content, or array content with no tool_result
  ( [ $w[]
      | select(.type=="user")
      | .message.content as $c
      | if ($c|type)=="string" then $c
        elif ($c|type)=="array" and (([ $c[].type ] | index("tool_result")) == null)
          then ([ $c[] | select(.type=="text") | .text ] | join("\n"))
        else empty end
      | select(. != null)
      | gsub("^\\s+";"")
      | select((. | length) >= 12)
      | select(is_preamble | not)
    ] ) as $umsgs
  | {
      source: "claude",
      session: $sid,
      cwd: ( [ $lines[] | .cwd // empty ] | last // "unknown" ),
      branch: ( [ $lines[] | .gitBranch // empty ] | last // "" ),
      version: ( [ $lines[] | .version // empty ] | last // "" ),
      first_ts: ($w[0].timestamp),
      last_ts: ($w[-1].timestamp),
      user_turns: ($umsgs | length),
      tools: ( reduce ( $w[]
                 | select(.type=="assistant")
                 | .message.content[]? | select(.type=="tool_use") | .name
               ) as $n ({}; .[$n] += 1) ),
      bash_bins: ( reduce ( $w[]
                 | select(.type=="assistant")
                 | .message.content[]? | select(.type=="tool_use" and .name=="Bash")
                 | (.input.command // "") | clean_bin
               ) as $b ({}; .[$b] += 1) ),
      read_files: ( reduce ( $w[]
                 | select(.type=="assistant")
                 | .message.content[]? | select(.type=="tool_use" and .name=="Read")
                 | (.input.file_path // empty)
               ) as $p ({}; .[$p] += 1) ),
      errorish: ( [ $w[]
                 | select(.type=="user")
                 | .message.content | select(type=="array") | .[]
                 | select(.type=="tool_result")
                 | ( (.is_error==true)
                     or ( ( .content
                            | if type=="string" then .
                              elif type=="array" then ([ .[].text? // "" ] | join(" "))
                              else "" end )
                          | test("^(Error|error:|fatal:|Traceback|panic:)") ) )
               ] | map(select(.)) | length ),
      snippets: ( [ $umsgs[] | trunc($snipchars) ] | .[0:$nper] )
    }
  end
JQ

read -r -d '' CODEX_JQ <<'JQ' || true
# args: $cutoff $sid $snipchars $nper
def trunc($n): if (.|length) > $n then (.[0:$n] + "…") else . end;
def is_preamble:
  test("^\\s*(# AGENTS.md|<environment_context>|<INSTRUCTIONS>|<user_instructions>|The following is|<task-notification>|\\[Request interrupted|You are running inside|This session is being continued from|Reply with exactly)");
def clean_bin:
  gsub("[\\n\\t]";" ") | gsub("^ +";"") | split(" ")[0]
  | gsub("^[\"']+";"") | gsub("[\"';]+$";"")
  | select(. != "" and (test("=")|not)) | (split("/") | last)
  | select(. != "" and . != "cd" and . != "sudo");
. as $lines
| ( [ $lines[] | select(.type=="session_meta") | .payload ] | last // {} ) as $meta
| ( [ $lines[] | select(.timestamp != null and .timestamp >= $cutoff) ] ) as $w
| if ($w | length) == 0 then empty else
  ( [ $w[]
      | select(.type=="event_msg")
      | .payload | select(.type=="user_message") | .message
      | select(type=="string")
      | gsub("^\\s+";"")
      | select((. | length) >= 12)
      | select(is_preamble | not)
    ] ) as $umsgs
  | {
      source: "codex",
      session: $sid,
      cwd: ( ($meta.cwd) // "unknown" ),
      branch: ( ($meta.git.branch) // "" ),
      version: ( ($meta.cli_version) // "" ),
      first_ts: ($w[0].timestamp),
      last_ts: ($w[-1].timestamp),
      user_turns: ($umsgs | length),
      tools: ( reduce ( $w[]
                 | select(.type=="response_item")
                 | .payload | select(.type=="function_call") | .name
               ) as $n ({}; .[$n] += 1) ),
      bash_bins: ( reduce ( $w[]
                 | select(.type=="response_item")
                 | .payload | select(.type=="function_call" and (.name|test("shell|exec_command|local_shell")))
                 | (.arguments // "{}") | (fromjson? // {})
                 | (.command // .cmd // .input // [])
                 | if type=="array" then . else [tostring] end
                 | map(select(. != "bash" and . != "-lc" and . != "-c" and . != "sh"))
                 | (.[0] // "") | clean_bin
               ) as $b ({}; .[$b] += 1) ),
      read_files: {},
      errorish: ( [ $w[]
                 | select(.type=="response_item")
                 | .payload | select(.type=="function_call_output")
                 | ( .output
                     | if type=="string" then .
                       elif type=="object" then (.content // .output // "" | tostring)
                       else tostring end )
                 | select(test("(Error|error:|fatal:|Traceback|panic:|exit code: [1-9])"))
               ] | length ),
      snippets: ( [ $umsgs[] | trunc($snipchars) ] | .[0:$nper] )
    }
  end
JQ

# ---- run extractors, collect per-session summaries --------------------------
SESS_TMP="$(mktemp "${TMPDIR:-/tmp}/daily-loop-sessions.XXXXXX")"
trap 'rm -f "$SESS_TMP"' EXIT

for f in "${claude_files[@]:-}"; do
  [ -n "${f:-}" ] || continue
  sid="$(basename "$f" .jsonl)"
  jq -s -c \
    --arg cutoff "$CUTOFF_UTC" --arg sid "$sid" \
    --argjson snipchars "$SNIPPET_CHARS" --argjson nper "$NPER" \
    "$CLAUDE_JQ" "$f" 2>/dev/null >>"$SESS_TMP" || dbg "claude parse failed: $f"
done

for f in "${codex_files[@]:-}"; do
  [ -n "${f:-}" ] || continue
  sid="$(basename "$f" .jsonl | sed 's/^rollout-//')"
  jq -s -c \
    --arg cutoff "$CUTOFF_UTC" --arg sid "$sid" \
    --argjson snipchars "$SNIPPET_CHARS" --argjson nper "$NPER" \
    "$CODEX_JQ" "$f" 2>/dev/null >>"$SESS_TMP" || dbg "codex parse failed: $f"
done

dbg "session summaries: $(wc -l < "$SESS_TMP" | tr -d ' ')"

# ---- prior run checkpoints --------------------------------------------------
# Run records use source-prefixed keys so Claude and Codex IDs cannot collide.
PRIOR_SESSIONS='[]'
if [ -f "$STATE_FILE" ]; then
  PRIOR_SESSIONS="$(jq -s -c '[ .[] | select(.kind? == "run") | .sessions[]? ] | unique' "$STATE_FILE" 2>/dev/null || echo '[]')"
fi

# ---- aggregate --------------------------------------------------------------
read -r -d '' AGG_JQ <<'JQ' || true
# slurp of per-session objects; args: $window_from $window_to $hours $maxsnip $prior
def mergecounts(f): reduce (.[] | f | to_entries[]) as $e ({}; .[$e.key] += $e.value);
. as $sessions
| {
    window: { from: $window_from, to: $window_to, hours: $hours },
    totals: {
      sessions: ($sessions | length),
      by_source: ( reduce ($sessions[].source) as $s ({}; .[$s] += 1) ),
      projects: ( [ $sessions[].cwd ] | unique | length ),
      user_turns: ( [ $sessions[].user_turns ] | add // 0 ),
      tools: mergecounts(.tools),
      errorish: ( [ $sessions[].errorish ] | add // 0 ),
      new_sessions: ( [ $sessions[] | ("\(.source):\(.session)")
                        | select(. as $x | ($prior | index($x)) | not) ] | length )
    },
    projects: (
      [ $sessions | group_by(.cwd)[]
        | {
            cwd: .[0].cwd,
            sources: ( [ .[].source ] | unique ),
            sessions: length,
            user_turns: ( [ .[].user_turns ] | add // 0 ),
            errorish: ( [ .[].errorish ] | add // 0 ),
            tools: ( reduce (.[].tools | to_entries[]) as $e ({}; .[$e.key] += $e.value) ),
            bash_bins: ( reduce (.[].bash_bins | to_entries[]) as $e ({}; .[$e.key] += $e.value) ),
            snippets: ( [ .[].snippets[] ] )
          }
      ] | sort_by(-.user_turns)
    ),
    signals: {
      hot_bins: ( mergecounts(.bash_bins) | to_entries | map(select(.value >= 3))
                  | sort_by(-.value) | map({ bin: .key, n: .value }) ),
      duplicate_read_hotspots: ( mergecounts(.read_files) | to_entries
                  | map(select(.value > 3)) | sort_by(-.value)
                  | map({ path: .key, n: .value }) ),
      recurring_openers: (
        [ $sessions[].snippets[]
          | ascii_downcase | gsub("[^a-z0-9 ]";" ") | gsub("  +";" ")
          | (split(" ")[0:6] | join(" ")) | select(. != "")
        ] | group_by(.) | map(select(length >= 2) | { opener: .[0], n: length })
          | sort_by(-.n)
      )
    }
  }
JQ

AGG="$(jq -s \
  --arg window_from "$CUTOFF_UTC" --arg window_to "$NOW_UTC" \
  --argjson hours "$SINCE_HOURS" --argjson maxsnip "$MAX_SNIPPETS" \
  --argjson prior "$PRIOR_SESSIONS" \
  "$AGG_JQ" "$SESS_TMP")"

# ---- output -----------------------------------------------------------------
if [ "$FORMAT" = "json" ]; then
  printf '%s\n' "$AGG"
else
  # Markdown rendering, driven from the aggregate JSON. The per-project snippet
  # count is budgeted so the total stays under --max-snippets.
  read -r -d '' MD_JQ <<'JQ' || true
# args: $maxsnip
def commas(o): [ o | to_entries | sort_by(-.value) | .[] | "\(.key)×\(.value)" ] | join(", ");
( .projects | length ) as $np
| ( if $np > 0 then ( ($maxsnip / $np) | floor ) else 0 end ) as $share
| ( if $share < 2 then 2 else $share end ) as $per
| ( "# daily-loop digest  (window: \(.window.from) .. \(.window.to), \(.window.hours)h)\n" ),
  ( "## Overview" ),
  ( "- sessions: \(.totals.sessions) (" +
      ( [ .totals.by_source | to_entries[] | "\(.key): \(.value)" ] | join(", ") ) + ")" ),
  ( "- distinct projects (cwd): \(.totals.projects)" ),
  ( "- total user turns: \(.totals.user_turns)" ),
  ( "- top tools: " + ( commas(.totals.tools) | if . == "" then "(none)" else . end ) ),
  ( "- error-ish tool results: \(.totals.errorish)  (heuristic, soft signal)" ),
  ( "- new sessions since last digest: \(.totals.new_sessions)" ),
  ( "" ),
  ( "## Projects" ),
  ( .projects[]
    | ( "### \(.cwd)  [\(.sources | join("+"))]" + (if .branch then "" else "" end) ),
      ( "- sessions: \(.sessions), user turns: \(.user_turns), error-ish: \(.errorish)" ),
      ( "- tools: " + ( commas(.tools) | if . == "" then "(none)" else . end ) ),
      ( if (.bash_bins | length) > 0
          then "- hot shell bins: " + commas(.bash_bins) else empty end ),
      ( if (.snippets | length) > 0
          then "- representative asks:" else empty end ),
      ( .snippets[0:$per][] | "  - " + (gsub("\n";" ⏎ ")) ),
      ( "" )
  ),
  ( "## Cross-cutting signals (script-computed, not judged)" ),
  ( if (.signals.hot_bins | length) > 0
      then "- high-frequency shell bins: " +
        ( [ .signals.hot_bins[] | "\(.bin)(\(.n))" ] | join(", ") )
      else "- high-frequency shell bins: (none ≥3)" end ),
  ( if (.signals.recurring_openers | length) > 0
      then "- recurring ask openers (≥2×): " +
        ( [ .signals.recurring_openers[] | "\"\(.opener)\"×\(.n)" ] | join("; ") )
      else "- recurring ask openers (≥2×): (none)" end ),
  ( "" ),
  ( "## Duplicate Read Hotspots" ),
  ( if (.signals.duplicate_read_hotspots | length) > 0
      then "- Claude Read paths over 3×: " +
        ( [ .signals.duplicate_read_hotspots[] | "\(.path)(\(.n))" ] | join(", ") )
      else "- Claude Read paths over 3×: (none)" end )
JQ

  printf '%s\n' "$AGG" | jq -r --argjson maxsnip "$MAX_SNIPPETS" "$MD_JQ"
fi

if [ "$CHECKPOINT" -eq 1 ]; then
  CURRENT_SESSIONS="$(jq -s -c '[ .[] | ("\(.source):\(.session)") ] | unique' "$SESS_TMP")"
  NEW_SESSIONS="$(jq -nc --argjson current "$CURRENT_SESSIONS" \
    --argjson prior "$PRIOR_SESSIONS" '$current - $prior')"
  if [ "$(jq 'length' <<<"$NEW_SESSIONS")" -gt 0 ]; then
    mkdir -p "$(dirname "$STATE_FILE")"
    jq -nc --arg ts "$NOW_UTC" --argjson sessions "$NEW_SESSIONS" \
      '{kind:"run",ts:$ts,sessions:$sessions}' >>"$STATE_FILE"
  fi
fi
