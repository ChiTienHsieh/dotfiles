# Disable telemetry for OpenSpec and tools that honor Do Not Track.
export OPENSPEC_TELEMETRY=0
export DO_NOT_TRACK=1

# Silence zoxide's doctor warning everywhere (incl. non-interactive shells like
# Claude Code's Bash tool, which sources .zshenv but not the full .zshrc).
export _ZO_DOCTOR=0
. "$HOME/.cargo/env"

# Codex runs non-interactive login zsh for shell tools, which can put /usr/bin
# before user-managed bins. Keep Codex-only wrappers available without changing
# normal terminal sessions.
if [[ -n "${CODEX_THREAD_ID:-}" || -n "${CODEX_SANDBOX:-}" ]]; then
  path=("$HOME/.codex/bin" "${(@)path:#$HOME/.codex/bin}")
  export PATH
fi
