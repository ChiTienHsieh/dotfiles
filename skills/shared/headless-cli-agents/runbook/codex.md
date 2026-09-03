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
codex exec -p cc-worker --sandbox workspace-write --skip-git-repo-check \
  --model gpt-5.6-luna -c model_reasoning_effort=medium \
  -o "$OUT" - < "$SPEC"
```

- Read-only variant: same command with `--sandbox read-only`; keep `-p cc-worker` so the
  credential deny still applies.
- `-p cc-worker` loads `~/.codex/cc-worker.config.toml` (repo: `codex/cc-worker.config.toml`):
  `:workspace` base, network off, deny on `~/.ssh`, `~/.aws`, `**/.env*`, `**/*.pem`. Plain
  `--sandbox workspace-write` alone still reads credentials — the profile is what blocks it.
- The profile must be a TOML file; `-c permissions...."**/*.pem"` fails (dotted-key parser
  splits on `.pem`).
- From Claude Code run it with `dangerouslyDisableSandbox: true` and absolute paths (see SKILL.md rule 3).
- `codex exec` loads `~/.codex/AGENTS.md`. If those rules forbid the task it exits 0 with an
  empty diff and a polite refusal: treat as refused, fix the rule, do not paper over it with a preamble.
- `--search` is a top-level flag (`codex --search exec ...`) and turns network on; only over trusted inputs.
- Models: `gpt-5.6-luna` routine, `gpt-5.6-sol` hard; `model_reasoning_effort` low|medium|high|xhigh.
  Anything else: `codex exec --help`.
