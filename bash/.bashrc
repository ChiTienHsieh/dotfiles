# =============================================================================
# .bashrc - Non-login shell configuration
# =============================================================================
# This file is sourced by .bash_profile, so it runs for both login and
# non-login shells. Keep it lightweight!

# Source aliases (enables subshells to use aliases - critical for AI tools!)
[ -f ~/.aliases ] && source ~/.aliases

# fzf - fuzzy finder (Ctrl+R for history, Ctrl+T for files, **<TAB> for completion)
[ -f ~/.fzf.bash ] && source ~/.fzf.bash

# Default editor
export EDITOR="nvim"

# Bun - fast JavaScript runtime
export BUN_INSTALL="$HOME/.bun"
export PATH="$BUN_INSTALL/bin:$PATH"
