# =============================================================================
# .zshrc - Zsh configuration
# =============================================================================

# -----------------------------------------------------------------------------
# 1. Homebrew (MUST come first - other configs depend on homebrew binaries!)
# -----------------------------------------------------------------------------
if [[ -x "$HOME/.homebrew/bin/brew" ]]; then
  eval "$($HOME/.homebrew/bin/brew shellenv)"
elif [[ -x "/opt/homebrew/bin/brew" ]]; then
  eval "$(/opt/homebrew/bin/brew shellenv)"
fi

# Cask apps go to ~/Applications/ (user-level, no sudo needed).
# Without this, casks default to /Applications/ and fail on sudo prompts.
export HOMEBREW_CASK_OPTS="--appdir=$HOME/Applications"

# GNU coreutils (use GNU versions of ls, cat, etc. instead of BSD)
PATH="$HOMEBREW_PREFIX/opt/coreutils/libexec/gnubin:$PATH"

# Python 3.13 (unversioned python3/pip3 symlinks)
export PATH="$HOMEBREW_PREFIX/opt/python@3.13/libexec/bin:$PATH"

# -----------------------------------------------------------------------------
# 2. PATH additions
# -----------------------------------------------------------------------------
export PATH="$HOME/.local/bin:$PATH"
export PATH="$HOME/bin:$PATH"

# Google Cloud SDK
export CLOUDSDK_PYTHON="$HOMEBREW_PREFIX/bin/python3.13"
export PATH="$HOMEBREW_PREFIX/share/google-cloud-sdk/bin:$PATH"

# Bun - fast JavaScript runtime
export BUN_INSTALL="$HOME/.bun"
export PATH="$BUN_INSTALL/bin:$PATH"

# -----------------------------------------------------------------------------
# 2.5 Resource limits
# -----------------------------------------------------------------------------
# Raise open-file descriptor soft limit. macOS defaults via launchctl to 256,
# which trips ENFILE/EMFILE on Astro/Vite builds, pnpm, and Claude Code CLI
# with many worktrees. Hard limit (kern.maxfilesperproc) is 61440 so 10240 is
# safe and non-sudo. See ~/.claude/projects/-Users-shroom-gu-log for context.
ulimit -n 10240

# -----------------------------------------------------------------------------
# 3. Source other config files
# -----------------------------------------------------------------------------
# Secrets (~/.secrets/ is a dir of per-provider *.sh files — NEVER commit!)
[ -f ~/.secrets/index.sh ] && source ~/.secrets/index.sh

# Aliases (shared with bash)
[ -f ~/.aliases ] && source ~/.aliases

# -----------------------------------------------------------------------------
# 4. Tool initializations
# -----------------------------------------------------------------------------
# fzf - fuzzy finder (Ctrl+R for history, Ctrl+T for files)
[ -f ~/.fzf.zsh ] && source ~/.fzf.zsh

# zoxide - smarter cd command
# Don't use --cmd cd; define our own cd with fallback for CC sandbox compatibility
if command -v zoxide &>/dev/null; then
    eval "$(zoxide init zsh)"  # Creates __zoxide_z, z, zi (but not cd)
fi

# Custom cd: use zoxide if available, otherwise builtin
cd() {
    if (( $+functions[__zoxide_z] )); then
        __zoxide_z "$@"
    else
        builtin cd "$@"
    fi
}

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
autoload -Uz compinit && compinit -u
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

# Homebrew's openssl@3 is built from source (non-default prefix) so Node
# doesn't trust system certs by default. Point it at Homebrew's CA bundle.
export NODE_EXTRA_CA_CERTS="$HOMEBREW_PREFIX/etc/ca-certificates/cert.pem"

# -----------------------------------------------------------------------------
# 9. Prompt (clean, similar to bash prompt + RPROMPT)
# -----------------------------------------------------------------------------
zmodload zsh/datetime

# User display name + color (fallback: %n in white)
case $USER in
    sprin)  _u='%F{117}Sprin%f' ;;
    shroom) _u='%F{183}Shroom%f' ;;
    *)      _u='%F{white}%n%f' ;;
esac

# Host display name + color (fallback: %m in white)
case $(hostname -s) in
    Sprin-MBA*) _h='%F{111}MacAir%f' ;;
    *)       _h='%F{white}%m%f' ;;
esac

PROMPT="${_u} ${_h} %F{180}%1~%f \$ "

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

# bun completions
[ -s "/Users/shroom/.bun/_bun" ] && source "/Users/shroom/.bun/_bun"
