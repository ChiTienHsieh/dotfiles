---
name: headless-agents
description: "Delegate bounded read-only research, review, extraction, or parallel investigation to Codex subagents from Claude Code or Codex. Use when the user asks for a headless agent/subagent, says 'run Codex on this', wants a fresh second opinion or parallel read-only checks, or needs isolated structured output. Prefer native Codex subagents when available; use the installed hardened Codex launcher from Claude Code or when process isolation is required. Never use this skill for file mutation or when readable workspace content cannot be sent to OpenAI."
---

# Headless Codex Delegation

Use Codex as the default headless worker. Keep each task bounded, read-only,
independently verifiable, and small enough to finish without live steering.

## Choose the surface

1. **Codex parent with native subagents:** Prefer `spawn_agent` when the worker
   may share the parent's trust and permission boundary. Native subagents avoid
   a nested CLI process and keep status, cancellation, and synthesis in one
   session.
2. **Claude Code parent:** Run the installed trusted launcher at
   `~/.local/libexec/dotfiles/run-codex-readonly.sh`. This is the normal
   Claude -> Codex route. Invoke that exact launcher with
   Bash's `dangerouslyDisableSandbox: true`; Claude's outer sandbox otherwise
   breaks Codex's control plane and nested OS sandbox.
3. **Codex parent needing enforced isolation:** Use the wrapper when the task
   requires workspace-only reads, disabled shell network, a disposable clean
   context, or `--output-schema` validation. Native subagents inherit the
   parent's permissions; they do not inherit the wrapper's hardened profile.
4. **Writes, approvals, or live steering:** Use `tmux-orchestration` and an
   interactive worker. Never grant a headless worker write access.

## Native Codex subagents

- Treat native delegation as coordination, not a new sandbox. Use the wrapper
  instead when its enforced boundary is part of the acceptance criteria.
- Start with one subagent. Use two or three only when the work divides into
  genuinely independent questions that can run concurrently.
- Give each subagent a distinct responsibility and a self-contained prompt.
  For a fresh or blinded review, pass raw artifacts and acceptance criteria
  without the parent's diagnosis.
- Keep all work under this skill read-only. Route implementation through
  `tmux-orchestration` instead.
- Ask for evidence paths, commands, or line references that the parent can
  verify cheaply. The parent owns synthesis and the final judgment.
- Do not spawn duplicate agents with the same prompt. More votes are not more
  evidence.

## Claude Code -> Codex wrapper

Run `~/dotfiles/install.sh` once after installing or upgrading Claude Code or
Codex. The installer copies a reviewed launcher outside project workspaces,
bakes in canonical executable paths, and idempotently merges only its scoped
Bash rule into the live Claude settings. Claude should invoke the literal
`~/.local/...` path so that rule matches before the shell expands `~`.

```bash
~/.local/libexec/dotfiles/run-codex-readonly.sh \
  --cwd "$PWD" \
  -- "Review src/auth for concrete correctness risks. Cite file paths and lines."
```

The wrapper prints only the final answer plus artifact paths. It stores the
full JSONL event stream separately so the parent does not waste context on
Codex progress events. Use `--prompt-file FILE` for long prompts and
`--schema FILE` when the result must match a JSON Schema.
Artifacts always go to a private per-run directory outside `--cwd`; the wrapper
does not accept caller-selected artifact paths.
The selected workspace must be the caller's current directory or a child, so
`cd` to the intended repository before launch. Prompt and schema files must
also be regular, non-symlink files under that directory.
When invoked under Claude Code, the launcher also resolves the installed
Claude executable in its real ancestor chain and anchors the invocation to
that process's project root. A same-command `cd` outside the project is
rejected. If process verification fails after an upgrade, rerun the installer
instead of weakening the check.

The wrapper prepends one compact worker contract: repository facts must be
verified with read-only tools, never guessed from names or prior knowledge. The
caller should not repeat that generic rule; add only task-specific evidence and
success criteria.

### Enforced boundary

The wrapper intentionally does not use `--sandbox read-only`. That flag selects
Codex's older sandbox system and would bypass the narrower permission profile.
Instead, every run:

- ignores user config and project/global `AGENTS.md` content while retaining
  Codex authentication, so the delegated prompt must be self-contained;
- runs ephemerally with approval policy `never`, non-login shells, and only
  Codex's core command environment instead of parent token/key variables;
- denies filesystem reads by default, then reopens only minimal runtime paths
  and the selected workspace as read-only, with `.env` and common home
  credential paths carved back out;
- points `TMPDIR` at a disposable per-run directory and denies model-command
  network access;
- disables web search, apps, plugins, browser/computer use, image generation,
  hooks, memories, goals, skill search, and nested multi-agent tools;
- writes the final output and trace only through the trusted Codex harness.

The worker may mutate its disposable per-run scratch directory. It must not be
treated as a zero-write process; the enforced promise is no workspace writes,
ordinary outside-workspace reads, or shell network. On macOS with Codex 0.145,
the platform scratch exception still permits access to shared `/private/tmp`
despite deny entries. Never put secrets there before a headless run. A task that
needs strict shared-temp confidentiality must use a stronger external isolation
boundary instead of this skill.

These controls bound model tools, not the Codex control plane: the CLI still
needs HTTPS access to OpenAI to run the model. Claude Code must therefore run
the installed launcher outside its outer Bash sandbox. The permissioned file
is an installer-created regular copy, not the writable skill symlink; it calls
the baked absolute Codex binary instead of resolving caller-controlled `PATH`.
This exception is scoped to that launcher; never use
`dangerouslyDisableSandbox` for a raw `codex` command. The Codex worker's own
shell network remains disabled.
Claude Code documents this parameter as a permission-gated escape hatch for
commands incompatible with its sandbox: <https://code.claude.com/docs/en/sandboxing>.

The load-bearing rule is simple: use the wrapper only when every readable byte
under `--cwd` is allowed to be sent to OpenAI. The `.env` and home credential
denies are defense in depth, not secret detection. Otherwise narrow `--cwd` or
use stronger isolation. Never add bypass flags.

## Model and effort

The operational default is `gpt-5.6-terra` at `medium`. Read
`references/prompting-gpt-5.6.md` before choosing Luna/Sol, changing effort, or
tuning a recurring workflow.

## Prompt contract

Keep the prompt lean and state each rule once. Include:

1. the outcome;
2. only the context needed for this worker;
3. read-only scope and forbidden actions;
4. required evidence and success criteria;
5. exact output shape and stopping condition.

Do not ask for hidden chain-of-thought or prescribe every mechanical step.
Read `references/prompting-gpt-5.6.md` when designing a reusable prompt,
choosing effort, or building an eval.

## Completion and failure handling

- Give ordinary runs at least 10 minutes before treating silence as a timeout.
  A clear non-zero exit or permission error may be handled immediately.
- On success, verify the smallest load-bearing claims from the final artifact.
- On failure, inspect the reported stderr and JSONL paths. Do not rerun with a
  looser sandbox.
- If Claude Code reports control-plane or nested Seatbelt failures, confirm the
  Bash call used `dangerouslyDisableSandbox: true` for the installed launcher.
  Do not weaken the wrapper's Codex permission profile.
- If the task grows beyond a one-shot check, stop and route it through
  `tmux-orchestration` instead of turning headless execution into a hidden
  long-running worker.
