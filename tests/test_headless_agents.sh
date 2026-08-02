#!/usr/bin/env bash
set -euo pipefail
unset CLAUDECODE

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
shim="$repo_root/skills/shared/headless-agents/scripts/run-codex-readonly.sh"
template="$repo_root/skills/shared/headless-agents/scripts/run-codex-readonly.template.sh"
installer="$repo_root/claude/scripts/install-headless-codex.py"
guard_source="$repo_root/claude/hooks/bash-helper-guard.py"
temp_base="${TMPDIR:-/tmp}"
temp_root="$(cd "${temp_base%/}" && pwd -P)"
test_tmp="$(mktemp -d "$temp_root/headless-agents-test.XXXXXX")"
runtime_tmp="$(mktemp -d "$temp_root/headless-agents-runtime.XXXXXX")"

cleanup() {
    case "$test_tmp" in
        "$temp_root"/headless-agents-test.*) rm -rf "$test_tmp" ;;
    esac
    case "$runtime_tmp" in
        "$temp_root"/headless-agents-runtime.*) rm -rf "$runtime_tmp" ;;
    esac
}
trap cleanup EXIT
export TMPDIR="$runtime_tmp"

mkdir -p "$test_tmp/trusted-bin" "$test_tmp/shadow-bin"

cat > "$test_tmp/trusted-bin/codex" <<'MOCK'
#!/usr/bin/env bash
set -euo pipefail

mock_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
mock_args="$mock_root/args.txt"
mock_stdin="$mock_root/stdin.txt"
mock_tmpdir_file="$mock_root/runtime-tmp.txt"
mock_exit=0
if [[ -f "$mock_root/mock-exit" ]]; then
    mock_exit="$(< "$mock_root/mock-exit")"
fi

printf '%s\n' "$@" > "$mock_args"
printf '%s\n' "$TMPDIR" > "$mock_tmpdir_file"
cat > "$mock_stdin"

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

if [[ "$mock_exit" != "0" ]]; then
    exit "$mock_exit"
fi

printf 'mock final\n' > "$output_path"
MOCK
chmod +x "$test_tmp/trusted-bin/codex"

cat > "$test_tmp/trusted-bin/claude" <<'MOCK'
#!/usr/bin/env bash
exit 0
MOCK
chmod +x "$test_tmp/trusted-bin/claude"

cat > "$test_tmp/shadow-bin/codex" <<'MOCK'
#!/usr/bin/env bash
printf 'PATH shadow executed\n' > "${SHADOW_MARKER:?}"
exit 99
MOCK
chmod +x "$test_tmp/shadow-bin/codex"

cat > "$test_tmp/shadow-bin/dirname" <<'MOCK'
#!/bin/bash
printf 'caller PATH helper shadow executed\n' > "${SHADOW_HELPER_MARKER:?}"
exit 98
MOCK
chmod +x "$test_tmp/shadow-bin/dirname"

template_copy="$test_tmp/run-codex-readonly.template.sh"
settings_fixture="$test_tmp/settings.json"
launcher="$test_tmp/libexec/run-codex-readonly.sh"
guard_destination="$test_tmp/libexec/bash-helper-guard.py"
artifact_root="$test_tmp/trusted-artifacts"
cp "$template" "$template_copy"
mkdir -p "$(dirname "$launcher")"
ln -s "$template_copy" "$launcher"
cat > "$settings_fixture" <<'JSON'
{
  "custom": {"preserve": true},
  "permissions": {
    "allow": [
      "Bash(ls:*)",
      "Bash(~/.claude/skills/headless-agents/scripts/run-codex-readonly.sh:*)"
    ]
  },
  "hooks": {
    "PreToolUse": [{
      "matcher": "Bash",
      "hooks": [
        {"type": "command", "command": "python3 ~/.claude/hooks/bash-helper-guard.py"},
        {"type": "command", "command": "printf preserve-existing-hook"}
      ]
    }]
  }
}
JSON

/usr/bin/python3 "$installer" \
    --settings "$settings_fixture" \
    --template "$template_copy" \
    --launcher "$launcher" \
    --launcher-command "$launcher" \
    --guard-source "$guard_source" \
    --guard-destination "$guard_destination" \
    --artifact-root "$artifact_root" \
    --trusted-root "$test_tmp" \
    --codex-bin "$test_tmp/trusted-bin/codex" \
    --claude-bin "$test_tmp/trusted-bin/claude" >/dev/null
/usr/bin/python3 "$installer" \
    --settings "$settings_fixture" \
    --template "$template_copy" \
    --launcher "$launcher" \
    --launcher-command "$launcher" \
    --guard-source "$guard_source" \
    --guard-destination "$guard_destination" \
    --artifact-root "$artifact_root" \
    --trusted-root "$test_tmp" \
    --codex-bin "$test_tmp/trusted-bin/codex" \
    --claude-bin "$test_tmp/trusted-bin/claude" >/dev/null

subject="$launcher"
launcher_digest="$(shasum -a 256 "$launcher" | awk '{print $1}')"
printf '\n# source mutation must not alter installed copy\n' >> "$template_copy"
if [[ "$(shasum -a 256 "$launcher" | awk '{print $1}')" != "$launcher_digest" ]]; then
    echo "installed launcher changed with its source template" >&2
    exit 1
fi
if [[ -L "$launcher" || ! -f "$launcher" || ! -x "$launcher" ]]; then
    echo "installed launcher must be a regular copy" >&2
    exit 1
fi

export SHADOW_MARKER="$test_tmp/path-shadow-executed"
export SHADOW_HELPER_MARKER="$test_tmp/helper-shadow-executed"

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

assert_arg_pair() {
    local first="$1"
    local second="$2"
    awk -v first="$first" -v second="$second" '
        previous == first && $0 == second { found = 1 }
        { previous = $0 }
        END { exit(found ? 0 : 1) }
    ' "$MOCK_ARGS" || {
        echo "missing adjacent arguments: $first $second" >&2
        exit 1
    }
}

file_mode() {
    case "$(uname -s)" in
        Darwin) /usr/bin/stat -f '%Lp' "$1" ;;
        *) stat -c '%a' "$1" ;;
    esac
}

if [[ "$(file_mode "$launcher")" != "700" ]]; then
    echo "installed launcher mode must be 700" >&2
    exit 1
fi
if [[ -L "$artifact_root" || ! -d "$artifact_root" || \
      "$(file_mode "$artifact_root")" != "700" ]]; then
    echo "installed artifact root must be a private real directory" >&2
    exit 1
fi
python_real="$(/usr/bin/python3 -c 'import os, sys; print(os.path.realpath(sys.executable))')"
expected_allow_rule="Bash($launcher:*)"
expected_guard_command="$python_real -I $guard_destination"
jq -e --arg allow_rule "$expected_allow_rule" --arg guard_command "$expected_guard_command" '
    .custom.preserve == true and
    ([.permissions.allow[] |
      select(. == $allow_rule)]
      | length) == 1 and
    ([.permissions.allow[] |
      select(. == "Bash(~/.claude/skills/headless-agents/scripts/run-codex-readonly.sh:*)")]
      | length) == 0 and
    ([.hooks.PreToolUse[] |
      select(.matcher == "Bash") | .hooks[] |
      select(.type == "command" and
        .command == $guard_command)]
      | length) == 1 and
    ([.hooks.PreToolUse[] |
      select(.matcher == "Bash") | .hooks[] |
      select(.command == "python3 ~/.claude/hooks/bash-helper-guard.py")]
      | length) == 0 and
    ([.hooks.PreToolUse[] |
      select(.matcher == "Bash") | .hooks[] |
      select(.command == "printf preserve-existing-hook")]
      | length) == 1
' "$settings_fixture" >/dev/null
if [[ -L "$guard_destination" || ! -f "$guard_destination" || \
      ! -x "$guard_destination" || "$(file_mode "$guard_destination")" != "700" ]]; then
    echo "installed guard must be a private regular executable copy" >&2
    exit 1
fi
grep -F "TRUSTED_CODEX_LAUNCHER = \"$launcher\"" "$guard_destination" >/dev/null
trusted_codex_real="$(cd "$test_tmp/trusted-bin" && pwd -P)/codex"
grep -F "$trusted_codex_real" "$launcher" >/dev/null
if grep -Eq 'command -v codex|(^|[[:space:]])codex exec' "$launcher"; then
    echo "installed launcher still resolves Codex through caller PATH" >&2
    exit 1
fi

invalid_settings="$test_tmp/invalid-settings.json"
printf '{ invalid json\n' > "$invalid_settings"
invalid_digest="$(shasum -a 256 "$invalid_settings" | awk '{print $1}')"
set +e
/usr/bin/python3 "$installer" \
    --settings "$invalid_settings" \
    --template "$template" \
    --launcher "$test_tmp/invalid-launcher" \
    --launcher-command "$test_tmp/invalid-launcher" \
    --guard-source "$guard_source" \
    --guard-destination "$guard_destination" \
    --artifact-root "$test_tmp/invalid-artifacts" \
    --trusted-root "$test_tmp" \
    --codex-bin "$test_tmp/trusted-bin/codex" \
    --claude-bin "$test_tmp/trusted-bin/claude" >/dev/null 2>&1
invalid_settings_status=$?
set -e
if [[ "$invalid_settings_status" == "0" || -e "$test_tmp/invalid-launcher" || \
      "$(shasum -a 256 "$invalid_settings" | awk '{print $1}')" != "$invalid_digest" ]]; then
    echo "invalid settings must fail without partial writes" >&2
    exit 1
fi

mkdir -p "$test_tmp/workspace-owned-parent"
ln -s "$test_tmp/workspace-owned-parent" "$test_tmp/unsafe-parent"
set +e
/usr/bin/python3 "$installer" \
    --settings "$settings_fixture" \
    --template "$template" \
    --launcher "$test_tmp/unsafe-parent/run-codex-readonly.sh" \
    --launcher-command "$test_tmp/unsafe-parent/run-codex-readonly.sh" \
    --guard-source "$guard_source" \
    --guard-destination "$guard_destination" \
    --artifact-root "$artifact_root" \
    --trusted-root "$test_tmp" \
    --codex-bin "$test_tmp/trusted-bin/codex" \
    --claude-bin "$test_tmp/trusted-bin/claude" >/dev/null 2>&1
symlink_ancestor_status=$?
set -e
if [[ "$symlink_ancestor_status" == "0" || \
      -e "$test_tmp/workspace-owned-parent/run-codex-readonly.sh" ]]; then
    echo "symlink launcher ancestor must be rejected without a write" >&2
    exit 1
fi

mkdir -p "$test_tmp/trusted-subroot" "$test_tmp/trusted-escape"
set +e
/usr/bin/python3 "$installer" \
    --settings "$settings_fixture" \
    --template "$template" \
    --launcher "$test_tmp/trusted-subroot/../trusted-escape/run-codex-readonly.sh" \
    --launcher-command "$test_tmp/trusted-subroot/../trusted-escape/run-codex-readonly.sh" \
    --guard-source "$guard_source" \
    --guard-destination "$guard_destination" \
    --artifact-root "$test_tmp/trusted-subroot/artifacts" \
    --trusted-root "$test_tmp/trusted-subroot" \
    --codex-bin "$test_tmp/trusted-bin/codex" \
    --claude-bin "$test_tmp/trusted-bin/claude" >/dev/null 2>&1
dotdot_escape_status=$?
set -e
if [[ "$dotdot_escape_status" == "0" || \
      -e "$test_tmp/trusted-escape/run-codex-readonly.sh" ]]; then
    echo "dot-dot launcher escape must be rejected" >&2
    exit 1
fi

ln -s "$test_tmp/trusted-subroot" "$test_tmp/trusted-root-link"
set +e
/usr/bin/python3 "$installer" \
    --settings "$settings_fixture" \
    --template "$template" \
    --launcher "$test_tmp/trusted-root-link/run-codex-readonly.sh" \
    --launcher-command "$test_tmp/trusted-root-link/run-codex-readonly.sh" \
    --guard-source "$guard_source" \
    --guard-destination "$test_tmp/trusted-root-link/bash-helper-guard.py" \
    --artifact-root "$test_tmp/trusted-root-link/artifacts" \
    --trusted-root "$test_tmp/trusted-root-link" \
    --codex-bin "$test_tmp/trusted-bin/codex" \
    --claude-bin "$test_tmp/trusted-bin/claude" >/dev/null 2>&1
symlink_root_status=$?
set -e
if [[ "$symlink_root_status" == "0" || \
      -e "$test_tmp/trusted-subroot/run-codex-readonly.sh" ]]; then
    echo "symlink trusted root must be rejected" >&2
    exit 1
fi

partial_settings="$test_tmp/partial-settings.json"
locked_parent="$test_tmp/locked-parent"
printf '{"permissions":{"allow":["Bash(ls:*)"]}}\n' > "$partial_settings"
partial_digest="$(shasum -a 256 "$partial_settings" | awk '{print $1}')"
mkdir -p "$locked_parent"
chmod 500 "$locked_parent"
set +e
/usr/bin/python3 "$installer" \
    --settings "$partial_settings" \
    --template "$template" \
    --launcher "$locked_parent/run-codex-readonly.sh" \
    --launcher-command "$locked_parent/run-codex-readonly.sh" \
    --guard-source "$guard_source" \
    --guard-destination "$guard_destination" \
    --artifact-root "$artifact_root" \
    --trusted-root "$test_tmp" \
    --codex-bin "$test_tmp/trusted-bin/codex" \
    --claude-bin "$test_tmp/trusted-bin/claude" >/dev/null 2>&1
partial_write_status=$?
set -e
chmod 700 "$locked_parent"
if [[ "$partial_write_status" == "0" || \
      "$(shasum -a 256 "$partial_settings" | awk '{print $1}')" != "$partial_digest" || \
      -e "$locked_parent/run-codex-readonly.sh" ]]; then
    echo "staging failure must not partially publish migration files" >&2
    exit 1
fi

for replace_failure_index in 1 2 3; do
    publish_root="$test_tmp/publish-$replace_failure_index"
    publish_settings="$publish_root/settings.json"
    publish_launcher="$publish_root/libexec/run-codex-readonly.sh"
    publish_guard="$publish_root/libexec/bash-helper-guard.py"
    publish_artifact_root="$publish_root/artifacts"
    mkdir -p "$publish_root/libexec"
    printf '{"permissions":{"allow":["Bash(ls:*)"]}}\n' > "$publish_settings"
    ln -s "$test_tmp/workspace-owned-parent" "$publish_launcher"
    ln -s "$test_tmp/workspace-owned-parent" "$publish_guard"
    publish_digest="$(shasum -a 256 "$publish_settings" | awk '{print $1}')"

    set +e
    /usr/bin/python3 - \
        "$installer" "$replace_failure_index" "$publish_settings" \
        "$template" "$publish_launcher" "$guard_source" "$publish_guard" \
        "$publish_artifact_root" "$publish_root" "$test_tmp/trusted-bin/codex" \
        "$test_tmp/trusted-bin/claude" <<'PY' >/dev/null 2>&1
import importlib.util
import os
from pathlib import Path
import sys

(
    installer_path,
    failure_index,
    settings,
    template,
    launcher,
    guard_source,
    guard_destination,
    artifact_root,
    trusted_root,
    codex,
    claude,
) = sys.argv[1:]
spec = importlib.util.spec_from_file_location("headless_installer", installer_path)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)

real_replace = module.os.replace
replace_count = 0


def injected_replace(source, destination):
    global replace_count
    replace_count += 1
    if replace_count == int(failure_index):
        raise OSError("injected publication failure")
    return real_replace(source, destination)


module.os.replace = injected_replace
sys.argv = [
    installer_path,
    "--settings", settings,
    "--template", template,
    "--launcher", launcher,
    "--launcher-command", launcher,
    "--guard-source", guard_source,
    "--guard-destination", guard_destination,
    "--artifact-root", artifact_root,
    "--trusted-root", trusted_root,
    "--codex-bin", codex,
    "--claude-bin", claude,
]
try:
    module.main()
except OSError as exc:
    if str(exc) != "injected publication failure":
        raise
    raise SystemExit(42)
raise SystemExit("injected os.replace failure did not trigger")
PY
    publish_failure_status=$?
    set -e

    if [[ "$publish_failure_status" != "42" || \
          "$(shasum -a 256 "$publish_settings" | awk '{print $1}')" != "$publish_digest" ]]; then
        echo "publication failure $replace_failure_index changed live settings" >&2
        exit 1
    fi
    if ((replace_failure_index == 3)) && \
       [[ -L "$publish_launcher" || ! -x "$publish_launcher" ]]; then
        echo "launcher was not safely published before settings" >&2
        exit 1
    fi
done

export MOCK_ARGS="$test_tmp/args.txt"
export MOCK_STDIN="$test_tmp/stdin.txt"
export MOCK_TMPDIR_FILE="$test_tmp/runtime-tmp.txt"

bash_env_file="$test_tmp/bash-env.sh"
bash_env_marker="$test_tmp/bash-env-executed"
exported_function_marker="$test_tmp/exported-function-executed"
# shellcheck disable=SC2016 # The test file must expand this in the child Bash.
printf 'printf "BASH_ENV executed\\n" > "$BASH_ENV_MARKER"\n' > "$bash_env_file"
# shellcheck disable=SC2329 # Exported and invoked indirectly by a child Bash.
dirname() {
    printf 'exported function executed\n' > "$EXPORTED_FUNCTION_MARKER"
    return 97
}
export -f dirname
export BASH_ENV_MARKER="$bash_env_marker"
export EXPORTED_FUNCTION_MARKER="$exported_function_marker"

default_result="$(BASH_ENV="$bash_env_file" PATH="$test_tmp/shadow-bin:$PATH" \
    "$subject" --cwd "$repo_root" -- 'Inspect README.md')"
unset -f dirname
if [[ -e "$bash_env_marker" ]]; then
    echo "privileged launcher processed caller BASH_ENV" >&2
    exit 1
fi
if [[ -e "$exported_function_marker" ]]; then
    echo "privileged launcher imported a caller shell function" >&2
    exit 1
fi
if [[ -e "$SHADOW_MARKER" ]]; then
    echo "caller PATH shadow replaced the baked Codex executable" >&2
    exit 1
fi
if [[ -e "$SHADOW_HELPER_MARKER" ]]; then
    echo "caller PATH shadow replaced a trusted launcher helper" >&2
    exit 1
fi

set +e
CLAUDECODE=1 "$subject" --cwd "$repo_root" -- 'Ancestor must be verified' \
    >/dev/null 2>&1
missing_claude_ancestor_status=$?
set -e
if [[ "$missing_claude_ancestor_status" != "2" ]]; then
    echo "CLAUDECODE without a verified Claude ancestor must fail closed" >&2
    exit 1
fi

ancestry_root="$test_tmp/ancestry"
ancestry_project="$ancestry_root/project"
mkdir -p "$ancestry_project" "$ancestry_root/runtime"
cp "$test_tmp/trusted-bin/codex" "$ancestry_project/codex"

codex_runtime_launcher="$ancestry_root/runtime/codex-check.sh"
printf '{}\n' > "$ancestry_root/codex-settings.json"
/usr/bin/python3 "$installer" \
    --settings "$ancestry_root/codex-settings.json" \
    --template "$template" \
    --launcher "$codex_runtime_launcher" \
    --launcher-command "$codex_runtime_launcher" \
    --guard-source "$guard_source" \
    --guard-destination "$ancestry_root/runtime/codex-guard.py" \
    --artifact-root "$ancestry_root/runtime/artifacts" \
    --trusted-root "$test_tmp" \
    --codex-bin "$ancestry_project/codex" \
    --claude-bin /bin/bash >/dev/null
set +e
codex_runtime_error="$(cd "$ancestry_project" && CLAUDECODE=1 /bin/bash -c \
    '"$1" --cwd . -- SHOULD_NOT_RUN' _ "$codex_runtime_launcher" 2>&1)"
codex_runtime_status=$?
set -e
if [[ "$codex_runtime_status" != "2" || \
      "$codex_runtime_error" != *"Trusted runtime is inside the Claude project root: $ancestry_project/codex"* ]]; then
    echo "project-writable baked Codex runtime was not rejected" >&2
    exit 1
fi

grep -F 'mock final' <<< "$default_result" >/dev/null
grep -F '[headless-codex] output=' <<< "$default_result" >/dev/null
grep -F 'Repository facts must be verified with read-only tools' "$MOCK_STDIN" >/dev/null
grep -Fx 'Inspect README.md' "$MOCK_STDIN" >/dev/null
grep -E '/headless-codex-scratch\.[[:alnum:]]+$' "$MOCK_TMPDIR_FILE" >/dev/null
default_scratch_dir="$(< "$MOCK_TMPDIR_FILE")"
if [[ -e "$default_scratch_dir" ]]; then
    echo "model-writable scratch directory was not removed" >&2
    exit 1
fi
default_output="$(sed -n 's/^\[headless-codex\] output=\([^ ]*\) trace=.*/\1/p' <<< "$default_result")"
default_run_dir="$(dirname "$default_output")"
case "$default_run_dir" in
    "$artifact_root"/headless-codex.*) ;;
    *)
        echo "headless artifacts escaped the trusted artifact root" >&2
        exit 1
        ;;
esac
if [[ "$(file_mode "$default_run_dir")" != "700" || \
      "$(file_mode "$default_output")" != "600" ]]; then
    echo "headless artifacts are not private" >&2
    exit 1
fi

assert_arg exec
assert_arg --ignore-user-config
assert_arg --ignore-rules
assert_arg --strict-config
assert_arg --ephemeral
assert_arg --skip-git-repo-check
assert_arg --json
assert_arg_pair -C "$repo_root"
assert_arg_pair -m gpt-5.6-terra
assert_arg_pair -o "$default_output"
assert_arg_pair -c 'model_reasoning_effort="medium"'
assert_arg_pair -c 'approval_policy="never"'
assert_arg_pair -c 'allow_login_shell=false'
assert_arg_pair -c 'project_doc_max_bytes=0'
assert_arg_pair -c 'shell_environment_policy={ inherit="core", ignore_default_excludes=false, include_only=["^(HOME|LANG|LC_[A-Z_]+|LOGNAME|PATH|SHELL|TERM|TMPDIR|USER)$"] }'
assert_arg_pair -c 'web_search="disabled"'
assert_arg_pair -c 'default_permissions="headless-readonly"'
assert_arg_pair -c "permissions.headless-readonly={ description=\"Ephemeral workspace-only read access.\", filesystem={ glob_scan_max_depth=4, \":root\"=\"deny\", \":minimal\"=\"read\", \":tmpdir\"=\"deny\", \":slash_tmp\"=\"deny\", \"/tmp\"=\"deny\", \"/private/tmp\"=\"deny\", \"$artifact_root\"=\"deny\", \"~/.aws\"=\"deny\", \"~/.config\"=\"deny\", \"~/.secrets\"=\"deny\", \"~/.ssh\"=\"deny\", \":workspace_roots\"={ \".\"=\"read\", \".env\"=\"deny\", \".env.*\"=\"deny\", \"**/.env\"=\"deny\", \"**/.env.*\"=\"deny\" } }, network={ enabled=false } }"
for disabled_feature in \
    apps \
    browser_use \
    computer_use \
    goals \
    hooks \
    image_generation \
    memories \
    multi_agent \
    plugins \
    remote_plugin \
    shell_snapshot \
    skill_search \
    tool_suggest \
    workspace_dependencies; do
    assert_arg_pair --disable "$disabled_feature"
done
assert_no_arg --sandbox
assert_no_arg --dangerously-bypass-approvals-and-sandbox
assert_no_arg --search
if [[ "$(head -n 1 "$MOCK_ARGS")" != "exec" || "$(tail -n 1 "$MOCK_ARGS")" != "-" ]]; then
    echo "Codex argv must start with exec and end with stdin marker" >&2
    exit 1
fi

structured_workspace="$test_tmp/structured-workspace"
mkdir -p "$structured_workspace"
prompt_file="$structured_workspace/prompt.txt"
schema_file="$structured_workspace/headless-boundary.schema.json"
printf 'Return structured evidence.\n' > "$prompt_file"
cp "$repo_root/tests/fixtures/headless-boundary.schema.json" "$schema_file"

structured_result="$(cd "$test_tmp" && PATH="$test_tmp/shadow-bin:$PATH" "$subject" \
    --cwd "$structured_workspace" \
    --model gpt-5.6-sol \
    --effort high \
    --schema "$schema_file" \
    --prompt-file "$prompt_file")"

schema_real="$(cd "$(dirname "$schema_file")" && pwd -P)/$(basename "$schema_file")"
assert_arg_pair -C "$structured_workspace"
assert_arg_pair -m gpt-5.6-sol
assert_arg_pair -c 'model_reasoning_effort="high"'
assert_arg_pair --output-schema "$schema_real"
grep -Fx 'Return structured evidence.' "$MOCK_STDIN" >/dev/null
structured_output="$(sed -n 's/^\[headless-codex\] output=\([^ ]*\) trace=.*/\1/p' <<< "$structured_result")"
structured_trace="$(sed -n 's/^\[headless-codex\].* trace=\([^ ]*\) stderr=.*/\1/p' <<< "$structured_result")"
structured_stderr="$(sed -n 's/^\[headless-codex\].* stderr=\(.*\)$/\1/p' <<< "$structured_result")"
grep -Fx 'mock final' "$structured_output" >/dev/null
grep -F 'mock-event' "$structured_trace" >/dev/null
grep -F 'mock stderr' "$structured_stderr" >/dev/null

real_workspace="$test_tmp/real-workspace"
workspace_link="$test_tmp/workspace-link"
mkdir -p "$real_workspace"
ln -s "$real_workspace" "$workspace_link"
(cd "$test_tmp" && PATH="$test_tmp/shadow-bin:$PATH" "$subject" \
    --cwd "$workspace_link" -- 'Canonicalize the workspace') >/dev/null
assert_arg_pair -C "$real_workspace"

set +e
printf '42\n' > "$test_tmp/mock-exit"
PATH="$test_tmp/shadow-bin:$PATH" "$subject" \
    --cwd "$repo_root" \
    -- 'Expected failure' >/dev/null 2>&1
failure_status=$?
rm -f "$test_tmp/mock-exit"
set -e

if [[ "$failure_status" != "42" ]]; then
    echo "expected wrapped exit 42, got $failure_status" >&2
    exit 1
fi

set +e
TMPDIR="$repo_root" PATH="$test_tmp/shadow-bin:$PATH" "$subject" \
    --cwd "$repo_root" \
    -- 'Reject a workspace-local temp root' >/dev/null 2>&1
workspace_tmp_status=$?
set -e

if [[ "$workspace_tmp_status" != "2" ]]; then
    echo "expected workspace TMPDIR rejection, got $workspace_tmp_status" >&2
    exit 1
fi

mkdir -p "$test_tmp/child-workspace"
set +e
(cd "$test_tmp" && \
    TMPDIR="$test_tmp" PATH="$test_tmp/shadow-bin:$PATH" "$subject" \
        --cwd "$test_tmp/child-workspace" \
        -- 'Reject invocation-local temp root for a child workspace') >/dev/null 2>&1
child_workspace_tmp_status=$?
set -e
if [[ "$child_workspace_tmp_status" != "2" ]]; then
    echo "expected invocation-root TMPDIR rejection for child workspace" >&2
    exit 1
fi

set +e
PATH="$test_tmp/shadow-bin:$PATH" "$subject" \
    --cwd "$test_tmp" \
    -- 'Reject a workspace outside the invocation root' >/dev/null 2>&1
outside_workspace_status=$?
set -e

if [[ "$outside_workspace_status" != "2" ]]; then
    echo "expected outside workspace rejection, got $outside_workspace_status" >&2
    exit 1
fi

set +e
(cd "$test_tmp" && PATH="$test_tmp/shadow-bin:$PATH" "$subject" \
    --cwd "$artifact_root" \
    -- 'Reject the trusted artifact root as a workspace') >/dev/null 2>&1
artifact_workspace_status=$?
set -e
if [[ "$artifact_workspace_status" != "2" ]]; then
    echo "expected artifact/workspace overlap rejection" >&2
    exit 1
fi

set +e
PATH="$test_tmp/shadow-bin:$PATH" "$subject" \
    --cwd "$repo_root" \
    --prompt-file "$prompt_file" >/dev/null 2>&1
outside_prompt_status=$?
PATH="$test_tmp/shadow-bin:$PATH" "$subject" \
    --cwd "$repo_root" \
    --schema "$schema_file" \
    -- 'Reject outside schema' >/dev/null 2>&1
outside_schema_status=$?
set -e

if [[ "$outside_prompt_status" != "2" || "$outside_schema_status" != "2" ]]; then
    echo "expected outside input-file rejection" >&2
    exit 1
fi

printf 'must not become a prompt\n' > "$test_tmp/.env"
printf '{}\n' > "$test_tmp/child-workspace/.env.schema.json"
set +e
(cd "$test_tmp" && PATH="$test_tmp/shadow-bin:$PATH" "$subject" \
    --cwd "$test_tmp/child-workspace" \
    --prompt-file "$test_tmp/.env") >/dev/null 2>&1
sibling_env_prompt_status=$?
(cd "$test_tmp" && PATH="$test_tmp/shadow-bin:$PATH" "$subject" \
    --cwd "$test_tmp/child-workspace" \
    --schema "$test_tmp/child-workspace/.env.schema.json" \
    -- 'Reject env-like schema') >/dev/null 2>&1
workspace_env_schema_status=$?
set -e
if [[ "$sibling_env_prompt_status" != "2" || \
      "$workspace_env_schema_status" != "2" ]]; then
    echo "expected workspace and .env input boundaries to reject files" >&2
    exit 1
fi

ln -s "$prompt_file" "$structured_workspace/prompt-link.txt"
ln -s "$schema_file" "$structured_workspace/schema-link.json"
set +e
(cd "$test_tmp" && PATH="$test_tmp/shadow-bin:$PATH" "$subject" \
    --cwd "$structured_workspace" \
    --prompt-file "$structured_workspace/prompt-link.txt") >/dev/null 2>&1
symlink_prompt_status=$?
(cd "$test_tmp" && PATH="$test_tmp/shadow-bin:$PATH" "$subject" \
    --cwd "$structured_workspace" \
    --schema "$structured_workspace/schema-link.json" \
    -- 'Reject symlink schema') >/dev/null 2>&1
symlink_schema_status=$?
set -e
if [[ "$symlink_prompt_status" != "2" || "$symlink_schema_status" != "2" ]]; then
    echo "expected symlink input-file rejection" >&2
    exit 1
fi

set +e
PATH="$test_tmp/shadow-bin:$PATH" "$subject" \
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
    PATH="$test_tmp/shadow-bin:$PATH" "$subject" \
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

bash -n "$subject" "$shim" "$template" \
    "$repo_root/tests/test_headless_agents_live.sh" \
    "$repo_root/tests/test_headless_agents_claude.sh"
bash -n "$repo_root/install.sh"
/usr/bin/python3 "$installer" --help >/dev/null
"$subject" --help >/dev/null
jq -e '
    (.permissions.allow |
      index("Bash(~/.local/libexec/dotfiles/run-codex-readonly.sh:*)") != null) and
    (.permissions.allow |
      index("Bash(~/.claude/skills/headless-agents/scripts/run-codex-readonly.sh:*)") == null) and
    ([.hooks.PreToolUse[] |
      select(.matcher == "Bash") | .hooks[] |
      select(.type == "command" and
        .command == "/usr/bin/python3 -I ~/.local/libexec/dotfiles/bash-helper-guard.py")]
      | length) == 1
' "$repo_root/claude/settings.json" >/dev/null
jq empty "$repo_root/tests/fixtures/headless-boundary.schema.json"
"$repo_root/claude/hooks/test-bash-helper-guard.sh" >/dev/null

echo "headless-agents tests passed"
