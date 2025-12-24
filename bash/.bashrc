# =============================================================================
# .bashrc - Non-login shell configuration
# =============================================================================
# This file is sourced by .bash_profile, so it runs for both login and
# non-login shells. Keep it lightweight!

# Source aliases (enables subshells to use aliases - critical for AI tools!)
[ -f ~/.aliases ] && source ~/.aliases

# fzf - fuzzy finder (Ctrl+R for history, Ctrl+T for files, **<TAB> for completion)
[ -f ~/.fzf.bash ] && source ~/.fzf.bash

# zoxide - smarter cd command
# Don't use --cmd cd; define our own cd with fallback for CC sandbox compatibility
if command -v zoxide &>/dev/null; then
    eval "$(zoxide init bash)"  # Creates __zoxide_z, z, zi (but not cd)
fi

# Custom cd: use zoxide if available, otherwise builtin
cd() {
    if type __zoxide_z &>/dev/null 2>&1; then
        __zoxide_z "$@"
    else
        builtin cd "$@"
    fi
}

# Default editor
export EDITOR="nvim"

# Bun - fast JavaScript runtime
export BUN_INSTALL="$HOME/.bun"
export PATH="$BUN_INSTALL/bin:$PATH"
