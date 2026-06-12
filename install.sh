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

backup_and_copy() {
    local src="$1"
    local dest="$2"

    mkdir -p "$(dirname "$dest")"

    if [ -e "$dest" ]; then
        mkdir -p "$BACKUP_DIR"
        echo "  Backing up: $dest -> $BACKUP_DIR/"
        mv "$dest" "$BACKUP_DIR/"
    fi

    cp "$src" "$dest"
    echo "  Copied: $dest"
}

ensure_real_dir() {
    local dest="$1"

    if [ -L "$dest" ]; then
        echo "  Removing directory symlink: $dest -> $(readlink "$dest")"
        rm "$dest"
    elif [ -e "$dest" ] && [ ! -d "$dest" ]; then
        mkdir -p "$BACKUP_DIR"
        echo "  Backing up non-directory: $dest -> $BACKUP_DIR/"
        mv "$dest" "$BACKUP_DIR/"
    fi

    mkdir -p "$dest"
}

collect_symlinked_dir_entries() {
    local dest="$1"
    local manifest="$2"
    local target entry

    : > "$manifest"

    [ -L "$dest" ] || return 0

    target="$(readlink "$dest")"
    case "$target" in
        /*) ;;
        *) target="$(cd "$(dirname "$dest")" && pwd -P)/$target" ;;
    esac

    [ -d "$target" ] || return 0

    for entry in "$target"/*; do
        [ -e "$entry" ] || [ -L "$entry" ] || continue
        printf '%s\t%s\n' "$(basename "$entry")" "$entry" >> "$manifest"
    done
}

restore_preserved_skill_links() {
    local manifest="$1"
    local dest="$2"
    local name entry

    [ -f "$manifest" ] || return 0

    while IFS=$'\t' read -r name entry; do
        [ -n "$name" ] || continue
        [ ! -e "$dest/$name" ] && [ ! -L "$dest/$name" ] || continue
        [ -e "$entry" ] || [ -L "$entry" ] || continue
        backup_and_link "$entry" "$dest/$name"
    done < "$manifest"
}

prune_stale_dotfiles_links() {
    local dir="$1"
    local link target

    [ -d "$dir" ] || return 0

    for link in "$dir"/*; do
        [ -L "$link" ] || continue
        target="$(readlink "$link")"
        case "$target" in
            "$DOTFILES_DIR"/*)
                if [ ! -e "$target" ]; then
                    rm "$link"
                    echo "  Removed stale dotfiles symlink: $link"
                fi
                ;;
        esac
    done
}

# -----------------------------------------------------------------------------
# Initialize submodules (for nvim config)
# -----------------------------------------------------------------------------
echo "[1/10] Initializing git submodules..."
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
echo "[2/10] Installing bash configuration..."
backup_and_link "$DOTFILES_DIR/bash/.bash_profile" "$HOME/.bash_profile"
backup_and_link "$DOTFILES_DIR/bash/.bashrc" "$HOME/.bashrc"
backup_and_link "$DOTFILES_DIR/bash/.bash_prompt" "$HOME/.bash_prompt"
backup_and_link "$DOTFILES_DIR/bash/.aliases" "$HOME/.aliases"
echo ""

# -----------------------------------------------------------------------------
# Zsh configuration
# -----------------------------------------------------------------------------
echo "[3/10] Installing zsh configuration..."
backup_and_link "$DOTFILES_DIR/zsh/.zshenv" "$HOME/.zshenv"
backup_and_link "$DOTFILES_DIR/zsh/.zshrc" "$HOME/.zshrc"
echo ""

# -----------------------------------------------------------------------------
# Git configuration
# -----------------------------------------------------------------------------
echo "[4/10] Installing git configuration..."
backup_and_link "$DOTFILES_DIR/git/.gitconfig" "$HOME/.gitconfig"
backup_and_link "$DOTFILES_DIR/git/.config/git/ignore" "$HOME/.config/git/ignore"
backup_and_link "$DOTFILES_DIR/git/.config/git/hooks" "$HOME/.config/git/hooks"
echo ""

# -----------------------------------------------------------------------------
# Vim configuration
# -----------------------------------------------------------------------------
echo "[5/10] Installing vim configuration..."
backup_and_link "$DOTFILES_DIR/vim/.vimrc" "$HOME/.vimrc"
echo ""

# -----------------------------------------------------------------------------
# Tmux configuration
# -----------------------------------------------------------------------------
echo "[6/10] Installing tmux configuration..."
backup_and_link "$DOTFILES_DIR/tmux/.tmux.conf" "$HOME/.tmux.conf"
echo ""

# -----------------------------------------------------------------------------
# Other configurations
# -----------------------------------------------------------------------------
echo "[7/10] Installing other configurations..."
backup_and_link "$DOTFILES_DIR/gh/.config/gh/config.yml" "$HOME/.config/gh/config.yml"
backup_and_link "$DOTFILES_DIR/ghostty/config" "$HOME/Library/Application Support/com.mitchellh.ghostty/config"

# Nvim (if submodule exists)
if [ -d "$DOTFILES_DIR/nvim" ] && [ "$(ls -A "$DOTFILES_DIR/nvim" 2>/dev/null)" ]; then
    backup_and_link "$DOTFILES_DIR/nvim" "$HOME/.config/nvim"
fi
echo ""

# -----------------------------------------------------------------------------
# Claude Code configuration
# -----------------------------------------------------------------------------
echo "[8/10] Installing Claude Code configuration..."
CLAUDE_SKILLS_PRESERVE_FILE="${TMPDIR:-/tmp}/dotfiles-claude-skills-preserve.$$"
collect_symlinked_dir_entries "$HOME/.claude/skills" "$CLAUDE_SKILLS_PRESERVE_FILE"
ensure_real_dir "$HOME/.claude/commands"
ensure_real_dir "$HOME/.claude/skills"

# Main config files
backup_and_link "$DOTFILES_DIR/claude/CLAUDE.md" "$HOME/.claude/CLAUDE.md"
backup_and_hardlink "$DOTFILES_DIR/claude/settings.json" "$HOME/.claude/settings.json"  # Hard link to avoid CC symlink bug
backup_and_link "$DOTFILES_DIR/claude/statusline.sh" "$HOME/.claude/statusline.sh"
backup_and_link "$DOTFILES_DIR/claude/claude-powerline.json" "$HOME/.claude/claude-powerline.json"
backup_and_link "$DOTFILES_DIR/claude/nvim-progress.json" "$HOME/.claude/nvim-progress.json"

# Directories
backup_and_link "$DOTFILES_DIR/claude/agents" "$HOME/.claude/agents"
backup_and_link "$DOTFILES_DIR/claude/hooks" "$HOME/.claude/hooks"

# Skills
for skill in "$DOTFILES_DIR"/skills/shared/* "$DOTFILES_DIR"/skills/claude/*; do
    [ -d "$skill" ] || continue
    backup_and_link "$skill" "$HOME/.claude/skills/$(basename "$skill")"
done
restore_preserved_skill_links "$CLAUDE_SKILLS_PRESERVE_FILE" "$HOME/.claude/skills"
prune_stale_dotfiles_links "$HOME/.claude/skills"
rm -f "$CLAUDE_SKILLS_PRESERVE_FILE"

# Legacy command entrypoints are thin compatibility shims that delegate to skills.
for cmd in chill.md eternal-code-seeker.md gsync.md iterate-worker-reviewer.md level-up.md night.md nvim-tutor.md remember.md wrap.md; do
    backup_and_link "$DOTFILES_DIR/claude/commands/$cmd" "$HOME/.claude/commands/$cmd"
done

# yolo-cc CLI tool
mkdir -p "$HOME/.local/bin"
backup_and_link "$DOTFILES_DIR/yolo-cc/bin/yolo-cc" "$HOME/.local/bin/yolo-cc"

# Plugins (personal marketplace - requires manual install after)
# The marketplace is at: $DOTFILES_DIR/claude/plugins/
# After running install.sh, run these commands in Claude Code:
#   /plugin marketplace add ~/dotfiles/claude/plugins
#   /plugin install cth-plugins@cth-marketplace
echo "  [!] Personal plugins require manual setup in Claude Code:"
echo "      /plugin marketplace add ~/dotfiles/claude/plugins"
echo "      /plugin install cth-plugins@cth-marketplace"
echo ""

# -----------------------------------------------------------------------------
# Codex CLI configuration
# -----------------------------------------------------------------------------
echo "[9/10] Installing Codex CLI configuration..."
mkdir -p "$HOME/.codex"
backup_and_link "$DOTFILES_DIR/codex/AGENTS.md" "$HOME/.codex/AGENTS.md"
backup_and_copy "$DOTFILES_DIR/codex/config.toml" "$HOME/.codex/config.toml"
if [ ! -e "$HOME/.codex/machine.md" ]; then
    backup_and_copy "$DOTFILES_DIR/codex/machine.md" "$HOME/.codex/machine.md"
else
    echo "  ~/.codex/machine.md already exists, skipping machine notes bootstrap"
fi
backup_and_link "$DOTFILES_DIR/codex/bin" "$HOME/.codex/bin"
backup_and_link "$DOTFILES_DIR/codex/agents" "$HOME/.codex/agents"
mkdir -p "$HOME/.codex/rules"
for rule in "$DOTFILES_DIR"/codex/rules/*.rules; do
    [ -f "$rule" ] || continue
    backup_and_link "$rule" "$HOME/.codex/rules/$(basename "$rule")"
done
ensure_real_dir "$HOME/.codex/skills"
ensure_real_dir "$HOME/.agents/skills"
for skill in "$DOTFILES_DIR"/codex/skills/.system "$DOTFILES_DIR"/skills/shared/* "$DOTFILES_DIR"/skills/codex/*; do
    [ -d "$skill" ] || continue
    backup_and_link "$skill" "$HOME/.codex/skills/$(basename "$skill")"
done
prune_stale_dotfiles_links "$HOME/.codex/skills"
for skill in "$DOTFILES_DIR"/skills/shared/*; do
    [ -d "$skill" ] || continue
    backup_and_link "$skill" "$HOME/.agents/skills/$(basename "$skill")"
done
prune_stale_dotfiles_links "$HOME/.agents/skills"
echo ""

# -----------------------------------------------------------------------------
# Git hooks (for dotfiles repo itself)
# -----------------------------------------------------------------------------
echo "[10/10] Installing git hooks..."
if [ -d "$DOTFILES_DIR/.git" ]; then
    mkdir -p "$DOTFILES_DIR/.git/hooks"
    backup_and_link "$DOTFILES_DIR/hooks/pre-commit" "$DOTFILES_DIR/.git/hooks/pre-commit"
else
    echo "  Not a git repo, skipping hooks."
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
echo "  3. Run: source ~/.zshrc (or source ~/.bash_profile for bash)"
echo ""
echo "Enjoy your new setup! (◕‿◕)"
echo ""
