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
- Credential protection is Claude Code's own: its Bash sandbox (writes limited to cwd plus the
  paths listed in `~/.claude/settings.json`, network allowlist) and the `permissions.deny` rules
  there (`Read(./.env)`, `Read(./.env.*)`, `Read(~/.ssh/**)`, `Read(~/.aws/**)`). There is no
  separate profile to pass; confirm the live file still has those rules before delegating:
  `grep -A6 '"deny"' ~/.claude/settings.json`.
- It loads `~/.claude/CLAUDE.md` including `@` imports, so it sees the shared `codex/AGENTS.md`.
- Bills the Claude subscription: `codexbar usage --provider claude --source cli` first.
