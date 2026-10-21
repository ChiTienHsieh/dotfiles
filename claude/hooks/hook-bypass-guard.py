#!/usr/bin/env python3
"""PreToolUse hook for the Bash tool: deny git hook bypasses.

Denies a git invocation that would skip the repo's hooks:

  - `--no-verify` on a subcommand that runs hooks (commit, push, merge, ...)
  - `-n` where it means --no-verify (`git commit -n`, `git am -n`), including
    combined short flags such as `-nm`; `git push -n` is a dry run and passes
  - `-c core.hooksPath=...` (or `--config-env`) before the subcommand

The command is split into words the way a shell would (shlex), so a quoted
commit message that only mentions --no-verify stays one word and never
matches; heredoc bodies are dropped before lexing for the same reason.

Threat model: an honest agent following a misleading hint, not an
adversary. Wrappers such as `bash -c '...'`, eval, git aliases and
variables are out of scope. Any parsing failure fails OPEN (exit 0, no
output) so a bug here can never block Bash entirely. Known gaps:
abbreviated long options (`--no-veri`) pass, and any word named `git`
starts a check, so `echo git commit -n` is denied too.
"""

import io
import json
import os
import re
import shlex
import sys

REASON = (
    "Bypassing git hooks is not allowed (--no-verify, git commit -n, "
    "-c core.hooksPath=...). When a hook blocks you, fix the code, or fix "
    "the hook itself in its own commit. Only the user can allow a bypass, "
    "one case at a time; if they do, ask them to run the command "
    "themselves. Rule: ~/dotfiles/agents/AGENTS.md."
)

# Subcommands with a --no-verify that skips hooks.
NO_VERIFY_SUBCOMMANDS = {"am", "commit", "merge", "pull", "push", "rebase", "send-email"}

# Subcommands whose -n means --no-verify, mapped to their short options that
# take a value (rest of the cluster, or the next word) and those that take
# only an optional attached value. Needed so `-mn` (message "n") passes.
SHORT_N_SUBCOMMANDS = {
    "am": ("Cp", "S"),
    "commit": ("CFcmt", "Su"),
}

# Long options of those subcommands whose value may be the next word.
LONG_VALUE_OPTIONS = {
    "--author", "--cleanup", "--date", "--file", "--fixup", "--message",
    "--pathspec-from-file", "--reedit-message", "--reuse-message",
    "--squash", "--template", "--trailer",
}

# git global options (before the subcommand) whose value is the next word.
GLOBAL_VALUE_OPTIONS = {
    "-C", "-c", "--attr-source", "--config-env", "--git-dir",
    "--namespace", "--super-prefix", "--work-tree",
}

HEREDOC_RE = re.compile(r"(?<!<)<<(?!<)-?\s*\\?(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\1")
PUNCTUATION = ";&|()<>\n"


class _CommentKeepsNewline(io.StringIO):
    """shlex skips a `# comment` with readline(); leave its newline behind
    so the next line still starts a new statement. A `#` inside a word
    (`fix#1`, `${#a[@]}`, a URL fragment) is no comment in a shell, so skip
    nothing there; shlex then just splits the word at the `#`."""

    lexer = None

    def readline(self, size=-1):
        if self.lexer is not None and self.lexer.state == "a":
            return ""
        line = super().readline(size)
        if line.endswith("\n"):
            self.seek(self.tell() - 1)
            return line[:-1]
        return line


def drop_heredoc_bodies(command):
    """Drop heredoc bodies (data such as commit messages) and terminators."""
    lines = command.split("\n")
    kept = []
    i = 0
    while i < len(lines):
        line = lines[i]
        kept.append(line)
        i += 1
        for match in HEREDOC_RE.finditer(line):
            marker = match.group(2)
            end = i
            while end < len(lines) and lines[end].strip() != marker:
                end += 1
            if end < len(lines):
                i = end + 1
    return "\n".join(kept)


def statements(command):
    """Yield each simple command as a list of words, redirections removed."""
    command = drop_heredoc_bodies(command).replace("\\\n", " ").replace("`", " ; ")
    stream = _CommentKeepsNewline(command)
    lexer = shlex.shlex(stream, posix=True, punctuation_chars=PUNCTUATION)
    stream.lexer = lexer
    lexer.whitespace = " \t\r"
    lexer.whitespace_split = True
    words = []
    skip_next = False
    for token in lexer:
        if token and set(token) <= set(PUNCTUATION):
            if "<" in token or ">" in token:
                skip_next = True  # redirection target: `> file`, `2>&1`
            else:
                if words:
                    yield words
                words = []
            continue
        if skip_next:
            skip_next = False
            continue
        words.append(token)
    if words:
        yield words


def is_hooks_path(config):
    return config.split("=", 1)[0].lower() == "core.hookspath"


def short_cluster_has_n(word, value_letters, optional_letters):
    """Return (has_n, value_is_next_word) for a short-option cluster."""
    letters = word[1:]
    for index, letter in enumerate(letters):
        if letter == "n":
            return True, False
        if letter in value_letters:
            return False, index == len(letters) - 1
        if letter in optional_letters:
            return False, False
    return False, False


def git_bypass(args):
    """Return True when the arguments after `git` bypass hooks."""
    i = 0
    while i < len(args) and args[i].startswith("-"):
        option = args[i]
        if option in ("-c", "--config-env"):
            if i + 1 < len(args) and is_hooks_path(args[i + 1]):
                return True
        elif option.startswith("--config-env="):
            if is_hooks_path(option.split("=", 1)[1]):
                return True
        elif option.startswith("-c") and not option.startswith("--"):
            if is_hooks_path(option[2:]):
                return True
        i += 2 if option in GLOBAL_VALUE_OPTIONS else 1
    if i >= len(args):
        return False

    subcommand = args[i]
    if subcommand not in NO_VERIFY_SUBCOMMANDS:
        return False
    short_options = SHORT_N_SUBCOMMANDS.get(subcommand)
    rest = args[i + 1:]
    j = 0
    while j < len(rest):
        word = rest[j]
        j += 1
        if word == "--":
            break
        if word == "--no-verify":
            return True
        if short_options is None:
            continue
        if word in LONG_VALUE_OPTIONS:
            j += 1
        elif len(word) > 1 and word[0] == "-" and word[1] != "-":
            has_n, value_is_next = short_cluster_has_n(word, *short_options)
            if has_n:
                return True
            if value_is_next:
                j += 1
    return False


def bypasses_hooks(command):
    for words in statements(command):
        for index, word in enumerate(words):
            if os.path.basename(word) == "git" and git_bypass(words[index + 1:]):
                return True
    return False


def main():
    try:
        payload = json.load(sys.stdin)
        command = payload.get("tool_input", {}).get("command")
        if not isinstance(command, str) or not command:
            return 0
        if bypasses_hooks(command):
            print(json.dumps({
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": REASON,
                }
            }))
        return 0
    except Exception:
        return 0


if __name__ == "__main__":
    sys.exit(main())
