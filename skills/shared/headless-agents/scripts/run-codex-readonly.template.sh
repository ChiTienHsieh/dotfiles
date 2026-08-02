#!/usr/bin/env bash
set -euo pipefail

# Replaced with shell-quoted, canonical executable paths by
# claude/scripts/install-headless-codex.py. This template is never the
# permissioned launcher itself.
codex_bin=@CODEX_BIN@
claude_bin=@CLAUDE_BIN@

usage() {
    cat <<'EOF'
Usage:
  run-codex-readonly.sh [options] -- PROMPT
  run-codex-readonly.sh [options] --prompt-file FILE

Options:
  --cwd DIR          Read-only workspace (default: current directory)
  --model MODEL      Codex model (default: gpt-5.6-terra)
  --effort LEVEL     Reasoning effort (default: medium)
  --schema FILE      JSON Schema for the final response
  --prompt-file FILE Read the prompt from a file
  -h, --help         Show this help
EOF
}

process_executable() {
    local pid="$1"

    case "$(uname -s)" in
        Darwin)
            /usr/sbin/lsof -a -p "$pid" -d txt -Fn 2>/dev/null |
                sed -n 's/^n//p' | head -n 1
            ;;
        Linux)
            readlink "/proc/$pid/exe" 2>/dev/null
            ;;
    esac
}

process_parent() {
    /bin/ps -p "$1" -o ppid= 2>/dev/null | tr -d '[:space:]'
}

process_cwd() {
    local pid="$1"

    case "$(uname -s)" in
        Darwin)
            /usr/sbin/lsof -a -p "$pid" -d cwd -Fn 2>/dev/null |
                sed -n 's/^n//p' | head -n 1
            ;;
        Linux)
            readlink "/proc/$pid/cwd" 2>/dev/null
            ;;
    esac
}

find_claude_project_root() {
    local pid="$PPID"
    local executable
    local parent
    local depth

    for ((depth = 0; depth < 32 && pid > 1; depth++)); do
        executable="$(process_executable "$pid" || true)"
        if [[ -n "$executable" && "$executable" == "$claude_bin" ]]; then
            process_cwd "$pid"
            return
        fi
        parent="$(process_parent "$pid" || true)"
        if [[ ! "$parent" =~ ^[0-9]+$ || "$parent" == "$pid" ]]; then
            break
        fi
        pid="$parent"
    done
}

if [[ ! -x "$codex_bin" || -d "$codex_bin" ]]; then
    echo "Installed Codex binary is unavailable: $codex_bin" >&2
    echo "Rerun the dotfiles installer to refresh the headless launcher." >&2
    exit 127
fi

invocation_root="$(pwd -P)"
claude_project_root="$(find_claude_project_root || true)"
if [[ "${CLAUDECODE:-}" == "1" && -z "$claude_project_root" ]]; then
    echo "Could not verify the invoking Claude Code process." >&2
    echo "Rerun the dotfiles installer after Claude Code upgrades, then retry." >&2
    exit 2
fi
if [[ -n "$claude_project_root" ]]; then
    claude_project_root="$(cd "$claude_project_root" && pwd -P)"
    case "$invocation_root" in
        "$claude_project_root"|"$claude_project_root"/*) ;;
        *)
            echo "Invocation directory escaped the Claude project root: $invocation_root" >&2
            exit 2
            ;;
    esac
fi

codex_cwd="$invocation_root"
codex_model="gpt-5.6-terra"
codex_effort="medium"
schema_path=""
prompt_file=""
prompt_text=""
worker_contract="Repository facts must be verified with read-only tools before you answer. Do not infer them from path names or prior knowledge. If required evidence is unavailable, report that instead of guessing."

resolve_input_file() {
    local input_path="$1"
    local input_real

    if [[ -L "$input_path" ]]; then
        echo "Input files must not be symlinks: $input_path" >&2
        return 2
    fi
    input_real="$(cd "$(dirname "$input_path")" && pwd -P)/$(basename "$input_path")"
    case "$input_real" in
        "$invocation_root"|"$invocation_root"/*) printf '%s\n' "$input_real" ;;
        *)
            echo "Input files must stay under the invocation directory: $input_real" >&2
            return 2
            ;;
    esac
}

while (($#)); do
    case "$1" in
        --cwd)
            codex_cwd="${2:?--cwd requires a directory}"
            shift 2
            ;;
        --model)
            codex_model="${2:?--model requires a model}"
            shift 2
            ;;
        --effort)
            codex_effort="${2:?--effort requires a level}"
            shift 2
            ;;
        --schema)
            schema_path="${2:?--schema requires a file}"
            shift 2
            ;;
        --prompt-file)
            prompt_file="${2:?--prompt-file requires a file}"
            shift 2
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        --)
            shift
            prompt_text="$*"
            break
            ;;
        *)
            echo "Unknown option: $1" >&2
            usage >&2
            exit 2
            ;;
    esac
done

if [[ ! -d "$codex_cwd" ]]; then
    echo "Workspace does not exist: $codex_cwd" >&2
    exit 2
fi

if [[ -n "$prompt_file" && -n "$prompt_text" ]]; then
    echo "Use either --prompt-file or -- PROMPT, not both" >&2
    exit 2
fi

if [[ -n "$prompt_file" && ! -f "$prompt_file" ]]; then
    echo "Prompt file does not exist: $prompt_file" >&2
    exit 2
fi

if [[ -n "$prompt_file" ]]; then
    prompt_file="$(resolve_input_file "$prompt_file")" || exit $?
fi

if [[ -z "$prompt_file" && -z "$prompt_text" ]]; then
    echo "A prompt is required" >&2
    exit 2
fi

if [[ -n "$schema_path" && ! -f "$schema_path" ]]; then
    echo "Schema file does not exist: $schema_path" >&2
    exit 2
fi

if [[ -n "$schema_path" ]]; then
    schema_path="$(resolve_input_file "$schema_path")" || exit $?
fi

case "$codex_effort" in
    low|medium|high|xhigh|max|ultra) ;;
    *)
        echo "Unsupported effort: $codex_effort" >&2
        exit 2
        ;;
esac

if [[ ! "$codex_model" =~ ^[A-Za-z0-9][A-Za-z0-9._:/-]*$ ]]; then
    echo "Invalid model name: $codex_model" >&2
    exit 2
fi

workspace_root="$(cd "$codex_cwd" && pwd -P)"
case "$workspace_root" in
    "$invocation_root"|"$invocation_root"/*) ;;
    *)
        echo "Workspace must be the invocation directory or its child: $workspace_root" >&2
        exit 2
        ;;
esac
temp_root="$(cd "${TMPDIR:-/tmp}" && pwd -P)"
case "$temp_root/headless-codex.placeholder" in
    "$invocation_root"|"$invocation_root"/*)
        echo "TMPDIR must stay outside the invocation directory: $temp_root" >&2
        exit 2
        ;;
esac

umask 077
run_dir="$(mktemp -d "$temp_root/headless-codex.XXXXXX")"
output_real="$run_dir/final.md"
trace_real="$run_dir/events.jsonl"
stderr_real="$run_dir/stderr.log"

codex_args=(
    "$codex_bin" exec
    --ignore-user-config
    --strict-config
    --ephemeral
    --skip-git-repo-check
    --json
    -C "$codex_cwd"
    -m "$codex_model"
    -o "$output_real"
    -c "model_reasoning_effort=\"$codex_effort\""
    -c 'approval_policy="never"'
    -c 'allow_login_shell=false'
    -c 'project_doc_max_bytes=0'
    -c 'shell_environment_policy={ inherit="core", ignore_default_excludes=false, include_only=["^(HOME|LANG|LC_[A-Z_]+|LOGNAME|PATH|SHELL|TERM|TMPDIR|USER)$"] }'
    -c 'web_search="disabled"'
    -c 'default_permissions="headless-readonly"'
    -c 'permissions.headless-readonly={ description="Ephemeral workspace-only read access.", filesystem={ glob_scan_max_depth=4, ":root"="deny", ":minimal"="read", ":tmpdir"="deny", ":slash_tmp"="deny", "/tmp"="deny", "/private/tmp"="deny", "~/.aws"="deny", "~/.config"="deny", "~/.secrets"="deny", "~/.ssh"="deny", ":workspace_roots"={ "."="read", ".env"="deny", ".env.*"="deny", "**/.env"="deny", "**/.env.*"="deny" } }, network={ enabled=false } }'
    --disable apps
    --disable browser_use
    --disable computer_use
    --disable goals
    --disable hooks
    --disable image_generation
    --disable memories
    --disable multi_agent
    --disable plugins
    --disable remote_plugin
    --disable shell_snapshot
    --disable skill_search
    --disable tool_suggest
    --disable workspace_dependencies
)

codex_runner=(/usr/bin/env "TMPDIR=$run_dir")

if [[ -n "$schema_path" ]]; then
    codex_args+=(--output-schema "$schema_path")
fi
codex_args+=(-)

if [[ -n "$prompt_file" ]]; then
    if {
        printf '%s\n\n' "$worker_contract"
        cat "$prompt_file"
    } | "${codex_runner[@]}" "${codex_args[@]}" > "$trace_real" 2> "$stderr_real"; then
        codex_status=0
    else
        codex_status=$?
    fi
else
    if printf '%s\n\n%s\n' "$worker_contract" "$prompt_text" | "${codex_runner[@]}" "${codex_args[@]}" > "$trace_real" 2> "$stderr_real"; then
        codex_status=0
    else
        codex_status=$?
    fi
fi

if ((codex_status != 0)); then
    echo "Headless Codex failed with exit $codex_status" >&2
    echo "stderr: $stderr_real" >&2
    echo "trace: $trace_real" >&2
    if [[ -s "$stderr_real" ]]; then
        tail -n 20 "$stderr_real" >&2
    fi
    exit "$codex_status"
fi

if [[ ! -s "$output_real" ]]; then
    echo "Headless Codex succeeded without a final output" >&2
    echo "trace: $trace_real" >&2
    exit 1
fi

cat "$output_real"
printf '\n[headless-codex] output=%s trace=%s stderr=%s\n' \
    "$output_real" "$trace_real" "$stderr_real"
