---
name: "gu-log"
description: "Use when the user or an agent wants gu-log context, mentions gu-log, gu-log-api, or gu-log-ios, or starts work on the blog."
---

# gu-log

## Machine Paths

Read `paths.local` in this skill directory before looking for repositories. It contains machine-specific checkout paths for:

- `gu-log`
- `gu-log-api`
- `gu-log-ios`

If `paths.local` is missing, tell the user to copy `paths.local.example` to `paths.local` and fill in the local checkout paths.

Do not copy machine-specific paths into tracked files, GitHub issues, PRs, docs, or reports intended for public repos.

## Repository Context

After locating the `gu-log` repo, read these files in order when they exist:

1. `CLAUDE.md`
2. `AGENTS.md`
3. `TODO.md`
4. `WRITING_GUIDELINES.md`
5. `CONTRIBUTING.md`

Use those files as the in-repo context for agent behavior, project conventions, writing style, current work, and contribution workflow.

## In-Repo Workflow SOPs

The gu-log repo owns its own workflow SOPs; do not duplicate them here.

- SP article draft/review/refine/translate/ship: read
  `<gu-log>/.agents/skills/sp-pipeline-sop/SKILL.md`, then follow the linked
  repo SSOT files.
- GitHub issue/PR backlog sweeps: read
  `<gu-log>/.agents/skills/backlog-sweep/SKILL.md`; keep fan-out analysis
  read-only and never merge/delete/force-push from a sweep.

If those SOP files are missing on the current checkout, they have not been
merged yet (introduced in gu-log PR #541, branch `agents/sop-modes`); check
that branch, or fall back to the repo SSOT docs listed above.

## Freshness Check

The local checkout may be far behind `origin/main`. Before trusting local state, run:

```bash
git fetch
git status -sb
```

Prefer `origin/main` as the source of truth for content when the local checkout is stale or diverged.

## Related Projects

Also use `paths.local` to locate related sibling projects:

- `gu-log-api`
- `gu-log-ios`

Read their local context only when the task touches their API, mobile app, integration points, or cross-repo behavior.
