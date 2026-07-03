---
name: oracle
description: Use Oracle CLI for hard-bug second opinions, risky reviews, architecture tradeoffs, prompt/file bundle checks, or multi-model sign-off when another frontier model can materially improve agent output.
---

# Oracle

Oracle bundles a prompt plus selected files so another model can answer with real repository context. Use it as an advisory reviewer; verify the result against the codebase and tests before acting.

## When to use

- Use Oracle for hard bugs, architecture tradeoffs, risky refactors, complex reviews, prompt reviews, design checks, or when the current agent is stuck.
- Use Oracle when a second model can catch blind spots before editing or shipping.
- Do not use Oracle for simple local facts, tiny edits, or anything that would expose secrets unnecessarily.

## Safety

- Never attach secrets by default: `.env`, private keys, tokens, credentials, cookies, browser profiles, or local-only machine notes.
- Prefer a tight file set plus a clear prompt over whole-repo dumps.
- Always preview large or sensitive bundles before sending:
  `oracle --dry-run summary --files-report -p "<task>" --file "src/**" --file "!**/*.test.*"`
- API mode can cost money. Start an API run only when the user explicitly requested it or already approved spending tokens for this task.
- Browser mode may automate Chrome/ChatGPT and may require login or Keychain prompts. Use manual/copy fallback when automation would be disruptive.

## Default workflow

1. Run `oracle --help` once per session before first use.
2. Write a standalone prompt: project stack, relevant paths, exact question, constraints, attempts, errors, and desired output.
3. Attach files with `--file`; include directories/globs and explicit excludes.
4. Preview with `--dry-run summary --files-report`.
5. Prefer browser mode for the user's ChatGPT Pro workflow; choose the best approved Pro model shown by `oracle --help`:
   `oracle --engine browser --model "<model-from-oracle-help>" -p "<task>" --file "src/**"`
6. For manual fallback, build and copy the bundle:
   `oracle --render --copy -p "<task>" --file "src/**"`

## Long-running sessions

- Long browser or Pro runs can detach or time out. Do not blindly rerun the same prompt.
- Check recent sessions with `oracle status --hours 72`.
- Reattach with `oracle session <session-id-or-slug>`.
- Use `--slug "<3-5 words>"` for readable session names on important runs.

## Prompt shape

Include:

- Repository and stack summary.
- Relevant entry points and directories.
- The exact decision, bug, or review request.
- What has already been tried.
- Hard constraints and non-goals.
- Output format, such as "findings with file references", "patch plan", or "three options with tradeoffs".

Keep the prompt specific. Oracle starts with no implicit project memory.
