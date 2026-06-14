# Disable telemetry for OpenSpec and tools that honor Do Not Track.
export OPENSPEC_TELEMETRY=0
export DO_NOT_TRACK=1

# Silence zoxide's doctor warning everywhere (incl. non-interactive shells like
# Claude Code's Bash tool, which sources .zshenv but not the full .zshrc).
export _ZO_DOCTOR=0
