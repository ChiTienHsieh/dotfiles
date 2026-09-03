<!-- md-zh-tw: ignore -->

# Dotfiles Repo Instructions

Personal dotfiles managed with symlinks: `install.sh` links from `~` into this
repo (e.g. `~/.zshrc` -> `~/dotfiles/zsh/.zshrc`), so editing either path edits
the same file. Directory layout: see the structure diagram in `README.md`.

## Agent Memory Access

- `~/.codex/AGENTS.md` -> `./codex/AGENTS.md`; `~/.claude/CLAUDE.md` ->
  `./claude/CLAUDE.md`. Edit the repo copies directly; no need to write outside
  the sandbox.

## Autonomous Completion

- Safe, clear changes: work autonomously through review, commit, and push to
  `origin`. Do not stop with unpushed changes — that forces the next agent to
  reconstruct context from scratch.
- This is a PUBLIC repo. Before pushing verify: no secrets, private keys, or
  tokens; no machine-specific host details; no accidental local-only paths.
- Guardrail / SSOT changes (CLAUDE.md, AGENTS.md, settings, skills, playbooks):
  follow the reviewer-routing and simplify-review rules in `codex/AGENTS.md`
  (reviewer choice per the `delegate` skill). Non-interactive review
  is pre-authorized for this repo — run it yourself; do not ask the user to
  approve the review step.
- Stop and ask only for: security concerns, destructive actions,
  force-push/reset/discard decisions, billing or data-loss risk, or
  product/design tradeoffs not inferable from existing instructions.
- Push rejected or CI red → investigate and resolve safe issues yourself first.

## Secrets

- Never in tracked files. Secrets live in `~/.secrets` (created from
  `templates/.secrets.template`), sourced by shell startup, never committed.

## Maintenance Recipes (lazy)

- Aliases, adding new dotfiles, testing shell/tmux changes, nvim submodule
  details: read `codex/notes/dotfiles-maintenance.md` when touching those areas.
  Quick rule: machine-specific content goes to gitignored `bash/.aliases.local`,
  and new dotfiles need an `install.sh` symlink entry.
