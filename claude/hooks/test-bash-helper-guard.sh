#!/usr/bin/env bash
# Tests for claude/hooks/bash-helper-guard.py
#
# Feeds fake PreToolUse JSON payloads on stdin and asserts the hook's
# allow/deny decision. Prints PASS/FAIL per case; exits non-zero if any
# case fails.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK="$SCRIPT_DIR/bash-helper-guard.py"

fail_count=0
case_num=0

run_case() {
  local desc="$1"
  local command="$2"
  local expect="$3" # "deny" or "allow"

  case_num=$((case_num + 1))

  local payload
  payload=$(python3 -c '
import json, sys
print(json.dumps({"tool_input": {"command": sys.argv[1]}}))
' "$command")

  local output
  output=$(printf '%s' "$payload" | python3 "$HOOK")

  local got="allow"
  if printf '%s' "$output" | grep -q '"permissionDecision": *"deny"'; then
    got="deny"
  fi

  if [ "$got" = "$expect" ]; then
    echo "PASS [$case_num] $desc"
  else
    echo "FAIL [$case_num] $desc (expected=$expect got=$got output=$output)"
    fail_count=$((fail_count + 1))
  fi
}

run_case_raw_stdin() {
  local desc="$1"
  local stdin_content="$2"
  local expect="$3"

  case_num=$((case_num + 1))

  local output
  output=$(printf '%s' "$stdin_content" | python3 "$HOOK")
  local exit_code=$?

  local got="allow"
  if printf '%s' "$output" | grep -q '"permissionDecision": *"deny"'; then
    got="deny"
  fi

  if [ "$got" = "$expect" ] && [ "$exit_code" -eq 0 ]; then
    echo "PASS [$case_num] $desc"
  else
    echo "FAIL [$case_num] $desc (expected=$expect got=$got exit=$exit_code output=$output)"
    fail_count=$((fail_count + 1))
  fi
}

# --- Rule A: capture-pane polling loops --------------------------------

run_case \
  "deny: while-loop polling tmux capture-pane" \
  'while true; do tmux capture-pane -p -t %3; sleep 5; done' \
  "deny"

run_case \
  "deny: three capture-pane calls chained with &&" \
  'tmux capture-pane -p -t %3 && tmux capture-pane -p -t %3 && tmux capture-pane -p -t %3' \
  "deny"

run_case \
  "allow: single one-off capture-pane before send-keys" \
  'tmux capture-pane -p -t %3 | tail -15' \
  "allow"

run_case \
  "allow: single capture-pane with prose 'for' (no do keyword)" \
  'tmux capture-pane -p -t %3 | grep "waiting for approval"' \
  "allow"

run_case \
  "allow: loop for unrelated setup then one-off capture-pane" \
  'for p in %1 %2; do tmux send-keys -t "$p" C-c; done; tmux capture-pane -p -t %1 | tail -20' \
  "allow"

run_case \
  "allow: rg for the literal string capture-pane inside a loop" \
  'for f in *.md; do rg -c capture-pane "$f"; done' \
  "allow"

run_case \
  "allow: prose mentions of capture-pane in a send-keys payload" \
  'tmux capture-pane -p -t %3 | tail -3 && tmux send-keys -t %3 "note: capture-pane loops denied; single capture-pane fine"' \
  "allow"

run_case \
  "allow: looped send-keys whose payload says tmux capture-pane" \
  'for p in %1 %2; do tmux send-keys -t "$p" "avoid tmux capture-pane"; done' \
  "allow"

run_case \
  "deny: polling via quoted command substitution is still polling" \
  'while true; do x="$(tmux capture-pane -p -t %3)"; sleep 5; done' \
  "deny"

run_case \
  "deny: polling via bash -lc quoted executable code" \
  "while true; do bash -lc 'tmux capture-pane -p -t %3'; sleep 5; done" \
  "deny"

run_case \
  "allow: send-keys prose mentioning bash -lc is data" \
  "tmux send-keys -t %3 'note: bash -lc is risky'" \
  "allow"

run_case \
  "deny: polling via bash -l -c split-flag executable code" \
  "while true; do bash -l -c 'tmux capture-pane -p -t %3'; sleep 5; done" \
  "deny"

run_case \
  "allow: looped send-keys broadcasting a bash -lc capture-pane snippet" \
  'for p in %1 %2; do tmux send-keys -t "$p" "bash -lc '"'"'tmux capture-pane -p -t %3'"'"'"; done' \
  "allow"

run_case \
  "allow: capture-pane sandwiched between two unrelated loops" \
  'for p in %1; do tmux send-keys -t "$p" C-c; done; tmux capture-pane -p -t %1 | tail -20; for p in %2; do echo ok; done' \
  "allow"

# --- Rule B: unbounded rg -----------------------------------------------

run_case \
  "deny: unbounded rg with no bound token" \
  'rg "pattern" src/' \
  "deny"

run_case \
  "allow: rg -c is bounded" \
  'rg -c "pattern" src/' \
  "allow"

run_case \
  "allow: rg piped to head is bounded" \
  'rg "pattern" src/ | head -20' \
  "allow"

run_case \
  "allow: agent-rg.sh wrapper is bounded" \
  'agent-rg.sh pattern src/' \
  "allow"

run_case \
  "allow: cargo build must not false-positive on rg substring" \
  'cargo build' \
  "allow"

run_case \
  "deny: --context must not count as -c bound" \
  'rg TODO --context 3 src/' \
  "deny"

run_case \
  "deny: head bound in a different statement does not cover rg" \
  'rg TODO .; git log --oneline | head -20' \
  "deny"

run_case \
  "allow: head bound in the same pipeline as rg" \
  'rg TODO . | head -20; git log --oneline' \
  "allow"

run_case \
  "allow: rg -m 5 is bounded" \
  'rg -m 5 "pattern" src/' \
  "allow"

run_case \
  "deny: time-prefixed rg is still rg" \
  'time rg TODO .' \
  "deny"

run_case \
  "deny: xargs rg is still rg" \
  'find . -type f | xargs rg TODO' \
  "deny"

run_case \
  "deny: env-prefixed rg is still rg" \
  'env LC_ALL=C rg TODO .' \
  "deny"

run_case \
  "deny: xargs with separate option arg is still rg" \
  'find . -type f | xargs -n 1 rg TODO' \
  "deny"

run_case \
  "deny: rg as if-condition is still rg" \
  'if rg TODO .; then echo hit; fi' \
  "deny"

run_case \
  "deny: rg inside loop body is still rg" \
  'for p in src tests; do rg TODO "$p"; done' \
  "deny"

run_case \
  "allow: xargs rg bounded by head in same pipeline" \
  'find . -type f | xargs rg TODO | head -5' \
  "allow"

run_case \
  "deny: tail -n +1 is not an output cap" \
  'rg TODO . | tail -n +1' \
  "deny"

run_case \
  "deny: sed -n p is not an output cap" \
  'rg TODO . | sed -n p' \
  "deny"

run_case \
  "allow: rg piped to tail -n 5 is bounded" \
  'rg TODO . | tail -n 5' \
  "allow"

run_case \
  "allow: rg piped to tail -20 is bounded" \
  'rg TODO . | tail -20' \
  "allow"

run_case \
  "allow: rg piped to tail -n5 is bounded" \
  'rg TODO . | tail -n5' \
  "allow"

# --- Rule C: long tmux send-keys prompt payloads -------------------------

run_case \
  "deny: long quoted tmux send-keys prompt payload" \
  "tmux send-keys -t %24 'Read /tmp/task.md and complete it exactly, then write the report with the required marker before stopping.' && tmux send-keys -t %24 Enter" \
  "deny"

run_case \
  "deny: true long quoted tmux send-keys prompt payload still blocked" \
  "tmux send-keys -t %24 'This is a deliberately long prompt payload that should still be blocked because tmux send-keys is really being executed here.'" \
  "deny"

run_case \
  "deny: long double-quoted tmux send-keys prompt payload" \
  'tmux send-keys -t %24 "Read /tmp/task.md and complete it exactly, then write the report with the required marker before stopping."' \
  "deny"

run_case \
  "allow: tmux send-keys Enter is allowed" \
  'tmux send-keys -t %24 Enter' \
  "allow"

run_case \
  "allow: tmux send-keys BTab is allowed" \
  'tmux send-keys -t %24 BTab' \
  "allow"

run_case \
  "allow: short tmux send-keys command is allowed" \
  "tmux send-keys -t %24 'pwd'" \
  "allow"

run_case \
  "allow: agent-send-prompt helper is allowed" \
  "~/dotfiles/skills/shared/tmux-orchestration/scripts/agent-send-prompt.sh %24 'Read /tmp/task.md and complete it exactly, then write the report with the required marker before stopping.'" \
  "allow"

run_case \
  "allow: heredoc data containing long tmux send-keys payload" \
  "cat > /tmp/example <<EOF
tmux send-keys -t %24 'Read /tmp/task.md and complete it exactly, then write the report with the required marker before stopping.'
EOF" \
  "allow"

run_case \
  "deny: bash heredoc executor containing long tmux send-keys payload" \
  "bash <<EOF
tmux send-keys -t %24 'Read /tmp/task.md and complete it exactly, then write the report with the required marker before stopping.'
EOF" \
  "deny"

run_case \
  "allow: echo data containing long tmux send-keys payload" \
  "echo \"tmux send-keys -t %24 'Read /tmp/task.md and complete it exactly, then write the report with the required marker before stopping.'\"" \
  "allow"

run_case \
  "allow: short send-keys + long unrelated commit message in another statement" \
  "tmux send-keys -t \"\$TMUX_PANE\" '/rename Fix' Enter && git commit -m \"This is a very long commit message that definitely exceeds eighty characters in length and has nothing to do with send-keys at all\"" \
  "allow"

run_case \
  "allow: short send-keys + long unrelated string in different pipeline segment" \
  "python3 -c 'import json; data = {\"key\": \"value\", \"description\": \"This is a very long description that exceeds eighty characters\"}; print(json.dumps(data))' | tmux send-keys -t %24 '/rename x'" \
  "allow"

run_case \
  "deny: long send-keys payload still blocked after narrowing" \
  "tmux send-keys -t %24 'Read /tmp/task.md and complete it exactly, then write the report with the required marker before stopping.'" \
  "deny"

# --- Fail-open ------------------------------------------------------------

run_case_raw_stdin \
  "allow: non-JSON stdin fails open" \
  'not json at all {{{' \
  "allow"

run_case_raw_stdin \
  "allow: empty stdin fails open" \
  '' \
  "allow"

echo ""
if [ "$fail_count" -eq 0 ]; then
  echo "All $case_num cases PASSED"
  exit 0
else
  echo "$fail_count of $case_num cases FAILED"
  exit 1
fi
