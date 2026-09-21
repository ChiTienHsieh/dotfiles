#!/usr/bin/env bash

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKUP_DIR="${DOTFILES_BACKUP_DIR:-$HOME/.dotfiles_backup/$(date +%Y%m%d_%H%M%S)}"
TEMP_MANIFESTS=()

cleanup() {
    local manifest

    for manifest in "${TEMP_MANIFESTS[@]}"; do
        rm -f "$manifest"
    done
}
trap cleanup EXIT

backup_existing() {
    local dest="$1"
    local relative backup

    case "$dest" in
        "$HOME"/*) relative="${dest#"$HOME"/}" ;;
        *)
            echo "ERROR: refusing to back up path outside HOME: $dest" >&2
            return 1
            ;;
    esac

    backup="$BACKUP_DIR/$relative"
    if [ -e "$backup" ] || [ -L "$backup" ]; then
        echo "ERROR: backup destination already exists: $backup" >&2
        return 1
    fi
    mkdir -p "$(dirname "$backup")"
    mv "$dest" "$backup"
    echo "  Backed up: $dest -> $backup"
}

link_skill() {
    local src="$1"
    local dest="$2"

    if [ ! -e "$src" ]; then
        echo "ERROR: skill source is missing: $src" >&2
        return 1
    fi

    mkdir -p "$(dirname "$dest")"

    if [ -e "$dest" ] && [ ! -L "$dest" ]; then
        backup_existing "$dest"
    elif [ -L "$dest" ]; then
        rm "$dest"
    fi

    ln -s "$src" "$dest"
    echo "  Linked: $dest -> $src"
}

collect_directory_symlink_entries() {
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

    for entry in "$target"/* "$target"/.[!.]* "$target"/..?*; do
        [ -e "$entry" ] || continue
        printf '%s\t%s\n' "$(basename "$entry")" "$entry" >> "$manifest"
    done
}

ensure_real_directory() {
    local dest="$1"

    if [ -L "$dest" ]; then
        echo "  Replacing directory symlink: $dest -> $(readlink "$dest")"
        rm "$dest"
    elif [ -e "$dest" ] && [ ! -d "$dest" ]; then
        backup_existing "$dest"
    fi

    mkdir -p "$dest"
}

restore_preserved_links() {
    local manifest="$1"
    local dest="$2"
    local name entry

    while IFS=$'\t' read -r name entry; do
        [ -n "$name" ] || continue
        [ ! -e "$dest/$name" ] && [ ! -L "$dest/$name" ] || continue
        [ -e "$entry" ] || [ -L "$entry" ] || continue
        link_skill "$entry" "$dest/$name"
    done < "$manifest"
}

is_skill_directory() {
    local skill="$1"

    [ -d "$skill" ] && [ -f "$skill/SKILL.md" ]
}

prune_stale_dotfiles_links() {
    local dir="$1"
    local link target

    for link in "$dir"/*; do
        [ -L "$link" ] || continue
        target="$(readlink "$link")"
        case "$target" in
            "$REPO_ROOT"/*)
                if [ ! -e "$target" ]; then
                    rm "$link"
                    echo "  Removed stale dotfiles symlink: $link"
                fi
                ;;
        esac
    done
}

sync_skill_directory() {
    local dest="$1"
    shift
    local manifest source_dir skill

    manifest="$(mktemp "${TMPDIR:-/tmp}/dotfiles-skills-preserve.XXXXXX")"
    TEMP_MANIFESTS+=("$manifest")

    collect_directory_symlink_entries "$dest" "$manifest"
    ensure_real_directory "$dest"

    for source_dir in "$@"; do
        for skill in "$source_dir"/*; do
            is_skill_directory "$skill" || continue
            link_skill "$skill" "$dest/$(basename "$skill")"
        done
    done

    restore_preserved_links "$manifest" "$dest"
    prune_stale_dotfiles_links "$dest"
}

echo "Syncing dotfiles skills..."
sync_skill_directory \
    "$HOME/.claude/skills" \
    "$REPO_ROOT/skills/shared" \
    "$REPO_ROOT/skills/claude"
sync_skill_directory \
    "$HOME/.codex/skills" \
    "$REPO_ROOT/skills/shared" \
    "$REPO_ROOT/skills/codex"
sync_skill_directory \
    "$HOME/.agents/skills" \
    "$REPO_ROOT/skills/shared" \
    "$REPO_ROOT/skills/codex"
echo "Skills synced."
