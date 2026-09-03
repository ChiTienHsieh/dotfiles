---
name: delegate
description: "Use when planning or delegating implementation, research, or review to another agent — choosing which provider or worker gets the job, answering quota / rate-limit / usage-reset questions, or running the codex, grok, or claude CLIs headlessly (codex exec, grok -p, claude -p). Owns the whole path: when to delegate at all, which role goes where, the sandbox profile that makes write mode safe, the spec contract, and the acceptance rules."
allowed-tools: Bash
---

# Delegate

Loaded by Claude Code, Codex, and Grok alike (Grok discovers it through `~/.claude/skills`).

```
DELEGATION MAP     [A]=always-loaded  [L]=lazy  [R]=computed at runtime
------------------------------------------------------------------------
[A] codex/AGENTS.md "委派與跨 agent": native subagent first; file-writing
    CLI only via `delegate`; never bypass; tmux read-only by default
                 |  "heavy task / tool loop / need a 2nd opinion"
                 v
[L] skills/shared/delegate/SKILL.md   (this file; README.md points here)
    1 WHEN   <=10-line edit -> do it yourself
             >20 same-shape loops, ssh/gh sweeps, bulk edits -> delegate
    2 WHO    [R] scripts/pick-worker -> provider + reason + reset time
             roles: impl -> most quota | review -> bounded read-only
                    guardrail reviewer -> fresh, strongest Claude
    3 HOW    provider == my runtime? --yes--> native subagent
                      | no                   (Agent / codex / spawn_subagent)
                      v
             runbook/<provider>.md  <- profile: codex/cc-worker.config.toml
             (exact CLI flags + quirks)         grok/sandbox.toml
    4 ACCEPT spec in a file; re-run verification yourself; empty diff =
             refusal; guardrail changes -> fresh reviewer before push
------------------------------------------------------------------------
[persona] claude/agents/orchestrator.md (`cldo`): same path, stricter WHEN
[L] skills/shared/tmux-orchestration: a different SURFACE (visible panes),
    human-invoked only; WHEN/WHO/ACCEPT still come from here
```

## When

- A single-file edit of ~10 lines or less, or anything where the delegation overhead exceeds the work: do it yourself.
- Delegate by default when a task is about to burn the controller's context on mechanical iteration, even if each step looks trivial: more than ~20 same-shaped tool loops (read/grep/edit cycles, log trawling), SSH command batches against remote hosts, GitHub sweeps across many issues/PRs/runs, broad web research with many fetches, bulk edits across many files.
- Delegate when the work needs a spec, acceptance criteria, and a separate implementation owner — including frontend work, where the controller keeps design intent and does the visual validation.
- Keep judgment, scope, architecture, debugging root-cause analysis, diff review, and git ownership in the controller session. Delegate the concrete fix once the cause is clear.
- Escape hatch: do not predict that a worker will fail — dispatch first. If it misses the acceptance criteria twice after concrete corrective feedback, keep the useful parts of the diff and finish it yourself.
- The `cldo` persona (`claude/agents/orchestrator.md`) tightens this same rule: as orchestrator, CC may only do read-only investigation, acceptance, and the ≤10-line single-file fix; everything else is delegated.

## Who

Roles, not provider names — `scripts/pick-worker` picks the provider from live quota.

- **Heavy implementation** (bulk edits, many files, long runs) → the current runtime's built-in subagent, or a headless CLI worker under the sandbox profile; take the provider with the most remaining quota. Headless is an option, never an obligation.
- **Review, read-only research, second opinion** → a bounded read-only worker; a different provider is fine and often useful here. Do not raise the surface cost just to switch provider.
- **Guardrail / prompt / SSOT reviewer** → always a fresh Claude subagent on the strongest Claude model, doing safety and simplify in one pass. Fresh is what matters, not the provider: the author carries the change's context and is the blindest to stale flags and self-contradiction. Codex is deliberately not used for this role (over-defensive, pads redundant context); keep its bounded read-only reviewer for code review that needs an opposing view.

Model principles:

- For any deliverable, prefer `intelligence > taste > cost`; cost is a local override, never the deciding factor.
- Cheap models are fine for mechanical work with an explicit spec (migrations, log triage, batch file reading, grep-style investigation). Taste work — UI, copy, API design, architecture, plan review — goes to the strongest model available.
- Never delegate to Haiku; it hallucinated badly in the user's experience.
- Never silently swap a model the user named. If quota forces a change, say so first.

## How

1. Run `~/.claude/skills/delegate/scripts/pick-worker` (absolute path — `~/.codex/skills/...` also resolves via symlink, but only the `~/.claude/skills` path is guaranteed across all three runtimes, since Grok discovers this skill through it and has no symlink of its own; in Claude Code add `dangerouslyDisableSandbox: true`, since codexbar writes its cookie cache and fails inside the sandbox). It prints remaining quota, a recommendation with a reason, and the matching `runbook/<provider>.md`. `--provider <name>` forces one; `--quiet` prints only the recommendation.
2. **If the recommended provider is the runtime you are running in, use your native subagent** (Claude Code: `Agent` tool; Codex: built-in subagent; Grok: `spawn_subagent`). Never shell out to your own CLI. The CLI lane in each runbook is for callers on a *different* runtime.
3. Write the spec, dispatch per the runbook, then apply the acceptance rules below.

Three absolute rules:

1. **Write mode needs the sandbox profile.** Any headless CLI that may touch files runs under a kernel sandbox profile that limits writes to the worktree, denies *reading* credential paths, and turns network off where the platform supports it. No profile → read-only only. **Read-only mode also needs the profile**: read-only blocks writes, not reads, so without the profile credentials would still be read into the model context. The only profile-free exception is `codex review`.
2. **Never bypass.** `danger-full-access`, `--dangerously-bypass-*`, `--yolo`, `bypassPermissions` are banned in every mode, no exceptions.
3. **A CLI with its own sandbox runs outside Claude Code's Bash sandbox** (`dangerouslyDisableSandbox: true`; nested Seatbelt fails with `sandbox initialization failed`) and gets absolute paths — `$TMPDIR` differs inside and outside the sandbox.

Spec contract, six parts, every delegation: objective · files in scope · interfaces (signatures, schemas, CLI contracts to honor) · constraints · verification command · reasoning effort. Put it in a file and pass the absolute path.

Frontend validation loop: the controller writes design intent and acceptance criteria into the spec; the worker implements inside its ownership boundary; the controller runs the app, screenshots it, writes concrete visual feedback, and re-dispatches until the UI matches intent and verification passes.

## Accept

- The controller re-runs the verification command itself; the worker's "tests pass" is a claim, not proof.
- "Done" with an empty diff is a refusal (often the worker's own instructions blocked it), never a success.
- Verify load-bearing claims with cheap read-only checks: grep for leftover references, `git status` / `git diff --stat`, confirm files moved or deleted, read only the one section whose accuracy matters.
- `wc -l` before opening a big file, then read the load-bearing slice. For long worker output, have a cheap subagent summarize it and personally verify only the slices that decide acceptance — a clean-context reviewer is at least as reliable as a controller carrying a long thread.
- For a large artifact, delegate the FULL review to a fresh worker instead of re-reading everything. If one dimension fails, fix it and rescore that dimension only; the rescore prompt must carry the original fail criterion, what changed, which slice to re-evaluate, and whether neighboring dimensions need a light sanity check.
- Every worker contract states "an out-of-contract CI failure is reported, not fixed" — otherwise parallel workers each fix the same inherited red gate and it lands N times.
- Cheapest ground truth first: before contracting any "reproduce / copy / match X" task, spend one read-only check hunting for X's direct source (a public repo behind a rendered page, a package, an export). Reproducing from rendered output when the source is obtainable wastes a whole worker run.
- Guardrail / SSOT changes: commit, then a fresh reviewer per `## Reviewer 授權`, then push.

## Fallback

1. Built-in subagent hits a wall → finish it in the current agent if that stays inside the `## When` threshold.
2. Still blocked → move review or research to another provider's bounded read-only worker.
3. Every provider low → `pick-worker` prints the earliest reset time; sleep until then (small buffer, keep no locks or half-written files) or run `--provider grok`, whose quota codexbar cannot see.
4. Re-run `pick-worker` after waking, then continue the interrupted work. Never recite quota numbers from memory; if the reset time is unclear, report the blocker instead of guessing.

## Reviewer 授權

- 使用者持續授權其他 agent（含已設定的外部 AI reviewer）做 review，不必逐次詢問。
- 送出 diff、prompt 或檔案前先檢查實際待傳資料有沒有 secret、憑證、private key 或未公開個資；發現敏感內容、無法判斷，或目的地與範圍超出既有 reviewer workflow 時才停下確認。
- 這項授權只涵蓋 review：不授權 reviewer 寫檔、執行外部 mutation，或繞過其他工具與權限邊界。
- guardrail / SSOT 改動的 reviewer 同時做 safety 與 simplify review。simplify 看三件事：只針對單次事故的過窄規則、過度工程化、能不能換成更通用的說法；逐項回報 Keep / Simplify / Drop。

Upstream: adapted from `blader/arbitrage` at `ccfd55098cc9e0b9910bc5c0f67a16a2fd61d5bd`.
