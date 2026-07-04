cmux 是次要 surface；主入口見 ../SKILL.md。

# cmux Orchestration

Use this skill to run a controller agent that coordinates one or more interactive Codex agents in separate cmux surfaces. Keep the controller focused on task design, read-only inspection, verification, and small fixes; delegate implementation, cross-file edits, and debugging to Codex surfaces.

## When To Use

- Use for multi-agent orchestration, parallel research, implementation handoff, or review loops where each worker should remain visible in cmux.
- Use when a Claude Code or Codex controller needs to start, observe, or resume multiple Codex agents without delegating implementation through file-mutating headless `codex exec`.
- Use when task completion should be detected by cmux events or marker files instead of terminal visual state.
- Do not use for a small single-agent edit where normal Codex work in the current session is enough.

## Safety Rules

- Use cmux surfaces plus interactive Codex CLI with normal approvals or auto-review.
- Delegate workers to new cmux surfaces by default. Do not create a new cmux window
  or workspace unless the user specifically asks for that.
- Never delegate file-mutating work with `codex exec` (a `workspace-write` sandbox or higher); that must run on an observable interactive Codex surface. Read-only headless Codex is the only exception: `codex review`, and `codex exec --sandbox read-only` for research/debug when credential paths are denied and network is off.
- Never use YOLO, bypass, or danger flags, including `--dangerously-bypass-approvals-and-sandbox`.
- Do not ask workers to weaken sandboxing, disable approvals, edit secrets, or bypass guardrails.
- Keep long prompts in files and send one-line instructions that point Codex at those files.
- Verify worker claims with read-only checks before accepting results.
- Store task prompts, logs, and handoff reports in an ignored scratch directory unless the user explicitly asks for tracked artifacts.
- Dotfiles is a public guardrail source of truth: keep task logs and handoffs out of the repo, and ensure guardrail diffs are human-reviewed before push.
- Record every cmux delegation in the local delegation history file so `wrap`
  can offer to close delegated surfaces later.

## Sandbox Escalation for System Commands

Some commands genuinely cannot run inside a worker's sandbox, and no allowlist
tweak will ever fix them. On macOS the Seatbelt sandbox (used by Codex) refuses
to `exec` setuid-root, SIP-protected binaries: `/bin/ps` is
`-rwsr-xr-x ... restricted`, so a sandboxed `ps` fails with `execvp ...
Operation not permitted` (no Seatbelt-denial line is even logged). `sysctl`
reads are denied too. No `sandbox_permissions` value (`disk-full-read-access`,
etc.) helps — verified empirically. The same applies to a freshly built binary
that internally shells out to `ps`/`sysctl` (e.g. a system-sensing CLI): the
child inherits the sandbox and the inner `exec` of `ps` still fails. The ONLY
way to run these is OUTSIDE the sandbox.

So when you delegate a command the worker's sandbox will block — process/system
introspection (`ps`, `sysctl`, `vm_stat`), or running a local binary that does
so — explicitly instruct the worker in the prompt to request **un-sandboxed
execution** via the normal on-request escalation, with safe, honest framing:
state that the command is a safe read-only system query, or a non-destructive
local binary in a trusted project, so the reviewer (`auto_review`) can approve
it. This is verified to work: workers self-test this way and `auto_review`
approves non-destructive reads/test runs in trusted projects.

This is NOT the same as weakening the sandbox or bypassing guardrails (still
forbidden, see Safety Rules). Escalation keeps approvals in force — the reviewer
still decides per command. Never instruct a worker to use
`--dangerously-bypass-approvals-and-sandbox`, to set `sandbox_mode =
"danger-full-access"` globally, or to edit config to disable the sandbox.
`approval_policy = "on-request"` + `auto_review` is the recommended setup and
already supports this; the only missing piece is telling the worker to actually
escalate instead of giving up. As controller (Claude Code runs unsandboxed for
cmux/system calls), independently re-verify any result the worker produced via
escalation.

## Completion Watching Without Foreground Long-Polling

Do not block the controller in a foreground poll loop waiting for a worker's
completion — it burns the controller's context and stalls other pipelines.
Prefer an event-based watcher: subscribe to `cmux events` in the background and
wake the controller on the worker's Codex stop event, then verify the worker's
report marker. The real event stream is `cmux events`; useful flags include
`--name`, `--category`, `--after`, `--after-seq`, `--cursor-file`,
`--reconnect`, `--limit`, `--no-ack`, and `--no-heartbeat`. For Codex turn
completion, start with:

```bash
cmux events --name agent.hook.Stop --no-ack --no-heartbeat --reconnect
```

Filter the NDJSON yourself for the expected `workspace_id`, `source`, and any
available payload correlation such as `session_id`. There is no real
`--surface-id`, `--workspace-id`, `turn-complete`, `surface-idle`, or
`agent-idle` event filter. If exact worker correlation is uncertain, or the
event stream is unavailable, falls behind its replay window, or hits a slow
consumer condition, fall back to marker-file polling in a background job.

## Codex Computer-Use Capability

As of June 2026, Codex should not be treated as terminal-only. OpenAI's
April 2026 Codex update added background computer use for the Codex desktop app
on macOS: Codex can see, click, and type in local apps with its own cursor, and
multiple Codex agents can work on the same Mac in parallel without taking over
the user's active app. OpenAI also added an in-app browser, image generation,
multiple terminal tabs, file previews, SSH devbox support, and plugin/MCP based
app integrations.

When orchestrating through cmux, this means Codex can be a good worker for
tasks that require direct local UI operation, browser inspection, screenshots,
or apps that do not expose APIs, not only repo edits and shell commands. Do not
assume every interactive `codex` surface has computer use available: tell the
worker to check its available skills/tools, and only delegate UI-control work
to a Codex session that exposes Computer Use or Browser capabilities. UI actions
must still follow normal approvals, sandboxing, and Computer Use confirmation
rules for deletion, account changes, sensitive-data transmission, purchases,
system settings, and other risky side effects.

## Orchestrator Mental Model (controller role)

The controller is an interface and judgment layer, not a doer. Internalize these:

- **Don't build heavy artifacts yourself.** Generating and maintaining large
  outputs (HTML artifacts, long docs, multi-file code) is worker work. The
  controller specs it and delegates it, even when the controller technically
  could produce it. Producing it yourself burns the controller's context for
  no reliability gain.
- **A fresh worker is as trustworthy as the controller doing it — often more.**
  When you don't fully trust one worker's output, do NOT re-do the work
  yourself to check it. Spawn a second, fresh Codex to review the first one's
  output. A fresh worker has clean context and is at least as reliable as the
  controller, and this saves the controller's tokens. Worker-reviews-worker is
  the default verification path for substantial artifacts; reserve the
  controller's own read-only checks for small, load-bearing claims.
- **For guardrail, prompt, and skill reviews, follow the reviewer-routing SSOT.**
  User-level `~/.codex/AGENTS.md` defines the current reviewer policy.
- **The controller is the human's translation layer.** The user often finds
  Codex too verbose and does not want to read or talk to Codex directly. The
  controller absorbs the verbose Codex interaction and gives the user short,
  plain, human summaries. Talking to Codex is the controller's job; shielding
  the user from Codex verbosity is the point.

## Controller Workflow

`scripts/...` paths below resolve against this skill's directory
(`~/dotfiles/skills/shared/tmux-orchestration/`), not your cwd.

1. Inspect the task, repo state, allowed edit paths, and stop conditions.
2. Split work into independent prompts with exact deliverables, allowed paths, verification commands, and a marker-file completion contract.
3. Start one new cmux surface per worker, or reuse an existing surface when appropriate. Stay in the current cmux window/workspace unless the user explicitly asks for a new one.
4. Record the delegated surface with `scripts/delegation_history.sh record`.
5. Send each worker a one-line prompt that tells it to read its prompt file.
6. Prefer a background `cmux events` watcher for completion wakeups, then verify the marker file; use marker polling as fallback, not cmux visual "Working" state.
7. Read each worker report, verify important claims, resolve conflicts, and produce the final synthesis.

## cmux Commands

```bash
cmux tree --all
cmux list-pane-surfaces
cmux read-screen --surface surface:N --lines 30
cmux send --surface surface:N -- "text"
cmux send --surface surface:N "\n"
cmux new-surface --type terminal
```

`surface:N` refs are resolved in the current cmux context and can be
ambiguous across workspaces. When inspecting or driving a surface outside the
controller's active workspace, always include the full target:

```bash
cmux read-screen --window window:N --workspace workspace:N --surface surface:N --lines 80
cmux send --window window:N --workspace workspace:N --surface surface:N -- "text\n"
```

If `cmux read-screen` or `cmux send` says `Surface is not a terminal` for a
surface that `cmux tree --all` labels `[terminal]`, first retry with explicit
`--window` and `--workspace`. Do not assume it is a sandbox or permission
problem until the fully targeted command fails the same way. This exact failure
can happen when the controller is in another workspace and `surface:N` resolves
against the wrong context.

Use `cmux new-surface --type terminal` for new workers. `scripts/drive_codex.sh`
pins new worker surfaces to the resolved controller workspace. Avoid
window/workspace creation commands unless explicitly requested by the user.

In the cmux app, use the left sidebar to inspect worker surfaces directly.

## Controller Workspace Targeting

When Claude Code is the controller, export
`CMUX_ORCH_WORKSPACE=<real controller workspace id>` before calling
`scripts/drive_codex.sh`, or otherwise pass it through to the helper. Claude Code's
Bash tool may run in a helper surface whose `$CMUX_SURFACE_ID` belongs to a
different workspace than the visible Claude Code agent TUI, so automatic
lookup from `$CMUX_SURFACE_ID` can target the helper workspace instead of the
workspace the user is watching.

The controller can learn its real workspace from the user or from the
`◀ active` marker in `cmux tree` when the user is focused on the controller
workspace. Codex-as-controller does not need this override because its shell
surface is its controller surface.

Workspace scoping details from the old delegation lessons:

- `agent.hook.Stop` is workspace-scoped, not surface-scoped. Multiple workers
  in one workspace need `session_id` correlation OR a marker/lease file to tell
  them apart.
- cmux replay-window detail: notification events can be suppressed
  (nested/stale sessions); the replay window is bounded (~4096 events); slow
  consumers get disconnected.
- `surface:N` refs are resolved in the current cmux context and can be
  ambiguous across workspaces. When inspecting or driving a surface outside the
  controller's active workspace, include explicit `--window` and `--workspace`
  targets before assuming a sandbox or permission problem.
- Keep marker-file polling as the final completion contract and fallback.

## Delegation History

Every delegated worker surface must be recorded in a local temp history file.
The default path is:

```bash
${CMUX_DELEGATION_HISTORY:-${TMPDIR:-/tmp}/cmux-delegations-$USER.tsv}
```

Use the bundled helper:

```bash
scripts/delegation_history.sh record surface:N PROMPTFILE MARKER OUTFILE "short note"
scripts/delegation_history.sh active
scripts/delegation_history.sh path
```

The history file is intentionally local and temporary. It exists so `wrap` can
identify delegated cmux surfaces from this machine and ask whether to close
them. Do not commit it.

## delegate.sh

Use `scripts/delegate.sh` as the one-command wrapper for routine delegation:

```bash
scripts/delegate.sh "short task title" [PROMPTFILE] [TIMEOUT]
```

It auto-creates a scratch workdir, prompt copy, marker, and report path, then
delegates through `scripts/drive_codex.sh`, which records the worker in delegation
history for later cleanup.

## drive_codex.sh

Use the bundled `scripts/drive_codex.sh` helper to drive one interactive Codex surface and wait for a marker file:

```bash
scripts/drive_codex.sh SURFACE PROMPTFILE MARKER OUTFILE TIMEOUT NEWSURF
```

- `SURFACE`: existing cmux surface, for example `surface:3`.
- `PROMPTFILE`: file containing the worker prompt.
- `MARKER`: completion marker expected in `OUTFILE`, for example `INSTALL_DONE`.
- `OUTFILE`: worker report file to poll.
- `TIMEOUT`: timeout in seconds; defaults to 420 when omitted.
- `NEWSURF`: any non-empty value creates a new cmux terminal surface and starts interactive `codex`.

The helper sends the prompt as one line, sends Enter separately, polls `OUTFILE` for `MARKER`, and prints the report tail when complete.
It also records the delegated surface in the local delegation history file.
When launching Codex in a new surface, the helper auto-accepts Codex's
directory-trust prompt because this orchestrator only launches Codex in
user-owned repositories.

## Marker-File Convention

Do not infer completion from a surface no longer showing "Working"; approval pauses and waiting states can look idle. Even when an event watcher wakes the controller, require every worker to write a report file and end the file with a single marker line:

```text
WORKER_DONE
```

Use distinct markers for distinct workers when multiple agents run in parallel. If the marker does not appear before timeout, inspect the relevant cmux surface manually; the worker may be waiting for approval or blocked.

Marker-file polling is the fallback when events are not reliable enough for exact worker completion. `agent.hook.Stop` is workspace-scoped rather than surface-scoped, notification events can be suppressed, replay is bounded, and slow consumers can be disconnected, so the marker remains the final completion contract.

## Delegation Lessons (shared, maintained)

Before delegating or supervising a worker, read the shared lessons index:

`~/dotfiles/skills/shared/tmux-orchestration/references/lessons.md`

It is a small index. Open ONLY the topic file relevant to the current delegation;
do not read every topic each turn. After the delegation finishes, if you learned a
durable lesson, update the relevant topic file and ensure the index has a one-line
entry. Distill into reusable rules — do not append raw logs or one-off incident detail.
