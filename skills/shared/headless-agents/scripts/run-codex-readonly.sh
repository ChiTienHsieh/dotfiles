#!/usr/bin/env bash
set -euo pipefail

usage() {
    cat <<'EOF'
Usage:
  run-codex-readonly.sh [options] -- PROMPT
  run-codex-readonly.sh [options] --prompt-file FILE

Options:
  --cwd DIR          Read-only workspace (default: current directory)
  --model MODEL      Codex model (default: gpt-5.6-terra)
  --effort LEVEL     Reasoning effort (default: medium)
  --output FILE      Final response path
  --trace FILE       JSONL event trace path
  --stderr FILE      Codex stderr path
  --schema FILE      JSON Schema for the final response
  --prompt-file FILE Read the prompt from a file
  -h, --help         Show this help
EOF
}

codex_cwd="$PWD"
codex_model="gpt-5.6-terra"
codex_effort="medium"
output_path=""
trace_path=""
stderr_path=""
schema_path=""
prompt_file=""
prompt_text=""
worker_contract="Repository facts must be verified with read-only tools before you answer. Do not infer them from path names or prior knowledge. If required evidence is unavailable, report that instead of guessing."

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
        --output)
            output_path="${2:?--output requires a file}"
            shift 2
            ;;
        --trace)
            trace_path="${2:?--trace requires a file}"
            shift 2
            ;;
        --stderr)
            stderr_path="${2:?--stderr requires a file}"
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

if ! command -v codex >/dev/null 2>&1; then
    echo "codex is not available on PATH" >&2
    exit 127
fi

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

if [[ -z "$prompt_file" && -z "$prompt_text" ]]; then
    echo "A prompt is required" >&2
    exit 2
fi

if [[ -n "$schema_path" && ! -f "$schema_path" ]]; then
    echo "Schema file does not exist: $schema_path" >&2
    exit 2
fi

run_dir="$(mktemp -d "${TMPDIR:-/tmp}/headless-codex.XXXXXX")"
output_path="${output_path:-$run_dir/final.md}"
trace_path="${trace_path:-$run_dir/events.jsonl}"
stderr_path="${stderr_path:-$run_dir/stderr.log}"

mkdir -p "$(dirname "$output_path")" "$(dirname "$trace_path")" "$(dirname "$stderr_path")"

workspace_root="$(cd "$codex_cwd" && pwd -P)"
output_real="$(cd "$(dirname "$output_path")" && pwd -P)/$(basename "$output_path")"
trace_real="$(cd "$(dirname "$trace_path")" && pwd -P)/$(basename "$trace_path")"
stderr_real="$(cd "$(dirname "$stderr_path")" && pwd -P)/$(basename "$stderr_path")"

for artifact_path in "$output_real" "$trace_real" "$stderr_real"; do
    case "$artifact_path" in
        "$workspace_root"|"$workspace_root"/*)
            echo "Artifact paths must stay outside the workspace: $artifact_path" >&2
            exit 2
            ;;
    esac
done

if [[ "$output_real" == "$trace_real" || "$output_real" == "$stderr_real" || "$trace_real" == "$stderr_real" ]]; then
    echo "Output, trace, and stderr paths must be distinct" >&2
    exit 2
fi

codex_args=(
    codex exec
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
    -c 'project_doc_max_bytes=0'
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
