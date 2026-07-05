# Delegation Lessons

Shared, maintained lessons for the `tmux-orchestration` skill. Read this small
index before delegating or supervising a worker, then open only the relevant
section. Distill durable rules; do not append raw logs or one-off incident
detail.

## tmux driving

Use when driving an interactive agent in a tmux pane from a controller.

- tmux/cmux socket access is already in the sandbox allowlist. Run commands
  normally; only request escalation if a real socket error occurs.
- Launch a worker with `codex --sandbox workspace-write`. Set cwd to a writable
  scratch dir (for example under `/tmp`) when the worker must write a report
  while only reading another repo; set cwd to the target repo when the worker
  must edit that repo.
- Send the instruction line, wait briefly, then send Enter separately. Put long
  prompts in a file; the send-line just says "Read PATH and do it."
- Capture panes (`capture-pane -p`) to confirm progress; do not assume idle
  means done.
- Before `send-keys` to an agent pane, capture first and confirm it is not
  showing an interactive dialog such as AskUserQuestion or an approval UI.
  Text plus Enter sent into that dialog can choose an option for the user
  (2026-07-04 %3 near miss). User-pending dialogs must be operated by the user.
- Shared-tree commit mutex: when another controller edits the same working
  tree, notify it and wait for an ACK before committing. A 2026-07-04 race had
  two controllers commit across each other, sweeping one side's staged files
  under the other's commit message.

Failure patterns:

- `/quit` needs a moment before the next launch command; sleep before
  relaunching.
- A directory-trust prompt appears on first Codex launch in a new dir; answer 1.

## worker prompts

Use when writing a prompt file for a delegated worker.

- Use fixed nouns "CC" and "user", never 你/我 — a relative pronoun flips
  referent when a different agent reads the prompt.
- Marker-file 完工合約: write output to PATH, end the file with one exact
  MARKER line. The controller polls the marker, not the visual "Working" state.
- State the side-effect boundary up front: READ-ONLY research, or exactly which
  paths may be edited, plus "do not commit/push" when the controller verifies
  first.
- Put long instructions in the file; keep the send-line a one-liner pointing at
  it.
- Token-efficient delegation means not reading the worker output stream. It is
  not mainly about choosing interactive vs exec surfaces; 2026-07-02 gu-log
  tests showed the token savings come from marker/report polling.
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

- Verify load-bearing claims with cheap read-only checks: grep for leftover
  references, `git status` / `git diff --stat`, confirm files moved/deleted,
  read only the one section whose accuracy matters.
- Fresh-reviewer 驗證原則: for large artifacts, delegate the FULL review to a fresh worker rather than
  re-reading everything yourself — a clean-context reviewer is at least as
  reliable and saves the controller's context.
- `wc -l` before opening a big file; read the load-bearing slice, not the whole
  thing.
- Long pane/transcript reviews follow the same principle: the controller does
  not read the full scrollback itself — spawn a cheap subagent (e.g. haiku) to
  capture the pane and report highlights, then personally verify only the
  load-bearing slices. (2026-07-06, user-directed after the controller started
  reading two full coach sessions inline.)
