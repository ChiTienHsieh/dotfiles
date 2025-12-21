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

# -----------------------------------------------------------------------------
# Initialize submodules (for nvim config)
# -----------------------------------------------------------------------------
echo "[1/6] Initializing git submodules..."
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
echo "[2/6] Installing bash configuration..."
backup_and_link "$DOTFILES_DIR/bash/.bash_profile" "$HOME/.bash_profile"
backup_and_link "$DOTFILES_DIR/bash/.bashrc" "$HOME/.bashrc"
backup_and_link "$DOTFILES_DIR/bash/.bash_prompt" "$HOME/.bash_prompt"
backup_and_link "$DOTFILES_DIR/bash/.aliases" "$HOME/.aliases"
echo ""

# -----------------------------------------------------------------------------
# Git configuration
# -----------------------------------------------------------------------------
echo "[3/6] Installing git configuration..."
backup_and_link "$DOTFILES_DIR/git/.gitconfig" "$HOME/.gitconfig"
backup_and_link "$DOTFILES_DIR/git/.config/git/ignore" "$HOME/.config/git/ignore"
echo ""

# -----------------------------------------------------------------------------
# Vim configuration
# -----------------------------------------------------------------------------
echo "[4/6] Installing vim configuration..."
backup_and_link "$DOTFILES_DIR/vim/.vimrc" "$HOME/.vimrc"
echo ""

# -----------------------------------------------------------------------------
# Tmux configuration
# -----------------------------------------------------------------------------
echo "[5/6] Installing tmux configuration..."
backup_and_link "$DOTFILES_DIR/tmux/.tmux.conf" "$HOME/.tmux.conf"
echo ""

# -----------------------------------------------------------------------------
# Other configurations
# -----------------------------------------------------------------------------
echo "[6/6] Installing other configurations..."
backup_and_link "$DOTFILES_DIR/gh/.config/gh/config.yml" "$HOME/.config/gh/config.yml"

# Nvim (if submodule exists)
if [ -d "$DOTFILES_DIR/nvim" ] && [ "$(ls -A "$DOTFILES_DIR/nvim" 2>/dev/null)" ]; then
    backup_and_link "$DOTFILES_DIR/nvim" "$HOME/.config/nvim"
fi
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
echo "  3. Run: source ~/.bash_profile"
echo ""
echo "Enjoy your new setup! (◕‿◕)"
echo ""
