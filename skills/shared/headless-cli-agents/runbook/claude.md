# Claude as worker

**If you ARE Claude Code, use the built-in `Agent` tool — never shell out to `claude -p`.**
The CLI lane below is only for callers on a different runtime (Codex, Grok).

## Native lane (caller is Claude Code)

- `Agent` tool with the six-part spec as the prompt. Subagents default to Sonnet
  (`CLAUDE_CODE_SUBAGENT_MODEL` in `claude/settings.json`); pass a bigger `model` only when
  the task needs it and say why in the report.

## CLI lane (caller is Codex or Grok)

```bash
SPEC=/abs/path/spec.md; OUT=/abs/path/claude-out.md
claude -p "$(cat "$SPEC")" --permission-mode auto --output-format text > "$OUT"
```

- `--permission-mode auto` is mandatory: `bypassPermissions` exits 1 on the first tool use.
- `claude -p --permission-mode auto` is **not** a kernel sandbox profile. Writes are limited to cwd
  plus the `~/.claude/settings.json` allow-list, and the `auto` classifier — not a human — gates
  escalation. This lane is weaker than the codex/grok lanes: feed it trusted inputs only.
- There is no separate credential-deny profile to pass for this lane. Before delegating, run
  `grep -A10 '"deny"' ~/.claude/settings.json` and treat THAT output as ground truth — do not assume
  `.env` reads are blocked. As of 2026-09-03 the live file denies `Read(~/.ssh/**)` and
  `Read(~/.aws/**)` but does **not** deny `Read(./.env)` / `Read(./.env.*)`. Do not point this lane at
  a tree with live `.env` secrets unless the verification command shows that deny present.
- It loads `~/.claude/CLAUDE.md` including `@` imports, so it sees the shared `codex/AGENTS.md`.
