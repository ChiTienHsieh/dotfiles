#!/usr/bin/env bash
set -euo pipefail

launcher="$HOME/.local/libexec/dotfiles/run-codex-readonly.sh"

if [[ ! -f "$launcher" || -L "$launcher" || ! -x "$launcher" ]]; then
    echo "Trusted headless Codex launcher is not installed: $launcher" >&2
    echo "Run ~/dotfiles/install.sh, then retry." >&2
    exit 127
fi

exec "$launcher" "$@"
