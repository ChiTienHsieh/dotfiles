---
name: "gu-log"
description: "Use when the user or an agent wants gu-log context, mentions gu-log, gu-log-api, or gu-log-ios, or starts work on the blog."
---

# gu-log

Use this skill when the user or another agent asks for context about `gu-log`, `gu-log-api`, `gu-log-ios`, or blog-related work.

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
