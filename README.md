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
│   ├── .secrets.template      # API keys template (copy to ~/.secrets/index.sh)
│   └── .aliases.local.template  # Machine-specific aliases
├── claude/
│   └── CLAUDE.md        # Claude Code instructions (+ SOUL/USER, agents, settings)
├── agents/
│   ├── AGENTS.md        # Shared instructions for Claude, Codex, and Grok
│   └── notes/           # Shared delivery, backlog, and dotfiles recipes
├── codex/
│   ├── AGENTS.md        # Compatibility symlink -> ../agents/AGENTS.md
│   ├── config.toml      # Portable first-install seed
│   ├── cc-worker.config.toml  # Sandbox profile for headless Codex workers
│   ├── hooks.json       # Global Codex lifecycle hook registration
│   ├── hooks/           # Stop dispatcher and bounded hook policies
│   └── pets/            # Codex TUI pet sprites (mogu, shroom)
├── grok/
│   └── sandbox.toml     # Sandbox profile for headless Grok workers
├── skills/
│   ├── shared/          # User-authored skills installed for Claude Code + Codex
│   │   └── delegate/    # how CC / Codex / Grok delegate to each other — map at top of SKILL.md
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

## 共用規則與工具專用設定

`agents/` 放跨工具共用的規則與 notes；`codex/`、`claude/`、`grok/` 保留各自的設定、hooks 與工具專用文件。

兩個 runtime 載入共用規則的方式（Codex 的[官方載入位置](https://learn.chatgpt.com/docs/agent-configuration/agents-md)）：

```text
~/.claude/CLAUDE.md -> <repo>/claude/CLAUDE.md          # @import agents/AGENTS.md
~/.codex/AGENTS.md  = agents/AGENTS.md + codex/AGENTS.md  # install.sh 生成，改完重跑
```

生成前會把內容不同的舊 `~/.codex/AGENTS.md` 備份到 `~/.dotfiles_backup/<時間戳>/`。

`~/.codex` 保留為 runtime 目錄，只連結受管理的檔案／子目錄。既有 `config.toml` 與 session 資料保留；config 只在首次安裝時從 repo 種子建立。不要把整個 `agents/` 或 `codex/` 連成 `~/.codex`，避免把帳號與 session 資料寫進公開 repo。

## Post-Installation

1. **Edit `~/.secrets/index.sh`** - Add your API keys (this file is never committed)
2. **Edit `~/.aliases.local`** - Add machine-specific shortcuts
3. **Skills** - `skills/shared/` is installed into Claude Code and both Codex user-skill paths; `skills/codex/` is installed into Codex's current `~/.agents/skills` discovery path plus the legacy `~/.codex/skills` path; `skills/claude/` is installed only into Claude Code. For how the agents hand work to each other — when to delegate, who gets it, how to dispatch, how to accept — start at the map at the top of `skills/shared/delegate/SKILL.md`
4. **Codex hooks** - Start a new Codex CLI session, open `/hooks`, review the global `PostToolUse` and `Stop` commands, then trust them explicitly.
5. **Machine-specific Git settings** - Put credential helpers or host-only Git overrides in optional `~/.gitconfig.local`; the tracked config includes it last.

## Files NOT Tracked

These files are created from templates but not tracked in git:

- `~/.secrets/` - API keys and tokens (never committed)
- `~/.aliases.local` - Machine-specific aliases
- `~/.gitconfig.local` - Machine-specific Git settings
- `~/.bunfig.toml`, `~/.npmrc`, `~/.config/pnpm/rc` - Real local files; the installer preserves registry credentials and only upserts the tracked release-age policy

## Updating

`level-up` 的公開概念進度隨 skill 放在 [learning/](skills/shared/level-up/learning/INDEX.md)，新機器可以直接接著學；私人補充放 `~/.local/share/level-up/learning/`，不在這個公開 repo。

既有 clone 升級前，先把舊 `skills/shared/level-up/learning/`（含未提交檔）複製到 repo 外，更新會取代舊追蹤檔；舊資料放私人目錄的 `archive/<日期>/`。讀寫規則見 [學習紀錄](skills/shared/level-up/references/learning-records.md)。

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
