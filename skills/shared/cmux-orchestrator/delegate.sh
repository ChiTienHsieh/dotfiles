#!/bin/bash
# One-command wrapper around drive_codex.sh.
# Usage: delegate.sh "short task title" [PROMPTFILE] [TIMEOUT]
set -o pipefail

usage() {
  echo "Usage: $0 \"short task title\" [PROMPTFILE] [TIMEOUT]" >&2
}

if [ "$#" -lt 1 ] || [ "$#" -gt 3 ]; then
  usage
  exit 2
fi

TITLE="$1"
PROMPTFILE="${2:-}"
TIMEOUT="${3:-600}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)" || exit 1
DRIVER="$SCRIPT_DIR/drive_codex.sh"

if [ ! -x "$DRIVER" ]; then
  echo "drive_codex.sh is not executable: $DRIVER" >&2
  exit 1
fi

SLUG="$(
  printf '%s' "$TITLE" |
    tr '[:upper:]' '[:lower:]' |
    sed 's/[^[:alnum:]]/-/g; s/--*/-/g; s/^-//; s/-$//' |
    cut -c 1-40 |
    sed 's/-$//'
)"

if [ -z "$SLUG" ]; then
  SLUG="task"
fi

BASE_SLUG="$SLUG"
WORKROOT="$HOME/dotfiles/cmux-orchestrator/scratch"
WORKDIR="$WORKROOT/$SLUG"
N=2

while [ -e "$WORKDIR" ]; do
  SLUG="$BASE_SLUG-$N"
  WORKDIR="$WORKROOT/$SLUG"
  N=$((N + 1))
done

mkdir -p "$WORKDIR" || exit 1

PROMPT_DEST="$WORKDIR/prompt.md"
if [ -n "$PROMPTFILE" ]; then
  if [ ! -f "$PROMPTFILE" ]; then
    echo "prompt file does not exist: $PROMPTFILE" >&2
    exit 1
  fi
  cp "$PROMPTFILE" "$PROMPT_DEST" || exit 1
else
  if [ -t 0 ]; then
    usage
    exit 2
  fi
  cat > "$PROMPT_DEST" || exit 1
fi

MARKER_SLUG="$(
  printf '%s' "$SLUG" |
    tr '[:lower:]-' '[:upper:]_'
)"
MARKER="CODEX_DONE_$MARKER_SLUG"
REPORT="$WORKDIR/report.md"

exec "$DRIVER" "new" "$PROMPT_DEST" "$MARKER" "$REPORT" "$TIMEOUT" "1"
