#!/usr/bin/env python3
"""PreToolUse hook for the Bash tool.

Denies two classes of commands that should route through the
tmux-orchestration helper scripts instead of being hand-rolled:

  Rule A: polling loops around `tmux capture-pane` (or 3+ manually
          unrolled capture-pane calls in one command) -> use
          agent-watch-marker.sh instead of busy-polling a pane.

  Rule B: unbounded `rg` invocations with no output cap -> add a bound
          (-c/-m/head/...) or use agent-rg.sh.

  Rule C: hand-written `tmux send-keys` with a long quoted prompt payload
          -> use agent-send-prompt.sh, which verifies paste and submit.

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

AGENT_SEND_PROMPT_HINT = (
    "Long tmux send-keys payload detected (quoted string >= 80 characters). "
    "Use ~/dotfiles/skills/shared/tmux-orchestration/scripts/agent-send-prompt.sh "
    "PANE 'ONE-LINE PROMPT' so the paste and Enter submission are verified. "
    "Short keys such as Enter/BTab and short commands are allowed."
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
LONG_SEND_KEYS_PAYLOAD_CHARS = 80
TMUX_SEND_KEYS_RE = re.compile(r"\btmux\s[^;&|\n]*\bsend-keys\b")
HEREDOC_RE = re.compile(r"<<-?\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\1")
HEREDOC_EXECUTOR_RE = re.compile(
    r"^\s*(?:\w+=\S+\s+)*(?:command\s+|time\s+|env\s+(?:-\S+\s+)*|sudo\s+)*"
    r"(?:ba|z)?sh\b|^\s*(?:\w+=\S+\s+)*(?:command\s+|time\s+|env\s+(?:-\S+\s+)*|sudo\s+)*"
    r"(?:eval|python[0-9.]*)\b"
)
HEREDOC_DATA_SINK_RE = re.compile(
    r"^\s*(?:\w+=\S+\s+)*(?:command\s+|time\s+|env\s+(?:-\S+\s+)*|sudo\s+)*"
    r"(?:cat|tee)\b|^\s*(?::|true)\s*(?:>|>>)"
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


def strip_heredoc_bodies(command):
    """Remove simple data heredoc bodies so data lines are not commands.

    This is intentionally small, matching the hook's existing shell-lite
    parsing style. Bodies fed to executors such as bash/sh/zsh/eval/python stay
    visible to the rule; bodies fed to data sinks such as cat/tee are stripped.
    """
    lines = command.splitlines()
    output = []
    i = 0
    while i < len(lines):
        line = lines[i]
        output.append(line)
        markers = []
        for statement in STATEMENT_SPLIT_RE.split(line):
            if not HEREDOC_RE.search(statement):
                continue
            if HEREDOC_EXECUTOR_RE.search(statement):
                continue
            if HEREDOC_DATA_SINK_RE.search(statement):
                markers.extend(match.group(2) for match in HEREDOC_RE.finditer(statement))
        i += 1
        for marker in markers:
            while i < len(lines):
                if lines[i].strip() == marker:
                    output.append(lines[i])
                    i += 1
                    break
                output.append("")
                i += 1
    return "\n".join(output)

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


def unquote_shell_literal(literal):
    if len(literal) >= 2 and literal[0] == literal[-1] and literal[0] in "'\"":
        return literal[1:-1]
    return literal


def check_long_tmux_send_keys_payload(command):
    """Detect hand-written long quoted prompt payloads sent via tmux send-keys.

    This deliberately targets simple quoted prompt strings. It leaves normal
    key sends (`Enter`, `BTab`), short commands, and the dedicated helper alone.
    """
    command = strip_heredoc_bodies(command)
    for statement in STATEMENT_SPLIT_RE.split(command):
        if "agent-send-prompt.sh" in statement:
            continue
        executable_statement = strip_data_quotes(statement)
        if not TMUX_SEND_KEYS_RE.search(executable_statement):
            continue
        for match in QUOTED_RE.finditer(statement):
            payload = unquote_shell_literal(match.group(0))
            if len(payload) >= LONG_SEND_KEYS_PAYLOAD_CHARS:
                return True
    return False


def main():
    try:
        payload = json.load(sys.stdin)
        command = payload.get("tool_input", {}).get("command")
        if not isinstance(command, str) or not command:
            return 0
        if check_long_tmux_send_keys_payload(command):
            deny(AGENT_SEND_PROMPT_HINT)
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
