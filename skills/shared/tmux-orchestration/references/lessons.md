# Delegation Lessons

Dated incident lessons for the `tmux-orchestration` skill. Durable delegation
rules live in SKILL.md (Delegation Contract) — do not restate them here. Open
only the relevant section; distill new lessons into dated, reusable rules
without raw logs.

## tmux driving

Use when driving an interactive agent in a tmux pane from a controller.

- tmux socket access is intentionally absent from `workspace-sprin`; every tmux
  command must go through Guardian automatic approval review.
- Launch a worker with `codex --sandbox workspace-write`. Set cwd to a writable
  scratch dir (for example under `/tmp`) when the worker must write a report
  while only reading another repo; set cwd to the target repo when the worker
  must edit that repo.
- Before `send-keys` to an agent pane, capture first and confirm it is not
  showing an interactive dialog such as AskUserQuestion or an approval UI.
  Text plus Enter sent into that dialog can choose an option on the user's
  behalf (2026-07-04). User-pending dialogs must be operated by the user.
- Shared-tree commit mutex (2026-07-04): when another controller edits the same
  working tree, notify it and wait for an ACK before committing; otherwise one
  side's staged files end up under the other's commit message.
- Launch a Claude worker with cwd set to the worktree it will operate on.
  A worker whose commands are `cd <other-dir> && git ...` never matches its
  `Bash(git ...)` allowlist prefixes, so every step needs a manual approval
  (2026-07-06).
- Verification-flavored tasks need their allowedTools to pre-include the
  verification surface: `gh run *`, `gh api *`, `curl *`, preview-server and
  screenshot tools — otherwise the worker stalls on approvals exactly at the
  verify step.

Failure patterns:

- `/quit` needs a moment before the next launch command; sleep before
  relaunching.
- A directory-trust prompt appears on first Codex launch in a new dir; answer 1.
- `agent-send-prompt.sh` fails (input swallowed) when the pane is showing an
  approval dialog — clear the dialog first, then send.

## hooks vs merge commits

Use when a worker's commit is blocked by a pre-commit/pre-push hook.

- Per-file hooks that are not merge-aware will re-flag files a merge brings in
  from main unchanged (they already passed CI on their own PRs). That is a
  false positive, not a violation — but the fix still needs authority.
- Never `--no-verify` or any equivalent (hooksPath override, env tricks). No
  hook enforces this (2026-07-06); it is a standing prompt-level rule, and a
  rule being technically unenforced is not permission.
- Resolution ladder: (1) propose the durable fix to the user — make the hook
  merge-aware, or commit a permanent ignore entry (that is repo/machine
  policy, so it is the user's call); (2) only when the user has already
  explicitly authorized the OUTCOME (e.g. "merge both") and the hook is the
  user's own machine-level check misfiring on unchanged files: a temporary
  on-disk edit to the checker's own ignore config is acceptable, but it must
  be fully documented in the task report, kept out of the commit (verify with
  `git status --short -- <file>` before and `git show HEAD --stat` after),
  and restored via `git restore` (not `rm` — it is tracked) with a diff
  against HEAD to confirm byte-identical. Silent or undocumented = bypass.
  When in doubt, ask.

## worker prompts

Use when writing a prompt file for a delegated worker. (Contract fields, fixed
nouns, side-effect boundary: see SKILL.md「Delegation Contract」.)

- Token-efficient delegation means not reading the worker output stream
  (2026-07-02): the savings come from marker/report polling, not from choosing
  interactive vs exec surfaces.
- Cheapest ground truth first: before contracting any "reproduce / copy /
  match X" task, spend one read-only check hunting for X's direct source (a
  public repo behind a *.github.io page, a package, an export). Reproducing
  from rendered output when the source is directly obtainable wastes a whole
  worker run.
- Inherited red gates: worker contracts must say "an out-of-contract CI
  failure = report it, do not fix it" — otherwise every parallel worker
  independently fixes the same inherited failure and the fix lands N times.

## verification

Use when a worker reports done and the controller must accept or reject.
(Load-bearing-claim checks and the fresh-reviewer principle: see the
`delegate` skill's `## Accept`.)

- `wc -l` before opening a big file; read the load-bearing slice, not the whole
  thing.
- Long pane/transcript reviews follow the same principle: the controller does
  not read the full scrollback itself — spawn a cheap subagent to capture the
  pane and report highlights, then personally verify only the load-bearing
  slices (2026-07-06).
