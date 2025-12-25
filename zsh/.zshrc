# =============================================================================
# .zshrc - Zsh configuration
# =============================================================================

# -----------------------------------------------------------------------------
# 1. Homebrew (MUST come first - other configs depend on homebrew binaries!)
# -----------------------------------------------------------------------------
eval "$(/opt/homebrew/bin/brew shellenv)"

# GNU coreutils (use GNU versions of ls, cat, etc. instead of BSD)
PATH="/opt/homebrew/opt/coreutils/libexec/gnubin:$PATH"

# -----------------------------------------------------------------------------
# 2. PATH additions
# -----------------------------------------------------------------------------
export PATH="$HOME/.local/bin:$PATH"
export PATH="$HOME/bin:$PATH"

# Bun - fast JavaScript runtime
export BUN_INSTALL="$HOME/.bun"
export PATH="$BUN_INSTALL/bin:$PATH"

# -----------------------------------------------------------------------------
# 3. Source other config files
# -----------------------------------------------------------------------------
# Secrets (API keys, tokens - NEVER commit this file!)
[ -f ~/.secrets ] && source ~/.secrets

# Aliases (shared with bash)
[ -f ~/.aliases ] && source ~/.aliases

# -----------------------------------------------------------------------------
# 4. Tool initializations
# -----------------------------------------------------------------------------
# fzf - fuzzy finder (Ctrl+R for history, Ctrl+T for files)
[ -f ~/.fzf.zsh ] && source ~/.fzf.zsh

# zoxide - smarter cd command
if command -v zoxide &>/dev/null; then
    eval "$(zoxide init zsh)"
fi

# -----------------------------------------------------------------------------
# 5. Zsh options
# -----------------------------------------------------------------------------
setopt AUTO_CD              # cd by typing directory name
setopt CORRECT              # Spelling correction for commands
setopt HIST_IGNORE_DUPS     # Don't record duplicate commands
setopt HIST_IGNORE_SPACE    # Don't record commands starting with space
setopt SHARE_HISTORY        # Share history between sessions
setopt EXTENDED_GLOB        # Extended globbing (**, etc.)

# History settings
HISTFILE=~/.zsh_history
HISTSIZE=10000
SAVEHIST=10000

# -----------------------------------------------------------------------------
# 6. Completion system
# -----------------------------------------------------------------------------
autoload -Uz compinit && compinit
zstyle ':completion:*' matcher-list 'm:{a-z}={A-Z}'  # Case-insensitive completion
zstyle ':completion:*' menu select                    # Menu-style completion

# -----------------------------------------------------------------------------
# 7. Key bindings (emacs-style, like bash default)
# -----------------------------------------------------------------------------
bindkey -e
bindkey '^[[A' history-search-backward  # Up arrow: search history
bindkey '^[[B' history-search-forward   # Down arrow: search history

# -----------------------------------------------------------------------------
# 8. Default editor
# -----------------------------------------------------------------------------
export EDITOR="nvim"

# Suppress Node.js experimental warnings (CommonJS/ESM compat noise)
export NODE_NO_WARNINGS=1

# -----------------------------------------------------------------------------
# 9. Prompt (clean, similar to bash prompt + RPROMPT)
# -----------------------------------------------------------------------------
zmodload zsh/datetime

PROMPT='%F{51}Sprin%f %F{33}MacAir%f %F{207}%1~%f $ '

# Command execution time tracking
typeset -g __cmd_start=0

preexec() { __cmd_start=$EPOCHREALTIME; }

precmd() {
    local dur_str=""
    if (( __cmd_start > 0 )); then
        local dur=$(( EPOCHREALTIME - __cmd_start ))
        (( dur >= 1 )) && dur_str="%F{yellow}${dur%.*}s %f"
        __cmd_start=0
    fi
    RPROMPT="${dur_str}%F{245}%D{%H:%M}%f"
}

# -----------------------------------------------------------------------------
# 10. Auto-generated sections (tools will add their init here)
# -----------------------------------------------------------------------------
# - conda init
# - nvm init
# - etc.
