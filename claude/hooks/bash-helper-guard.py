#!/usr/bin/env python3
"""PreToolUse hook for the Bash tool.

Denies two classes of commands that should route through the
tmux-orchestration helper scripts instead of being hand-rolled:

  Rule A: polling loops around `tmux capture-pane` (or 3+ manually
          unrolled capture-pane calls in one command) -> use
          agent-watch-marker.sh instead of busy-polling a pane.

  Rule B: unbounded `rg` invocations with no output cap -> add a bound
          (-c/-m/head/...) or use agent-rg.sh.

Reads the PreToolUse payload from stdin as JSON, inspects
`tool_input.command`, and prints a deny decision as JSON on stdout when a
rule matches. Any parsing failure or unexpected shape fails OPEN (exit 0,
no output) so a bug in this hook can never block Bash entirely.
"""

import json
import re
import sys

WATCH_MARKER_HINT = (
    "Repeated/looping tmux capture-pane calls are not allowed. Use "
    "~/dotfiles/skills/shared/tmux-orchestration/scripts/agent-watch-marker.sh "
    "REPORT_PATH [MARKER] --timeout SECS to poll a marker file instead of "
    "capturing the pane in a loop. A single one-off capture-pane (e.g. "
    "checking for a dialog right before send-keys) is fine."
)

AGENT_RG_HINT = (
    "Unbounded rg call with no output cap. Add a bound such as "
    "'| head -n 50' or '-m N', or use "
    "~/dotfiles/skills/shared/tmux-orchestration/scripts/agent-rg.sh PATTERN PATH "
    "(defaults to --count-matches; --files lists filenames; --full REASON "
    "for full output)."
)

# A capture-pane INSIDE a loop body: between `do` and a later `done`.
# Scoping to the do...done span (instead of "loop keyword anywhere +
# capture-pane anywhere") allows commands that loop for unrelated setup
# and then do one legitimate capture-pane afterwards, and avoids prose
# false positives like `grep "waiting for approval"`.
LOOP_BODY_CAPTURE_RE = re.compile(
    r"\bdo\b(?:(?!\bdone\b).)*?tmux\s[^;&|]*capture-pane", re.S
)
# Quoted string literals are usually data/message payloads, not commands.
# They are stripped before any rule runs, so prose (e.g. a send-keys
# announcement that mentions capture-pane, 2026-07-04 incident) never
# triggers rules.
#
# EXCEPT: keep quoted spans that contain command substitution ($( or
# backtick), or that immediately follow a shell/eval execution prefix such
# as `bash -lc '...'` or `eval '...'`. Those quotes hold executable code.
# Still out of scope: deliberately evasive wrappers, escaped/nested quotes,
# and complete shell grammar.
QUOTED_RE = re.compile(r"'[^']*'|\"[^\"]*\"")
EXEC_QUOTE_PREFIX_RE = re.compile(
    r"(?:\b(?:ba|z)?sh\s+(?:-\S+\s+)*-\S*c|\beval)\s*$"
)


def strip_data_quotes(command):
    def replace(match):
        span = match.group(0)
        if "$(" in span or "`" in span:
            return span
        prefix = command[: match.start()]
        # Precedence: inside a send-keys statement everything quoted is
        # payload data for another pane, even if it textually looks like
        # `bash -lc '...'`. The exec-prefix exception applies only when
        # the quote is NOT a send-keys argument.
        statement_prefix = STATEMENT_SPLIT_RE.split(prefix)[-1]
        if "send-keys" in statement_prefix:
            return " "
        if EXEC_QUOTE_PREFIX_RE.search(prefix):
            return span
        return " "

    return QUOTED_RE.sub(replace, command)

# Count real `tmux ... capture-pane` invocations, not the literal string.
TMUX_CAPTURE_RE = re.compile(r"tmux\s[^;&|]*capture-pane")

# Statement separators: `;`, `&&`, `||`, newline. Not a full shell parser;
# separators inside quotes may over-split, which is an accepted error --
# it only shifts which segment a token lands in, and the fail-open spirit
# still holds.
STATEMENT_SPLIT_RE = re.compile(r"\|\||&&|[;\n]")

# An `rg` invocation within one pipeline segment: at segment start, or
# right after `$(` / backtick command substitution, optionally behind
# common wrappers (time/command/nice/sudo/xargs, env assignments). Avoids
# false positives on substrings like `cargo` or `.rg`; `agent-rg.sh ...`
# never starts a segment with `rg`, so it is naturally exempt. This is a
# nudge, not a security boundary: exotic evasion (eval, bash -c) is out
# of scope by design.
RG_SEGMENT_RE = re.compile(
    r"(?:^|\$\(|`)\s*"
    r"(?:(?:if|elif|then|else|do|while|until)\s+)*"
    r"(?:(?:command|time|nice|sudo|xargs|env)\s+(?:-\S+(?:\s+\S+)?\s+)*|\w+=\S*\s+)*"
    r"rg\b"
)

# Bound flags matched with token boundaries (NOT whole-command substring
# search), so e.g. `--context` no longer counts as `-c`.
BOUND_FLAG_RES = [
    re.compile(r"(?:^|\s)-(?:c|l|q)(?:\s|$)"),
    re.compile(r"(?:^|\s)-m\s*\d"),
    re.compile(r"--count(?:-matches)?\b"),
    re.compile(r"--files(?:-with-matches)?\b"),
    re.compile(r"--max-count\b"),
    re.compile(r"--quiet\b"),
]

HEAD_LIMITER_RE = re.compile(r"^\s*head\b")
WC_LIMITER_RE = re.compile(r"^\s*wc\b")
GREP_COUNT_LIMITER_RE = re.compile(r"^\s*grep\s+-c\b")
TAIL_LIMITER_RE = re.compile(
    r"^\s*tail(?:\s*$|\s+-\d+\b|\s+-n\s*\d+\b|\s+--lines[=\s]\d+\b)"
)


def is_limiter_segment(segment):
    """Return whether a downstream pipeline segment bounds output volume."""
    return any(
        limiter.search(segment)
        for limiter in (
            HEAD_LIMITER_RE,
            WC_LIMITER_RE,
            GREP_COUNT_LIMITER_RE,
            TAIL_LIMITER_RE,
        )
    )


def deny(reason):
    output = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }
    print(json.dumps(output))


def check_capture_pane_loop(command):
    if not TMUX_CAPTURE_RE.search(command):
        return False
    if LOOP_BODY_CAPTURE_RE.search(command):
        return True
    if len(TMUX_CAPTURE_RE.findall(command)) >= 3:
        return True
    return False


def check_unbounded_rg(command):
    """Per-pipeline-segment bound check.

    Split into statements (`;`, `&&`, `||`, newline), then each statement
    into pipeline segments on `|`. An rg segment is bounded only if the
    segment itself carries a bound flag, or a LATER segment of the same
    pipeline is an output limiter (head/tail/wc/...). A bound in a
    different statement does not count.
    """
    for statement in STATEMENT_SPLIT_RE.split(command):
        segments = statement.split("|")
        for i, segment in enumerate(segments):
            if not RG_SEGMENT_RE.search(segment):
                continue
            if any(flag.search(segment) for flag in BOUND_FLAG_RES):
                continue
            if any(is_limiter_segment(later) for later in segments[i + 1:]):
                continue
            return True
    return False


def main():
    try:
        payload = json.load(sys.stdin)
        command = payload.get("tool_input", {}).get("command")
        if not isinstance(command, str) or not command:
            return 0
        command = strip_data_quotes(command)

        if check_capture_pane_loop(command):
            deny(WATCH_MARKER_HINT)
            return 0

        if check_unbounded_rg(command):
            deny(AGENT_RG_HINT)
            return 0

        return 0
    except Exception:
        return 0


if __name__ == "__main__":
    sys.exit(main())
