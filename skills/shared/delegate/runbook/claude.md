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
- There is no separate credential-deny profile for this lane. The live settings file is the only
  source of what is denied — run `grep -n -A10 '"deny"' ~/.claude/settings.json` immediately before
  delegating and treat that output as truth. Do not assume `.env` reads are blocked, and do not
  point this lane at a tree with live secrets unless that output shows the deny you need.

## Quirks

- `claude -p` spends the same subscription quota as an interactive session; it is not a separate
  budget, so it counts against the numbers `pick-worker` reports.
- `--permission-mode bypassPermissions` exits 1 the moment the nested run touches a tool, so a
  nested worker that "did nothing" is usually this, not a refusal. `auto` is the only mode that works.
- It loads `~/.claude/CLAUDE.md` including `@` imports, so it sees the shared `codex/AGENTS.md` —
  a spec that contradicts those rules gets refused rather than obeyed.
- Output goes to stdout; `--output-format text` keeps it parseable. Redirect to an absolute path,
  since the nested run's cwd is the caller's cwd.
