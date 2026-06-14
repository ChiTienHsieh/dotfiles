<!-- md-zh-tw: ignore -->

# Dotfiles Repo - Codex Instructions

## What This Repo Is

Personal dotfiles managed with symlinks. `install.sh` creates symlinks from `~` to this repo.

Example: `~/.bashrc` → `~/dotfiles/bash/.bashrc`

Editing either path modifies the same file (symlink = pointer to same inode).

## Directory Structure

```
bash/      → shell config (.bash_profile, .bashrc, .aliases, .bash_prompt)
git/       → git config (.gitconfig, .config/git/ignore)
vim/       → vim fallback (.vimrc)
tmux/      → tmux config (.tmux.conf)
gh/        → GitHub CLI (.config/gh/config.yml)
nvim/      → neovim config (git submodule)
Codex/    → Codex config (AGENTS.md = user memory)
templates/ → templates for secrets/local aliases (not symlinked directly)
```

## CC User Memory Access
- `~/.Codex/AGENTS.md` is symlinked to `./Codex/AGENTS.md`
- **Edit `./Codex/AGENTS.md` directly** — no need to access outside sandbox

## Key Conventions

### Autonomous Completion
- Agents touching this dotfiles repo SHALL work autonomously through review, commit, and push to `origin` when the requested change is safe and the intent is clear.
- Do not stop with local-only or unpushed changes after making a safe educated choice. Leaving dotfiles changes unpushed forces the next agent to reconstruct context from scratch.
- Before pushing, verify the content is safe and appropriate for a public dotfiles repo: no secrets, no private keys, no tokens, no machine-specific host details, and no accidental local-only paths.
- For guardrail / SSOT changes, use the repo safety flow: make the change, review the diff, commit, get an independent Codex review when available, then push only if the review finds no blocking issue.
- For this dotfiles repo's guardrail / SSOT changes, the user explicitly authorizes non-interactive `codex review` of the relevant commit or unpushed diff. Codex MUST run that review itself and MUST NOT ask the user to approve the review step unless the review command remains blocked after trying the normal approved/escalated path or authentication is missing.
- Stop and ask the user only for security concerns, destructive actions, force-push/reset/discard decisions, billing or data-loss risk, or product/design choices where the correct tradeoff cannot be inferred from existing instructions.
- If push is rejected or CI/checks fail, investigate and resolve safe issues yourself. Ask only when resolution requires one of the stop conditions above.

### Aliases
- **Portable aliases** → `bash/.aliases` (tracked in git)
- **Machine-specific aliases** → `bash/.aliases.local` (gitignored, symlinked to ~/.aliases.local)
- Use functions for anything needing arguments or logic
- Keep alias names short (2-4 chars preferred)

**Why .aliases.local is in this repo (but gitignored)?**
So Codex can edit it in sandbox mode. Sandbox allows writes to cwd (~/dotfiles) but not arbitrary paths like ~/.aliases.local.

### Secrets
- **NEVER** add API keys or secrets to tracked files
- Secrets go in `~/.secrets` (created from `templates/.secrets.template`)
- `.secrets` is sourced by `.bash_profile` but never committed

### Adding New Dotfiles
1. Add file to appropriate directory (e.g., `bash/.newconfig`)
2. Update `install.sh` to create symlink
3. Update README.md structure diagram if needed

## Testing Changes

After editing shell configs:
```bash
source ~/.bash_profile   # or just: src
```

For tmux changes:
```bash
tmux source-file ~/.tmux.conf
# or from inside tmux: prefix + :source-file ~/.tmux.conf
```

## Submodules

`nvim/` is a git submodule. Update with:
```bash
git submodule update --recursive
```

## Nvim Config Details
- Uses **LazyVim** as base distribution
- Completion: **blink.cmp** (switched from nvim-cmp for performance)
- AI: Copilot with ghost text (`zbirenbaum/copilot.lua`)
- Gamification: triforce.nvim (requires `nvzone/volt` dependency)
- Config location: `nvim/` submodule → separate repo (ChiTienHsieh/nvim-config)

## What NOT To Do

- Don't commit secrets or API keys
- Don't add machine-specific paths to tracked files (use ~/.aliases.local)
- Don't forget to update install.sh when adding new dotfiles
