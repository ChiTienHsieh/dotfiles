#!/usr/bin/env bash
# =============================================================================
# Dotfiles Installation Script
# =============================================================================
# Usage: ./install.sh
#
# This script creates symlinks from your home directory to the dotfiles repo.
# Run this after cloning the repo on a new machine.
# =============================================================================

set -e  # Exit on error

DOTFILES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_DIR="$HOME/.dotfiles_backup/$(date +%Y%m%d_%H%M%S)"

echo "=========================================="
echo "  Dotfiles Installation"
echo "=========================================="
echo ""
echo "Dotfiles directory: $DOTFILES_DIR"
echo ""

# -----------------------------------------------------------------------------
# Helper functions
# -----------------------------------------------------------------------------
backup_and_link() {
    local src="$1"
    local dest="$2"

    # Create parent directory if needed
    mkdir -p "$(dirname "$dest")"

    # Backup existing file if it's not a symlink
    if [ -e "$dest" ] && [ ! -L "$dest" ]; then
        mkdir -p "$BACKUP_DIR"
        echo "  Backing up: $dest -> $BACKUP_DIR/"
        mv "$dest" "$BACKUP_DIR/"
    fi

    # Remove existing symlink
    if [ -L "$dest" ]; then
        rm "$dest"
    fi

    # Create symlink
    ln -sf "$src" "$dest"
    echo "  Linked: $dest -> $src"
}

# Hard link version (for files that don't work well with symlinks, e.g. settings.json)
backup_and_hardlink() {
    local src="$1"
    local dest="$2"

    mkdir -p "$(dirname "$dest")"

    if [ -e "$dest" ] && [ ! -L "$dest" ]; then
        mkdir -p "$BACKUP_DIR"
        echo "  Backing up: $dest -> $BACKUP_DIR/"
        mv "$dest" "$BACKUP_DIR/"
    fi

    if [ -L "$dest" ]; then
        rm "$dest"
    fi

    # Create hard link (same inode, works around symlink detection issues)
    ln -f "$src" "$dest"
    echo "  Hard linked: $dest"
}

# -----------------------------------------------------------------------------
# Initialize submodules (for nvim config)
# -----------------------------------------------------------------------------
echo "[1/8] Initializing git submodules..."
if [ -f "$DOTFILES_DIR/.gitmodules" ]; then
    git -C "$DOTFILES_DIR" submodule update --init --recursive
    echo "  Done!"
else
    echo "  No submodules found, skipping."
fi
echo ""

# -----------------------------------------------------------------------------
# Bash configuration
# -----------------------------------------------------------------------------
echo "[2/8] Installing bash configuration..."
backup_and_link "$DOTFILES_DIR/bash/.bash_profile" "$HOME/.bash_profile"
backup_and_link "$DOTFILES_DIR/bash/.bashrc" "$HOME/.bashrc"
backup_and_link "$DOTFILES_DIR/bash/.bash_prompt" "$HOME/.bash_prompt"
backup_and_link "$DOTFILES_DIR/bash/.aliases" "$HOME/.aliases"
echo ""

# -----------------------------------------------------------------------------
# Zsh configuration
# -----------------------------------------------------------------------------
echo "[3/8] Installing zsh configuration..."
backup_and_link "$DOTFILES_DIR/zsh/.zshrc" "$HOME/.zshrc"
echo ""

# -----------------------------------------------------------------------------
# Git configuration
# -----------------------------------------------------------------------------
echo "[4/8] Installing git configuration..."
backup_and_link "$DOTFILES_DIR/git/.gitconfig" "$HOME/.gitconfig"
backup_and_link "$DOTFILES_DIR/git/.config/git/ignore" "$HOME/.config/git/ignore"
echo ""

# -----------------------------------------------------------------------------
# Vim configuration
# -----------------------------------------------------------------------------
echo "[5/8] Installing vim configuration..."
backup_and_link "$DOTFILES_DIR/vim/.vimrc" "$HOME/.vimrc"
echo ""

# -----------------------------------------------------------------------------
# Tmux configuration
# -----------------------------------------------------------------------------
echo "[6/8] Installing tmux configuration..."
backup_and_link "$DOTFILES_DIR/tmux/.tmux.conf" "$HOME/.tmux.conf"
echo ""

# -----------------------------------------------------------------------------
# Other configurations
# -----------------------------------------------------------------------------
echo "[7/8] Installing other configurations..."
backup_and_link "$DOTFILES_DIR/gh/.config/gh/config.yml" "$HOME/.config/gh/config.yml"

# Nvim (if submodule exists)
if [ -d "$DOTFILES_DIR/nvim" ] && [ "$(ls -A "$DOTFILES_DIR/nvim" 2>/dev/null)" ]; then
    backup_and_link "$DOTFILES_DIR/nvim" "$HOME/.config/nvim"
fi
echo ""

# -----------------------------------------------------------------------------
# Claude Code configuration
# -----------------------------------------------------------------------------
echo "[8/8] Installing Claude Code configuration..."
mkdir -p "$HOME/.claude/commands"

# Main config files
backup_and_link "$DOTFILES_DIR/claude/CLAUDE.md" "$HOME/.claude/CLAUDE.md"
backup_and_hardlink "$DOTFILES_DIR/claude/settings.json" "$HOME/.claude/settings.json"  # Hard link to avoid CC symlink bug
backup_and_link "$DOTFILES_DIR/claude/claude-powerline.json" "$HOME/.claude/claude-powerline.json"
backup_and_link "$DOTFILES_DIR/claude/nvim-progress.json" "$HOME/.claude/nvim-progress.json"

# Directories (agents and hooks can be fully symlinked)
backup_and_link "$DOTFILES_DIR/claude/agents" "$HOME/.claude/agents"
backup_and_link "$DOTFILES_DIR/claude/hooks" "$HOME/.claude/hooks"

# Commands (individual files - directory has local state we don't track)
for cmd in chill.md eternal-code-seeker.md headless-agents.md level-up.md nvim-tutor.md remember.md; do
    backup_and_link "$DOTFILES_DIR/claude/commands/$cmd" "$HOME/.claude/commands/$cmd"
done
echo ""

# -----------------------------------------------------------------------------
# Copy templates (these are NOT symlinked, they're starting points)
# -----------------------------------------------------------------------------
echo "=========================================="
echo "  Templates"
echo "=========================================="
echo ""
if [ ! -f "$HOME/.secrets" ]; then
    cp "$DOTFILES_DIR/templates/.secrets.template" "$HOME/.secrets"
    chmod 600 "$HOME/.secrets"
    echo "Created ~/.secrets from template"
    echo "  -> Edit this file to add your API keys!"
else
    echo "~/.secrets already exists, skipping."
fi

# .aliases.local is symlinked (but gitignored) so CC can edit it in sandbox mode
if [ ! -f "$DOTFILES_DIR/bash/.aliases.local" ]; then
    cp "$DOTFILES_DIR/templates/.aliases.local.template" "$DOTFILES_DIR/bash/.aliases.local"
    echo "Created bash/.aliases.local from template"
fi
backup_and_link "$DOTFILES_DIR/bash/.aliases.local" "$HOME/.aliases.local"
echo "  -> Add your machine-specific aliases here!"
echo ""

# -----------------------------------------------------------------------------
# Done!
# -----------------------------------------------------------------------------
echo "=========================================="
echo "  Installation Complete!"
echo "=========================================="
echo ""
if [ -d "$BACKUP_DIR" ]; then
    echo "Backups saved to: $BACKUP_DIR"
    echo ""
fi
echo "Next steps:"
echo "  1. Edit ~/.secrets to add your API keys"
echo "  2. Edit ~/.aliases.local for machine-specific shortcuts"
echo "  3. Run: source ~/.zshrc (or source ~/.bash_profile for bash)"
echo ""
echo "Enjoy your new setup! (◕‿◕)"
echo ""
