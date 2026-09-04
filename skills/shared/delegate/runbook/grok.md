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

- `--sandbox cc-worker` loads `~/.grok/sandbox.toml` (repo: `grok/sandbox.toml`): `workspace` base
  plus a kernel read+write deny list. That TOML is the only source of the deny list — read it, do
  not trust a copy: `grep -n -A8 deny ~/.grok/sandbox.toml`.
- `--allow 'Bash(<verify cmd>:*)'` whitelists exactly the verification command; add nothing broader.
- From Claude Code run it with `dangerouslyDisableSandbox: true` and absolute paths (see SKILL.md rule 3).
- Models: `grok models`; pick with `-m`, reasoning with `--effort`. Anything else: `grok --help`.

## Quirks

- `--permission-mode acceptEdits` is what makes headless writes work (verified 2026-09-03):
  `grok -p … --sandbox cc-worker --permission-mode acceptEdits` wrote a file under the profile.
- `restrict_network` is a no-op on macOS (it is Linux seccomp), and `--disable-web-search` only
  removes Grok's own web tools: a child `curl` still reaches the network. Feed it trusted inputs only.
- `-p` / `--prompt-file` run in the caller's cwd and never create a worktree — isolate by handing it
  a worktree path yourself.
- It loads `~/.claude/CLAUDE.md` but does not expand `@` imports, so it never sees
  `codex/AGENTS.md`: every constraint must be in the spec itself.
- `~` is not expanded in `deny` globs (it resolves to `<cwd>/~/.ssh`), so home-directory entries in
  `grok/sandbox.toml` must be absolute one-segment globs such as `/Users/*/.ssh/**`.
- `codexbar` cannot see SuperGrok quota at all, so `pick-worker` reports it as `n/a`; before a long
  run you only have Grok's own rate-limit errors to go on.
