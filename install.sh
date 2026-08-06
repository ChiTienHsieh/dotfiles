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
DOTFILES_PYTHON="$(command -v python3 || true)"

if [ -z "$DOTFILES_PYTHON" ] || ! "$DOTFILES_PYTHON" -c 'import tomllib' >/dev/null 2>&1; then
    echo "ERROR: install.sh requires Python 3.11 or newer on PATH." >&2
    exit 1
fi

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

    # Guard: never create a symlink to a nonexistent source. A silent ln -sf
    # here is how ~/.claude/skills once became a dangling link after a repo
    # dir rename — fail loudly instead.
    if [ ! -e "$src" ]; then
        echo "  ERROR: link source missing, refusing to create dangling link: $src" >&2
        return 1
    fi

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

configure_codex_local_permissions() {
    local config="$1"

    "$DOTFILES_PYTHON" - "$config" <<'PY'
from pathlib import Path
import re
import sys

path = Path(sys.argv[1])
text = path.read_text()

lines = text.splitlines()
filtered = []
skip = False
for line in lines:
    if re.match(r"^\[permissions\.workspace-(?:local-vm|sprin)(?:\.network)?\]$", line):
        skip = True
        continue
    if skip and re.match(r"^\[.*\]$", line):
        skip = False
    if not skip:
        filtered.append(line)
text = "\n".join(filtered).rstrip() + "\n"

if re.search(r"^default_permissions\s*=", text, flags=re.MULTILINE):
    text = re.sub(
        r"^default_permissions\s*=.*$",
        'default_permissions = "workspace-sprin"',
        text,
        count=1,
        flags=re.MULTILINE,
    )
else:
    marker = re.search(r"^approvals_reviewer\s*=.*$", text, flags=re.MULTILINE)
    if marker:
        insert_at = marker.end()
        text = text[:insert_at] + '\ndefault_permissions = "workspace-sprin"' + text[insert_at:]
    else:
        text = 'default_permissions = "workspace-sprin"\n' + text

features = re.search(r"^\[features\]\n(?P<body>(?:^[^\[].*\n?)*)", text, flags=re.MULTILINE)
if features:
    body = features.group("body")
    if not re.search(r"^network_proxy\s*=", body, flags=re.MULTILINE):
        insert_at = features.start("body")
        text = text[:insert_at] + "network_proxy = true\n" + text[insert_at:]
else:
    text = text.rstrip() + "\n\n[features]\nnetwork_proxy = true\n"

block = f"""
[permissions.workspace-sprin]
description = "Workspace-write with clawd-vm SSH access."
extends = ":workspace"

[permissions.workspace-sprin.network]
enabled = true
mode = "limited"
domains = {{ "clawd-vm" = "allow" }}
"""

path.write_text(text.rstrip() + "\n" + block)
PY

    echo "  Configured Codex workspace permissions"
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

is_linkable_skill_dir() {
    local skill="$1"

    [ -d "$skill" ] || return 1
    [ -f "$skill/SKILL.md" ] || [ "$(basename "$skill")" = ".system" ]
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
"$DOTFILES_PYTHON" "$DOTFILES_DIR/scripts/configure_package_policies.py" \
    --home "$HOME" --repo-root "$DOTFILES_DIR"
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
ensure_real_dir "$HOME/.claude/skills"

# Main config files
backup_and_link "$DOTFILES_DIR/claude/CLAUDE.md" "$HOME/.claude/CLAUDE.md"
# settings.json is intentionally NOT linked: ~/.claude/settings.json stays an
# independent file the user edits freely; the repo copy is just a seed/reference.
# (Hard links break silently on atomic writes; symlinks hit a CC bug.)
if [ ! -e "$HOME/.claude/settings.json" ]; then
    cp "$DOTFILES_DIR/claude/settings.json" "$HOME/.claude/settings.json"
    echo "  Seeded: $HOME/.claude/settings.json"
fi
# machine.md: one machine-local canonical (~/.config/machine.md) shared by
# Claude Code + Codex via symlink, so both agents always read identical
# machine notes. Seeded once from a secret-free template, then owned locally
# (machine-specific, non-syncable content — never committed). Editing a symlink
# is refused by the agent write-guard, which is what keeps the views from
# diverging: edits are forced back to the canonical file.
mkdir -p "$HOME/.config"
if [ ! -e "$HOME/.config/machine.md" ]; then
    # On machines predating the canonical, migrate an existing REAL machine.md
    # (not a symlink) so hand-written notes survive instead of being replaced by
    # an empty template; else seed the secret-free template. Only the first
    # match is migrated — if both agent paths are real files with diverging
    # content, merge them by hand afterwards (the other is in $BACKUP_DIR).
    machine_seed="$DOTFILES_DIR/templates/machine.md.template"
    for existing in "$HOME/.codex/machine.md" "$HOME/.claude/machine.md"; do
        if [ -f "$existing" ] && [ ! -L "$existing" ]; then machine_seed="$existing"; break; fi
    done
    cp "$machine_seed" "$HOME/.config/machine.md"
    echo "  Seeded: $HOME/.config/machine.md (from ${machine_seed##*/})"
fi
backup_and_link "$HOME/.config/machine.md" "$HOME/.claude/machine.md"
backup_and_link "$DOTFILES_DIR/claude/statusline.sh" "$HOME/.claude/statusline.sh"
backup_and_link "$DOTFILES_DIR/claude/user-en-vocab.md" "$HOME/.claude/user-en-vocab.md"

# Directories
backup_and_link "$DOTFILES_DIR/claude/agents" "$HOME/.claude/agents"
backup_and_link "$DOTFILES_DIR/claude/hooks" "$HOME/.claude/hooks"

# Skills
for skill in "$DOTFILES_DIR"/skills/shared/* "$DOTFILES_DIR"/skills/claude/*; do
    is_linkable_skill_dir "$skill" || continue
    backup_and_link "$skill" "$HOME/.claude/skills/$(basename "$skill")"
done
restore_preserved_skill_links "$CLAUDE_SKILLS_PRESERVE_FILE" "$HOME/.claude/skills"
prune_stale_dotfiles_links "$HOME/.claude/skills"
rm -f "$CLAUDE_SKILLS_PRESERVE_FILE"

# Legacy command shims were removed (skills are directly user-invocable as
# /skill-name); prune any leftover shim links from earlier installs.
prune_stale_dotfiles_links "$HOME/.claude/commands"

# Prune retired CLI links that pointed into this repo.
prune_stale_dotfiles_links "$HOME/.local/bin"

# -----------------------------------------------------------------------------
# Codex CLI configuration
# -----------------------------------------------------------------------------
echo "[9/10] Installing Codex CLI configuration..."
mkdir -p "$HOME/.codex"
backup_and_link "$DOTFILES_DIR/codex/AGENTS.md" "$HOME/.codex/AGENTS.md"
# config.toml is seeded once, then owned by the live Codex runtime (it appends
# projects/hooks/desktop state); unconditional copy would clobber live drift.
if [ ! -e "$HOME/.codex/config.toml" ]; then
    backup_and_copy "$DOTFILES_DIR/codex/config.toml" "$HOME/.codex/config.toml"
    configure_codex_local_permissions "$HOME/.codex/config.toml"
else
    echo "  ~/.codex/config.toml already exists, skipping config seed"
fi
# machine.md symlinks to the shared canonical (~/.config/machine.md) seeded in
# the Claude Code step above — same file both agents read, no divergence.
backup_and_link "$HOME/.config/machine.md" "$HOME/.codex/machine.md"
backup_and_link "$DOTFILES_DIR/codex/bin" "$HOME/.codex/bin"
backup_and_link "$DOTFILES_DIR/codex/agents" "$HOME/.codex/agents"
backup_and_link "$DOTFILES_DIR/codex/hooks" "$HOME/.codex/hooks"
/usr/bin/python3 "$DOTFILES_DIR/codex/hooks/install_hooks.py" \
    "$DOTFILES_DIR/codex/hooks.json" "$HOME/.codex/hooks.json"
mkdir -p "$HOME/.codex/rules"
for rule in "$DOTFILES_DIR"/codex/rules/*.rules; do
    [ -f "$rule" ] || continue
    backup_and_link "$rule" "$HOME/.codex/rules/$(basename "$rule")"
done
ensure_real_dir "$HOME/.codex/skills"
ensure_real_dir "$HOME/.agents/skills"
# NOTE: codex/skills/.system was removed from the repo — codex-cli manages and
# updates its own system skills under ~/.codex/skills/.system; vendoring a
# snapshot here only re-installs stale copies over the live ones.
for skill in "$DOTFILES_DIR"/skills/shared/* "$DOTFILES_DIR"/skills/codex/*; do
    is_linkable_skill_dir "$skill" || continue
    backup_and_link "$skill" "$HOME/.codex/skills/$(basename "$skill")"
done
prune_stale_dotfiles_links "$HOME/.codex/skills"
for skill in "$DOTFILES_DIR"/skills/shared/*; do
    is_linkable_skill_dir "$skill" || continue
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
# Postcondition: no dangling agent/skill links may survive an install run
# -----------------------------------------------------------------------------
DANGLING=0
for dir in "$HOME/.claude/skills" "$HOME/.claude/commands" "$HOME/.codex/skills" "$HOME/.agents/skills"; do
    [ -d "$dir" ] || continue
    while IFS= read -r link; do
        echo "  WARNING: dangling symlink: $link -> $(readlink "$link")" >&2
        DANGLING=$((DANGLING + 1))
    done < <(find "$dir" -maxdepth 1 -type l ! -exec test -e {} \; -print)
done
if [ "$DANGLING" -gt 0 ]; then
    echo "  [!] $DANGLING dangling link(s) found — fix before relying on skills." >&2
    echo "  Installation FAILED the postcondition check." >&2
    exit 1
fi

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
