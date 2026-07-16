---
name: headless-agents
description: "Delegate bounded, one-shot, read-only checks to headless Claude CLI workers. Use when the user explicitly asks for headless, detached, or `claude -p` execution, or when a parallel check can be completed solely from supplied stdin with all model tools disabled. Repository tools require an explicit headless request; Codex/Gemini requests, generic second opinions, network-heavy work, and every file mutation follow worker-routing and tmux-orchestration instead."
allowed-tools: Bash
---

# Headless Agents Delegation

Use headless execution only when a one-shot worker needs neither approval nor
live steering. The orchestrator still owns process supervision, result review,
and integration.

## Choose the surface first

- An **implicit** bounded parallel check may use only the Claude stdin recipe
  below, with all model tools disabled. The orchestrator supplies the complete
  artifact; the worker does not inspect the repository.
- Claude repository inspection with `Read`, `Glob`, or `Grep` is available only
  when the user explicitly asks for headless execution or `claude -p`.
- Generic second opinions, interactive work, approvals, Bash/network access,
  and every mutation follow `codex/notes/worker-routing.md` and
  `tmux-orchestration`.
- Codex and Gemini CLI have no verified hard-isolation recipe in this setup.
  Route their repo and web requests through an observable tmux surface until
  such a recipe is tested; filesystem sandboxing or avoiding permissive flags
  does not disable inherited MCP, plugin, or external API side effects.

Read-only is not shorthand for side-effect-free. A filesystem read-only sandbox
may block local writes while leaving inherited MCP servers, plugins, browser
integrations, or external API tools active. It is also not path confinement or
a confidentiality boundary: a worker may read more than the prompt names, and
model input is sent to its provider. Never expose secrets or untrusted
prompt-bearing content. Prefer the stdin/no-tools recipe when the artifact
itself is enough; a Git worktree does not change these boundaries.

## Claude CLI

### Implicit-safe artifact pass: stdin, zero tools

```bash
claude -p --model fable --effort medium --permission-mode dontAsk \
  --safe-mode --no-chrome --strict-mcp-config --tools "" \
  --no-session-persistence \
  "Analyze only the artifact from stdin and return findings." < "$INPUT"
```

This is the only recipe eligible for implicit bounded checks. It disables model
tools and user/project customizations; centrally managed policy may still
apply. The shell supplies the complete artifact. Review the input first because
it is still sent to Anthropic.

### Repository pass: explicit headless requests only

```bash
claude -p --model fable --effort medium --permission-mode dontAsk \
  --safe-mode --no-chrome --strict-mcp-config --tools "Read,Glob,Grep" \
  --no-session-persistence \
  "Inspect only the named repository paths and return findings. Do not edit."
```

Run this only from a trusted repository with a narrow, explicit path scope.
Tool allowlisting removes write tools but does not prove filesystem confinement:
`Read`, `Glob`, and `Grep` may access other readable paths. If the task needs
Bash, network, writes, approvals, or live steering, use tmux instead.

### Fable effort and quota

- Use `--effort medium` by default. Reserve `max` for ambiguous, high-risk
  reasoning whose expected benefit justifies much faster quota burn.
- Consult the `quota` skill before expensive fan-out and after a limit error;
  provider priority and reset handling stay in their existing SSOTs.

## Supervision and completion

Judge progress from process state plus meaningful output, not quiet stdout.
Reuse the observation and intervention cadence in `tmux-orchestration` instead
of defining a second polling policy here. Per the user's explicit expectation,
do not label a still-running Claude worker as timed out before one hour; an
approval wait, clear error, or confirmed no-progress state may still require the
earlier intervention defined by that SSOT.

`You've hit your session limit` is quota exhaustion, not a timeout. Preserve
captured output, report the exact terminal state, consult the `quota` skill,
then resume or reroute according to the user's model intent.
