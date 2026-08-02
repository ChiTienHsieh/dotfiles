---
name: headless-agents
description: "Delegate bounded read-only research, review, extraction, or parallel investigation to Codex subagents from Claude Code or Codex. Use when the user asks for a headless agent/subagent, says 'run Codex on this', wants a fresh second opinion or parallel read-only checks, or needs isolated structured output. Prefer native Codex subagents when available; use the bundled codex exec wrapper from Claude Code or when process isolation is required. Never use this skill for file mutation or untrusted web content."
---

# Headless Codex Delegation

Use Codex as the default headless worker. Keep each task bounded, read-only,
independently verifiable, and small enough to finish without live steering.

## Choose the surface

1. **Codex parent with native subagents:** Prefer `spawn_agent` for parallel or
   delegated work. Native subagents avoid a nested CLI process and keep status,
   cancellation, and synthesis in one session.
2. **Claude Code parent:** Run the bundled `scripts/run-codex-readonly.sh`.
   This is the normal Claude -> Codex route.
3. **Codex parent needing a clean CLI process:** Use the wrapper only when the
   user explicitly wants headless CLI execution, a disposable clean context,
   or `--output-schema` validation.
4. **Writes, approvals, or live steering:** Use `tmux-orchestration` and an
   interactive worker. Never grant a headless worker write access.

Grok is an optional independent perspective, not the default worker for this
skill. Do not fan out across providers merely because they are available.

## Native Codex subagents

- Start with one subagent. Use two or three only when the work divides into
  genuinely independent questions that can run concurrently.
- Give each subagent a distinct responsibility and a self-contained prompt.
  Pass raw artifacts and acceptance criteria, not the parent's diagnosis.
- Keep all delegated work read-only unless the user separately authorizes an
  implementation workflow.
- Ask for evidence paths, commands, or line references that the parent can
  verify cheaply. The parent owns synthesis and the final judgment.
- Do not spawn duplicate agents with the same prompt. More votes are not more
  evidence.

## Claude Code -> Codex wrapper

Resolve `<skill-dir>` to this skill's installed directory, usually
`~/.claude/skills/headless-agents` in Claude Code or
`~/.codex/skills/headless-agents` in Codex.

```bash
<skill-dir>/scripts/run-codex-readonly.sh \
  --cwd "$PWD" \
  --model gpt-5.6-terra \
  --effort medium \
  -- "Review src/auth for concrete correctness risks. Cite file paths and lines."
```

The wrapper prints only the final answer plus artifact paths. It stores the
full JSONL event stream separately so the parent does not waste context on
Codex progress events. Use `--prompt-file FILE` for long prompts and
`--schema FILE` when the result must match a JSON Schema.
Artifact paths inside `--cwd` are rejected so even the trusted harness cannot
dirty the workspace.

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
- runs ephemerally with approval policy `never`;
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
boundary instead of this skill. Omit explicit output paths to get the isolated
defaults.

These controls bound model tools, not the Codex control plane: the CLI still
needs HTTPS access to OpenAI to run the model. In Claude Code `auto` mode, the
parent may therefore classify or approve OpenAI service domains even though the
Codex worker's shell network remains disabled.

Never add bypass flags. Never use the wrapper on repositories that contain
secrets outside the denied patterns or on untrusted prompt-bearing content. A
read-only agent can still send every permitted input to its model provider.

## Model and effort

- `gpt-5.6-terra` + `medium`: default for everyday research, review, and repo
  exploration.
- `gpt-5.6-luna` + `low`: simple extraction, classification, or cheap broad
  screening with deterministic acceptance criteria.
- `gpt-5.6-sol` + `high`: difficult architecture, security, or final-judge
  work where quality matters more than latency.

Do not default to `max`. Increase model or effort only after a representative
task shows a quality gap. When tuning a recurring workflow, compare the same
effort and one level lower as recommended by OpenAI.

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
- If Claude Code blocks OpenAI control-plane access, approve only the specific
  service-domain request or move the check to an interactive surface. Do not
  disable Codex's permission profile.
- If the task grows beyond a one-shot check, stop and route it through
  `tmux-orchestration` instead of turning headless execution into a hidden
  long-running worker.
