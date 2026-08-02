#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
template="$repo_root/skills/shared/headless-agents/scripts/run-codex-readonly.template.sh"
installer="$repo_root/claude/scripts/install-headless-codex.py"
test_tmp="$(mktemp -d "${TMPDIR:-/tmp}/headless-agents-claude.XXXXXX")"
settings="$test_tmp/settings.json"
launcher="$test_tmp/run-codex-readonly.sh"

cleanup() {
    case "$test_tmp" in
        "${TMPDIR:-/tmp}"/headless-agents-claude.*) rm -rf "$test_tmp" ;;
    esac
}
trap cleanup EXIT

command -v claude >/dev/null 2>&1 || {
    echo "claude is not available on PATH" >&2
    exit 127
}

printf '{}\n' > "$settings"
/usr/bin/python3 "$installer" \
    --settings "$settings" \
    --template "$template" \
    --launcher "$launcher" >/dev/null

settings_tmp="$test_tmp/settings.tmp"
jq --arg launcher_rule "Bash($launcher:*)" '
    .permissions.allow += [
      $launcher_rule,
      "Bash(cd /private/tmp:*)"
    ] |
    .permissions.allow |= unique |
    .permissions.defaultMode = "auto" |
    .sandbox = {"enabled": true}
' "$settings" > "$settings_tmp"
mv "$settings_tmp" "$settings"

normal_prompt="Run exactly this Bash command and set dangerouslyDisableSandbox to true on that Bash tool call: $launcher --cwd \"\$PWD\" -- \"Read README.md and return its first Markdown heading exactly.\" Return the child command's final answer only."
normal_output="$(cd "$repo_root" && claude -p \
    --model haiku \
    --permission-mode auto \
    --allowedTools Bash \
    --settings "$settings" \
    --no-session-persistence \
    "$normal_prompt")"
grep -F '# Dotfiles' <<< "$normal_output" >/dev/null || {
    echo "Claude -> Codex integration did not return the repository heading" >&2
    printf '%s\n' "$normal_output" >&2
    exit 1
}

escape_prompt="Run exactly this Bash command and set dangerouslyDisableSandbox to true on that Bash tool call: cd /private/tmp && $launcher --cwd . -- \"Return only ESCAPE_SHOULD_NOT_RUN.\" Report the command's exact error without retrying or changing it."
escape_output="$(cd "$repo_root" && claude -p \
    --model haiku \
    --permission-mode auto \
    --allowedTools Bash \
    --settings "$settings" \
    --no-session-persistence \
    "$escape_prompt")"
grep -F 'Invocation directory escaped the Claude project root' \
    <<< "$escape_output" >/dev/null || {
    echo "Claude project-root escape was not rejected" >&2
    printf '%s\n' "$escape_output" >&2
    exit 1
}

echo "headless-agents Claude integration test passed"
