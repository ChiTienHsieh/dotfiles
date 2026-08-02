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

export MOCK_ARGS="$test_tmp/args.txt"
export MOCK_STDIN="$test_tmp/stdin.txt"
export MOCK_TMPDIR_FILE="$test_tmp/runtime-tmp.txt"

default_result="$(PATH="$test_tmp/bin:$PATH" "$subject" --cwd "$repo_root" -- 'Inspect README.md')"
grep -F 'mock final' <<< "$default_result" >/dev/null
grep -F '[headless-codex] output=' <<< "$default_result" >/dev/null
grep -F 'Repository facts must be verified with read-only tools' "$MOCK_STDIN" >/dev/null
grep -Fx 'Inspect README.md' "$MOCK_STDIN" >/dev/null
grep -E '/headless-codex\.[[:alnum:]]+$' "$MOCK_TMPDIR_FILE" >/dev/null

assert_arg exec
assert_arg --ignore-user-config
assert_arg --strict-config
assert_arg --ephemeral
assert_arg --skip-git-repo-check
assert_arg --json
assert_arg gpt-5.6-terra
assert_arg 'model_reasoning_effort="medium"'
assert_arg 'approval_policy="never"'
assert_arg 'project_doc_max_bytes=0'
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
schema_file="$test_tmp/schema.json"
output_file="$test_tmp/custom/final.json"
trace_file="$test_tmp/custom/events.jsonl"
stderr_file="$test_tmp/custom/stderr.log"
printf 'Return structured evidence.\n' > "$prompt_file"
printf '{"type":"object"}\n' > "$schema_file"

PATH="$test_tmp/bin:$PATH" "$subject" \
    --cwd "$repo_root" \
    --model gpt-5.6-sol \
    --effort high \
    --output "$output_file" \
    --trace "$trace_file" \
    --stderr "$stderr_file" \
    --schema "$schema_file" \
    --prompt-file "$prompt_file" >/dev/null

assert_arg gpt-5.6-sol
assert_arg 'model_reasoning_effort="high"'
assert_arg --output-schema
assert_arg "$schema_file"
grep -Fx 'Return structured evidence.' "$MOCK_STDIN" >/dev/null
grep -Fx 'mock final' "$output_file" >/dev/null
grep -F 'mock-event' "$trace_file" >/dev/null
grep -F 'mock stderr' "$stderr_file" >/dev/null

set +e
PATH="$test_tmp/bin:$PATH" MOCK_EXIT=42 "$subject" \
    --cwd "$repo_root" \
    --output "$test_tmp/fail-final.md" \
    --trace "$test_tmp/fail-events.jsonl" \
    --stderr "$test_tmp/fail-stderr.log" \
    -- 'Expected failure' >/dev/null 2>&1
failure_status=$?
set -e

if [[ "$failure_status" != "42" ]]; then
    echo "expected wrapped exit 42, got $failure_status" >&2
    exit 1
fi

set +e
PATH="$test_tmp/bin:$PATH" "$subject" \
    --cwd "$repo_root" \
    --output "$repo_root/headless-test-output.md" \
    -- 'Reject workspace artifact' >/dev/null 2>&1
workspace_artifact_status=$?
set -e

if [[ "$workspace_artifact_status" != "2" ]]; then
    echo "expected workspace artifact rejection, got $workspace_artifact_status" >&2
    exit 1
fi

bash -n "$subject"
"$subject" --help >/dev/null

echo "headless-agents tests passed"
