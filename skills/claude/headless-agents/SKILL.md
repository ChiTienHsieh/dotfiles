---
name: headless-agents
description: "Delegate bounded, one-shot, read-only checks to headless Codex or Claude CLI workers. Use when the user explicitly asks for headless, detached, `claude -p`, or `run codex` execution, or when a parallel check can be completed solely from supplied stdin with all model tools disabled. Repository tools require an explicit headless request; generic second opinions, Gemini, network-heavy work, and every file mutation follow worker-routing and tmux-orchestration instead."
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
- Repository inspection with `Read`, `Glob`, `Grep`, or Codex tools is available
  only when the user explicitly asks for headless execution, `claude -p`, or a
  named CLI worker.
- Generic second opinions, interactive work, approvals, Bash/network access,
  and every mutation follow `codex/notes/worker-routing.md` and
  `tmux-orchestration`.
- Gemini CLI has no verified hard read-only mode in this setup. Route Gemini
  requests through an observable tmux surface; `-p`, quiet output, and avoiding
  `--yolo` do not themselves disable its file tools.

Read-only is a **write boundary**, not path confinement or a confidentiality
boundary. A worker may be able to read more than the prompt names, and model
input is sent to its provider. Never expose secrets or untrusted prompt-bearing
content. Prefer the stdin/no-tools recipe when the artifact itself is enough.
A Git worktree and a CLI working-directory flag do not change this boundary.

## Codex CLI: explicit headless requests only

### Repository analysis without live web

```bash
OUTPUT="${TMPDIR:-/tmp}/codex-research.md"
mkdir -p "$(dirname "$OUTPUT")"
codex exec -s read-only --skip-git-repo-check -C "$REPO" \
  -o "$OUTPUT" \
  "Inspect only the named paths for this task. Return findings; do not edit."
```

`-s read-only` blocks model-initiated writes. `-C` selects the working
directory; it does not confine reads to that directory. `-o` is written by the
Codex harness so the result can still be captured under a read-only sandbox.
Name the allowed paths in the prompt and exclude secrets from the worker's
readable inputs.

### Live web research: explicit opt-in

```bash
OUTPUT="${TMPDIR:-/tmp}/codex-websearch.md"
mkdir -p "$(dirname "$OUTPUT")"
codex --search exec -s read-only --skip-git-repo-check -C "$REPO" \
  -o "$OUTPUT" \
  "Research this bounded question and cite the sources used."
```

`--search` is a top-level flag and enables a higher-risk surface. Use it only
when the user explicitly requested live research and the local/web inputs are
trusted. Network access creates prompt-injection and data-disclosure risk even
though writes remain blocked; route broad or untrusted web work through tmux.
Never use danger or bypass flags.

## Claude CLI

### Implicit-safe artifact pass: stdin, zero tools

```bash
claude -p --model fable --effort medium --permission-mode dontAsk \
  --safe-mode --no-chrome --strict-mcp-config --tools "" \
  --no-session-persistence \
  "Analyze only the artifact from stdin and return findings." < "$INPUT"
```

This is the only recipe eligible for implicit bounded checks. It disables model
tools and inherited integrations; the shell supplies the complete artifact.
Review the input first because it is still sent to Anthropic.

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
