# Dotfiles

[![CI](https://github.com/ChiTienHsieh/dotfiles/actions/workflows/ci.yml/badge.svg)](https://github.com/ChiTienHsieh/dotfiles/actions/workflows/ci.yml)

Personal dotfiles for Unix systems. Managed with symlinks.

Prerequisite: Python 3.11 or newer must be available as `python3` on `PATH`.

## Quick Start

```bash
# Clone the repo
git clone --recursive https://github.com/ChiTienHsieh/dotfiles.git ~/dotfiles

# Run install script
cd ~/dotfiles
./install.sh

# Reload shell
source ~/.bash_profile
```

## What's Included

```
dotfiles/
├── bash/
│   ├── .bash_profile    # Main bash config (login shell)
│   ├── .bashrc          # Non-login shell config
│   ├── .bash_prompt     # Terminal prompt styling
│   └── .aliases         # Aliases and functions
├── bun/
│   └── .bunfig.toml     # Seed for local Bun safeguards
├── git/
│   ├── .gitconfig       # Git configuration
│   └── .config/git/ignore  # Global gitignore
├── vim/
│   └── .vimrc           # Vim fallback config
├── tmux/
│   └── .tmux.conf       # Tmux configuration
├── gh/
│   └── .config/gh/config.yml  # GitHub CLI config
├── templates/
│   ├── .secrets.template      # API keys template (copy to ~/.secrets)
│   └── .aliases.local.template  # Machine-specific aliases
├── claude/
│   └── CLAUDE.md        # Claude Code instructions (+ SOUL/USER, agents, settings)
├── codex/
│   ├── AGENTS.md        # Codex CLI instructions
│   ├── config.toml      # Portable first-install seed
│   ├── hooks.json       # Global Codex lifecycle hook registration
│   ├── hooks/           # Stop dispatcher and bounded hook policies
│   └── pets/            # Codex TUI pet sprites (mogu, shroom)
├── skills/
│   ├── shared/          # User-authored skills installed for Claude Code + Codex
│   ├── codex/           # User-authored Codex-only skills
│   └── claude/          # User-authored Claude Code-only skills
├── scripts/
│   └── sync-skills.sh   # Sync only user-authored skill symlinks
├── nvim/                # Neovim config (git submodule)
├── npm/
│   └── .npmrc            # Seed for local npm safeguards
├── pnpm/
│   └── .config/pnpm/rc   # Seed for local pnpm safeguards
├── install.sh           # Installation script
└── README.md
```

## Post-Installation

1. **Edit `~/.secrets`** - Add your API keys (this file is never committed)
2. **Edit `~/.aliases.local`** - Add machine-specific shortcuts
3. **Skills** - `skills/shared/` is installed into Claude Code and both Codex user-skill paths; `skills/codex/` is installed into Codex's current `~/.agents/skills` discovery path plus the legacy `~/.codex/skills` path; `skills/claude/` is installed only into Claude Code
4. **Codex hooks** - Start a new Codex CLI session, open `/hooks`, review the global `PostToolUse` and `Stop` commands, then trust them explicitly. The installer never writes or bypasses hook trust.
5. **Machine-specific Git settings** - Put credential helpers or host-only Git overrides in optional `~/.gitconfig.local`; the tracked config includes it last.

## Files NOT Tracked

These files are created from templates but not tracked in git:

- `~/.secrets` - API keys and tokens
- `~/.aliases.local` - Machine-specific aliases
- `~/.gitconfig.local` - Machine-specific Git settings
- `~/.bunfig.toml`, `~/.npmrc`, `~/.config/pnpm/rc` - Real local files; the installer preserves registry credentials and only upserts the tracked release-age policy

## Updating

```bash
cd ~/dotfiles
git pull
git submodule update --recursive
```

To sync only user-authored skills without reinstalling other dotfiles:

```bash
./scripts/sync-skills.sh
```

The skill-only sync preserves unrelated skills, backs up conflicting real files
or directories under `~/.dotfiles_backup/`, and removes broken symlinks that
point into this dotfiles checkout. It does not modify runtime settings such as
`~/.claude/settings.json`.

## Adding New Dotfiles

1. Add the file to the appropriate directory in `~/dotfiles/`
2. Update `install.sh` to create the symlink
3. Commit and push

## Uninstalling

The install script backs up your original files to `~/.dotfiles_backup/`.
To restore, copy them back from the backup directory.
