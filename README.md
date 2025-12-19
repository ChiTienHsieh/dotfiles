# Dotfiles

Personal dotfiles for Unix systems. Managed with symlinks.

## Quick Start

```bash
# Clone the repo
git clone --recursive https://github.com/YOUR_USERNAME/dotfiles.git ~/dotfiles

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
├── git/
│   ├── .gitconfig       # Git configuration
│   └── .config/git/ignore  # Global gitignore
├── vim/
│   └── .vimrc           # Vim fallback config
├── gh/
│   └── .config/gh/config.yml  # GitHub CLI config
├── templates/
│   ├── .secrets.template      # API keys template (copy to ~/.secrets)
│   └── .aliases.local.template  # Machine-specific aliases
├── nvim/                # Neovim config (git submodule)
├── install.sh           # Installation script
└── README.md
```

## Post-Installation

1. **Edit `~/.secrets`** - Add your API keys (this file is never committed)
2. **Edit `~/.aliases.local`** - Add machine-specific shortcuts

## Files NOT Tracked

These files are created from templates but not tracked in git:

- `~/.secrets` - API keys and tokens
- `~/.aliases.local` - Machine-specific aliases

## Updating

```bash
cd ~/dotfiles
git pull
git submodule update --recursive
```

## Adding New Dotfiles

1. Add the file to the appropriate directory in `~/dotfiles/`
2. Update `install.sh` to create the symlink
3. Commit and push

## Uninstalling

The install script backs up your original files to `~/.dotfiles_backup/`.
To restore, copy them back from the backup directory.
