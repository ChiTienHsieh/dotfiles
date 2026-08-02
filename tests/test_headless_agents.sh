#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
subject="$repo_root/skills/shared/headless-agents/scripts/run-codex-readonly.sh"
test_tmp="$(mktemp -d "${TMPDIR:-/tmp}/headless-agents-test.XXXXXX")"

cleanup() {
    case "$test_tmp" in
        "${TMPDIR:-/tmp}"/headless-agents-test.*) rm -rf "$test_tmp" ;;
    esac
}
trap cleanup EXIT

mkdir -p "$test_tmp/bin"

cat > "$test_tmp/bin/codex" <<'MOCK'
#!/usr/bin/env bash
set -euo pipefail

: "${MOCK_ARGS:?}"
: "${MOCK_STDIN:?}"
: "${MOCK_TMPDIR_FILE:?}"

printf '%s\n' "$@" > "$MOCK_ARGS"
printf '%s\n' "$TMPDIR" > "$MOCK_TMPDIR_FILE"
cat > "$MOCK_STDIN"

output_path=""
while (($#)); do
    if [[ "$1" == "-o" ]]; then
        output_path="${2:?}"
        shift 2
    else
        shift
    fi
done

printf 'mock stderr\n' >&2
printf '{"type":"mock-event"}\n'

if [[ "${MOCK_EXIT:-0}" != "0" ]]; then
    exit "$MOCK_EXIT"
fi

printf 'mock final\n' > "$output_path"
MOCK
chmod +x "$test_tmp/bin/codex"

assert_arg() {
    local expected="$1"
    grep -Fx -- "$expected" "$MOCK_ARGS" >/dev/null || {
        echo "missing argument: $expected" >&2
        exit 1
    }
}

assert_no_arg() {
    local unexpected="$1"
    if grep -Fx -- "$unexpected" "$MOCK_ARGS" >/dev/null; then
        echo "unexpected argument: $unexpected" >&2
        exit 1
    fi
}

file_mode() {
    case "$(uname -s)" in
        Darwin) /usr/bin/stat -f '%Lp' "$1" ;;
        *) stat -c '%a' "$1" ;;
    esac
}

export MOCK_ARGS="$test_tmp/args.txt"
export MOCK_STDIN="$test_tmp/stdin.txt"
export MOCK_TMPDIR_FILE="$test_tmp/runtime-tmp.txt"

default_result="$(PATH="$test_tmp/bin:$PATH" "$subject" --cwd "$repo_root" -- 'Inspect README.md')"
grep -F 'mock final' <<< "$default_result" >/dev/null
grep -F '[headless-codex] output=' <<< "$default_result" >/dev/null
grep -F 'Repository facts must be verified with read-only tools' "$MOCK_STDIN" >/dev/null
grep -Fx 'Inspect README.md' "$MOCK_STDIN" >/dev/null
grep -E '/headless-codex\.[[:alnum:]]+$' "$MOCK_TMPDIR_FILE" >/dev/null
default_run_dir="$(< "$MOCK_TMPDIR_FILE")"
default_output="$(sed -n 's/^\[headless-codex\] output=\([^ ]*\) trace=.*/\1/p' <<< "$default_result")"
if [[ "$(file_mode "$default_run_dir")" != "700" || "$(file_mode "$default_output")" != "600" ]]; then
    echo "headless artifacts are not private" >&2
    exit 1
fi

assert_arg exec
assert_arg --ignore-user-config
assert_arg --strict-config
assert_arg --ephemeral
assert_arg --skip-git-repo-check
assert_arg --json
assert_arg gpt-5.6-terra
assert_arg 'model_reasoning_effort="medium"'
assert_arg 'approval_policy="never"'
assert_arg 'allow_login_shell=false'
assert_arg 'project_doc_max_bytes=0'
assert_arg 'shell_environment_policy={ inherit="core", ignore_default_excludes=false, include_only=["^(HOME|LANG|LC_[A-Z_]+|LOGNAME|PATH|SHELL|TERM|TMPDIR|USER)$"] }'
assert_arg 'web_search="disabled"'
assert_arg 'default_permissions="headless-readonly"'
assert_arg 'permissions.headless-readonly={ description="Ephemeral workspace-only read access.", filesystem={ glob_scan_max_depth=4, ":root"="deny", ":minimal"="read", ":tmpdir"="deny", ":slash_tmp"="deny", "/tmp"="deny", "/private/tmp"="deny", "~/.aws"="deny", "~/.config"="deny", "~/.secrets"="deny", "~/.ssh"="deny", ":workspace_roots"={ "."="read", ".env"="deny", ".env.*"="deny", "**/.env"="deny", "**/.env.*"="deny" } }, network={ enabled=false } }'
assert_arg apps
assert_arg browser_use
assert_arg computer_use
assert_arg hooks
assert_arg multi_agent
assert_arg plugins
assert_arg shell_snapshot
assert_arg skill_search
assert_arg tool_suggest
assert_arg workspace_dependencies
assert_no_arg --sandbox
assert_no_arg --dangerously-bypass-approvals-and-sandbox
assert_no_arg --search

prompt_file="$test_tmp/prompt.txt"
schema_file="$test_tmp/headless-boundary.schema.json"
printf 'Return structured evidence.\n' > "$prompt_file"
cp "$repo_root/tests/fixtures/headless-boundary.schema.json" "$schema_file"

structured_result="$(cd "$test_tmp" && PATH="$test_tmp/bin:$PATH" "$subject" \
    --cwd "$test_tmp" \
    --model gpt-5.6-sol \
    --effort high \
    --schema "$schema_file" \
    --prompt-file "$prompt_file")"

assert_arg gpt-5.6-sol
assert_arg 'model_reasoning_effort="high"'
assert_arg --output-schema
schema_real="$(cd "$(dirname "$schema_file")" && pwd -P)/$(basename "$schema_file")"
assert_arg "$schema_real"
grep -Fx 'Return structured evidence.' "$MOCK_STDIN" >/dev/null
structured_output="$(sed -n 's/^\[headless-codex\] output=\([^ ]*\) trace=.*/\1/p' <<< "$structured_result")"
structured_trace="$(sed -n 's/^\[headless-codex\].* trace=\([^ ]*\) stderr=.*/\1/p' <<< "$structured_result")"
structured_stderr="$(sed -n 's/^\[headless-codex\].* stderr=\(.*\)$/\1/p' <<< "$structured_result")"
grep -Fx 'mock final' "$structured_output" >/dev/null
grep -F 'mock-event' "$structured_trace" >/dev/null
grep -F 'mock stderr' "$structured_stderr" >/dev/null

set +e
PATH="$test_tmp/bin:$PATH" MOCK_EXIT=42 "$subject" \
    --cwd "$repo_root" \
    -- 'Expected failure' >/dev/null 2>&1
failure_status=$?
set -e

if [[ "$failure_status" != "42" ]]; then
    echo "expected wrapped exit 42, got $failure_status" >&2
    exit 1
fi

set +e
TMPDIR="$repo_root" PATH="$test_tmp/bin:$PATH" "$subject" \
    --cwd "$repo_root" \
    -- 'Reject a workspace-local temp root' >/dev/null 2>&1
workspace_tmp_status=$?
set -e

if [[ "$workspace_tmp_status" != "2" ]]; then
    echo "expected workspace TMPDIR rejection, got $workspace_tmp_status" >&2
    exit 1
fi

set +e
PATH="$test_tmp/bin:$PATH" "$subject" \
    --cwd "$test_tmp" \
    -- 'Reject a workspace outside the invocation root' >/dev/null 2>&1
outside_workspace_status=$?
set -e

if [[ "$outside_workspace_status" != "2" ]]; then
    echo "expected outside workspace rejection, got $outside_workspace_status" >&2
    exit 1
fi

set +e
PATH="$test_tmp/bin:$PATH" "$subject" \
    --cwd "$repo_root" \
    --prompt-file "$prompt_file" >/dev/null 2>&1
outside_prompt_status=$?
PATH="$test_tmp/bin:$PATH" "$subject" \
    --cwd "$repo_root" \
    --schema "$schema_file" \
    -- 'Reject outside schema' >/dev/null 2>&1
outside_schema_status=$?
set -e

if [[ "$outside_prompt_status" != "2" || "$outside_schema_status" != "2" ]]; then
    echo "expected outside input-file rejection" >&2
    exit 1
fi

set +e
PATH="$test_tmp/bin:$PATH" "$subject" \
    --cwd "$repo_root" \
    --output "$repo_root/should-not-exist.md" \
    -- 'Custom artifact paths are unsupported' >/dev/null 2>&1
custom_artifact_status=$?
set -e

if [[ "$custom_artifact_status" != "2" || -e "$repo_root/should-not-exist.md" ]]; then
    echo "expected custom artifact option rejection without a workspace write" >&2
    exit 1
fi

for invalid_option in \
    '--effort|medium"; approval_policy="on-request' \
    '--model|gpt-5.6-terra"'; do
    option_name="${invalid_option%%|*}"
    option_value="${invalid_option#*|}"
    set +e
    PATH="$test_tmp/bin:$PATH" "$subject" \
        --cwd "$repo_root" \
        "$option_name" "$option_value" \
        -- 'Reject unsafe option input' >/dev/null 2>&1
    invalid_option_status=$?
    set -e
    if [[ "$invalid_option_status" != "2" ]]; then
        echo "expected $option_name validation failure, got $invalid_option_status" >&2
        exit 1
    fi
done

bash -n "$subject"
"$subject" --help >/dev/null
jq -e '
    .permissions.allow |
    index("Bash(~/.claude/skills/headless-agents/scripts/run-codex-readonly.sh:*)") != null
' "$repo_root/claude/settings.json" >/dev/null

echo "headless-agents tests passed"
