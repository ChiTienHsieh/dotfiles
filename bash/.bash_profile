# =============================================================================
# .bash_profile - Login shell configuration (dotfiles-ready version)
# =============================================================================

# -----------------------------------------------------------------------------
# 1. Homebrew (MUST come first - other configs depend on homebrew binaries!)
# -----------------------------------------------------------------------------
eval "$(/opt/homebrew/bin/brew shellenv)"

# GNU coreutils (use GNU versions of ls, cat, etc. instead of BSD)
PATH="/opt/homebrew/opt/coreutils/libexec/gnubin:$PATH"

# -----------------------------------------------------------------------------
# 2. Source other config files
# -----------------------------------------------------------------------------
# Source .bashrc (ensures non-login shells get same config)
if [ -f ~/.bashrc ]; then
    source ~/.bashrc
fi

# Source secrets (API keys, tokens - NEVER commit this file!)
if [ -f ~/.secrets ]; then
    source ~/.secrets
fi

# Source prompt configuration
if [ -f ~/.bash_prompt ]; then
    source ~/.bash_prompt
fi

# Note: .aliases is sourced in .bashrc (no need to duplicate here)

# -----------------------------------------------------------------------------
# 3. PATH additions
# -----------------------------------------------------------------------------
export PATH="$HOME/.local/bin:$PATH"
export PATH="$HOME/bin:$PATH"

# -----------------------------------------------------------------------------
# 4. Tool initializations (tools that don't auto-generate their init)
# -----------------------------------------------------------------------------
# fzf is sourced in .bashrc (no need to duplicate here)

# zoxide + custom cd wrapper in .bashrc (with fallback for CC sandbox)

# -----------------------------------------------------------------------------
# 5. Auto-generated sections (DO NOT add to dotfiles, let tools generate)
# -----------------------------------------------------------------------------
# The following will be added automatically when you install the tools:
# - conda init (if using conda)
# - nvm init (Node Version Manager)
# - OrbStack init
# - Google Cloud SDK (if using)
# - etc.
