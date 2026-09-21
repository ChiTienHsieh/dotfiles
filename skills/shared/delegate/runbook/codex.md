# Codex as worker

**If you ARE Codex, use Codex's built-in subagent — never shell out to `codex exec`.**
The CLI lane below is only for callers on a different runtime (Claude Code, Grok).

## Before delegating

- `codexbar usage --provider codex --source cli`: the weekly window usually runs out first.
  Low quota → fall back to Claude; headless Codex is an option, never an obligation.

## CLI lane (caller is Claude Code or Grok)

```bash
SPEC=/abs/path/spec.md; OUT=/abs/path/codex-out.md
mkdir -p "$(dirname "$OUT")"          # -o does not create parent dirs
codex exec -p cc-worker --skip-git-repo-check \
  --model gpt-5.6-luna -c model_reasoning_effort=medium \
  -o "$OUT" - < "$SPEC"
```

- **Never put any `--sandbox` flag next to `-p cc-worker` / `-p cc-worker-ro`.** `--sandbox`
  overrides the profile's `default_permissions`, so the credential deny list silently stops
  applying (`codex-cli 0.153.0`: `-p cc-worker --sandbox workspace-write` reads `.env.sample`
  fine; `-p cc-worker` alone gets `Operation not permitted`). The banner prints
  `sandbox: workspace-write` either way, so it is not evidence. Verify by `cat` on a deny-listed
  file — e.g. create `.env.sample` in a scratch git dir and run the exact command there.
- Read-only lane: `codex exec -p cc-worker-ro ...` (same command, different profile). It loads
  `~/.codex/cc-worker-ro.config.toml` (repo: `codex/cc-worker-ro.config.toml`): `:read-only`
  base plus the same credential denies. Plain `read-only` only blocks writes, not reads, so
  without the profile it would read `.env`/`~/.ssh` into context and send them to OpenAI.
- `codex review` has no `-p` flag (`codex review --help`), so it runs without a kernel profile:
  trusted input only.
- `-p cc-worker` loads `~/.codex/cc-worker.config.toml` (repo: `codex/cc-worker.config.toml`):
  `:workspace` base (workspace-write + network off) plus explicit credential denies. That TOML is
  the only source of the deny list — read it, do not trust a copy:
  `grep -n deny ~/.codex/cc-worker.config.toml`.
- The profile must be a TOML file; `-c permissions...."**/*.pem"` fails (dotted-key parser
  splits on `.pem`), so deny globs only work from a file loaded with `-p`.
- From Claude Code run it with `dangerouslyDisableSandbox: true` and absolute paths (see SKILL.md rule 3).
- `codex exec` loads `~/.codex/AGENTS.md`. If those rules forbid the task it exits 0 with an
  empty diff and a polite refusal: treat as refused, fix the rule, do not paper over it with a preamble.
- `--search` is a top-level flag (`codex --search exec ...`) and turns network on; only over trusted inputs.
- Models: the live default in `~/.codex/config.toml` is `gpt-5.6-sol` (hard work);
  `gpt-5.6-luna` is the routine worker model. `model_reasoning_effort` low|medium|high|xhigh.
  Anything else: `codex exec --help`.

## Quirks

Dated observations that affect delegation. Delete a line once it stops being true. TUI / app
quirks (terminal title, font blowup, thread rename) live in `codex/notes/codex-cli.md`.

- **tmux always goes through Guardian** (2026-07-29, `codex-cli 0.145.0`): the permissions profile
  has no tmux socket allowlist, so every tmux command — read-only included — needs scoped escalation
  and Guardian review. `codex/rules/tmux.rules` marks tmux `prompt` as a second layer. Do not add a
  read-only tmux exception (socket permissions see a path, not a subcommand), do not build a
  "deny, then tell the agent to retry escalated" PreToolUse hook (`ask` is unsupported and a denied
  retry cannot be proven escalated), and never keep a broad command-runner allow rule such as
  `["uv", "run"]` — `uv run tmux …` matches the outer allow and skips the tmux prompt. The guarantee
  covers commands Codex submits, not child processes an approved program spawns on its own.
- **Hooks load only at session start** (2026-08-08, `codex-cli 0.145.0`): `install.sh` merges the
  repo's `codex/hooks.json` into the live `~/.codex/hooks.json` — never symlink or overwrite that
  file. After a first install or a command change, restart Codex and trust the hook via `/hooks`;
  an existing session never picks it up. Per the official hooks manual the unified `exec_command`
  tool name is `Bash` and `PostToolUse` output lands in `tool_response`.
- **CodexBar and the Keychain**: use `codexbar usage --provider both --source cli`; plain
  `codexbar usage` imports browser cookies and can raise a macOS Keychain Safe Storage prompt that
  blocks a non-interactive agent. It often takes ~30s — wait 60s before calling it hung, and rerun
  outside the sandbox if the sandboxed attempt fails.
- **`codex review`** (2026-07-04, `0.142.5`): inside Claude Code's Bash sandbox it dies with
  `failed to start managed network proxy … reserve managed loopback proxy listeners` because it
  binds a loopback listener — rerun that one command with `dangerouslyDisableSandbox`, do not try
  config variants. It also refuses a custom prompt alongside `--commit` / `--base`; for a simplify
  lens run `codex exec` and let it read `git diff main...HEAD` itself. Skill validation has a fixed
  command: `uv run --with pyyaml python ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py <skill-dir>`.
