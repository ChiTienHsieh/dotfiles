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

After locating the `gu-log` repo, read `AGENTS.md` first. Follow its identity
detection command, runtime playbook route, and topic-specific SSOT pointers.
Claude Code may then read `CLAUDE.md` for Claude-only tooling details; it does
not replace the shared bootstrap in `AGENTS.md`.

## In-Repo Workflow SOPs

The gu-log repo owns its own workflow SOPs; do not duplicate them here.

- GP/MP source capture, draft, review, refine, translate, and ship: read
  `<gu-log>/tools/gp-pipeline/SKILL.md`, then follow the linked repo SSOT files.
- GitHub issue/PR backlog sweeps: follow the current `AGENTS.md` routing and
  runtime playbook. Keep fan-out analysis read-only and never
  merge/delete/force-push from a sweep.

If a routed file is missing on the current checkout, return to the current
`AGENTS.md` routing table. Do not chase an old branch or retired SOP path.

## Freshness Check

The local checkout may be far behind `origin/main`. Before trusting local state, run:

```bash
git fetch
git status -sb
```

Keep the current task branch as the working source of truth. After fetching,
use `origin/main` only as a comparison/rebase baseline for drift; never replace
the task branch with `origin/main` or infer task intent from the baseline.

## Related Projects

Also use `paths.local` to locate related sibling projects:

- `gu-log-api`
- `gu-log-ios`

Read their local context only when the task touches their API, mobile app, integration points, or cross-repo behavior.
