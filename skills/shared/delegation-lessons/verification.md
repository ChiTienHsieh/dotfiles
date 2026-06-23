---
name: verification
description: How the controller verifies worker output without redoing the work.
type: delegation-lesson
updated: 2026-06-23
---

## Use when
A worker reports done and the controller must accept or reject.

## Lessons
- Verify load-bearing claims with cheap read-only checks: grep for leftover references,
  `git status` / `git diff --stat`, confirm files moved/deleted, read only the one
  section whose accuracy matters.
- For large artifacts, delegate the FULL review to a fresh worker rather than re-reading
  everything yourself — a clean-context reviewer is at least as reliable and saves the
  controller's context.
- `wc -l` before opening a big file; read the load-bearing slice, not the whole thing.
