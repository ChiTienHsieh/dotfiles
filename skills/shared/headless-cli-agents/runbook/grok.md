# Grok as worker

**If you ARE Grok, use the `spawn_subagent` tool — never shell out to `grok -p`.**
The CLI lane below is only for callers on a different runtime (Claude Code, Codex).

## Before delegating

- SuperGrok quota is separate and `codexbar` cannot read it, so Grok is the overflow lane:
  use it when both Claude and Codex are low, and watch Grok's own rate-limit errors.

## CLI lane (caller is Claude Code or Codex)

```bash
SPEC=$(mktemp -t grok-spec).md; OUT=/abs/path/grok-out.md    # write the spec into $SPEC first
grok --prompt-file "$SPEC" --sandbox cc-worker --permission-mode acceptEdits \
  --allow 'Bash(pytest:*)' --disable-web-search --no-auto-update > "$OUT"
```

- `--sandbox cc-worker` loads `~/.grok/sandbox.toml` (repo: `grok/sandbox.toml`): `workspace`
  base plus kernel deny (read + write) on `**/.env*`, `**/*.pem`, `/Users/*/.ssh/**`,
  `/Users/*/.aws/**`. `~` is not expanded in `deny` — use absolute globs.
- `restrict_network` is a no-op on macOS and `--disable-web-search` only removes Grok's own
  web tools: a child `curl` still reaches the network. Feed it trusted inputs only.
- `--allow 'Bash(<verify cmd>:*)'` whitelists exactly the verification command; add nothing broader.
- `-p` / `--prompt-file` run in the cwd and never create a worktree.
- It loads `~/.claude/CLAUDE.md` but does not expand `@` imports, so it never sees
  `codex/AGENTS.md`: every constraint must be in the spec itself.
- From Claude Code run it with `dangerouslyDisableSandbox: true` and absolute paths (see SKILL.md rule 3).
- Models: `grok models`; pick with `-m`, reasoning with `--effort`. Anything else: `grok --help`.
