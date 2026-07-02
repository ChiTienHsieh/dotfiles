# Model Routing

Read this reference only when model choice materially affects delegated work,
long-running work, quota use, or review quality.

The cost rank below reflects actual paid cost, not list price or OpenAI quota;
higher numbers are better.

| Model | Cost | Intelligence | Taste |
| --- | ---: | ---: | ---: |
| `gpt-5.5` | 9 | 8 | 5 |
| `sonnet-5` | 5 | 5 | 7 |
| `opus-4.8` | 4 | 7 | 8 |
| `fable-5` | 2 | 9 | 9 |

Use these as defaults, not ceilings. If the cheaper model's output is below the
bar, upgrade or rerun without asking first; quality matters more than the model
price label.

- When quota state might affect model choice or long-running delegation, use the
  `quota` skill. Do not duplicate CodexBar command details here; `quota` owns
  the safe CLI-backed usage check.
- Treat `cost` as a local override only. For any deliverable, prefer
  `intelligence > taste > cost`.
- Use `gpt-5.5` for batch or mechanical work with explicit specs: data
  analysis, migrations, log triage, and similar implementation chores.
- Use `gpt-5.5` via `codex exec -s read-only`, or `sonnet-5` as the delegated
  worker, for high-token but low-difficulty tasks such as computer use, browser
  operation, repository exploration, batch file reading, and grep-style
  investigation. Prefer `sonnet-5` for automated computer/browser operation.
- Use `opus-4.8` or `fable-5` for user-facing deliverables that need taste,
  including UI, copy, API design, and polished code quality.
- Use `fable-5` or `opus-4.8` to review implementation plans, with optional
  `gpt-5.5` as an independent third perspective.
- Use `fable-5` for the hardest reasoning and architecture decisions.
- Do not use Haiku.

`gpt-5.5` is only available through Codex CLI: use `codex exec` or
`codex review`; `~/.codex/config.toml` defaults to `gpt-5.5`. The Claude rows
above are capability labels; when setting a Workflow or Agent `model` parameter,
use the surface's accepted alias, not the versioned label. In this repo's
Claude command and agent frontmatter, the supported aliases are `sonnet`,
`opus`, and `haiku`; route `fable-5` recommendations through `opus` unless the
specific surface is known to accept Fable or `claude-fable-5`.

If a Workflow or Agent needs `gpt-5.5` for read-only analysis or review,
dispatch a lightweight Claude wrapper such as `model: 'sonnet', effort: 'low'`;
its prompt should build the self-contained Codex prompt, run
`codex exec -s read-only`, and return the raw output. File-changing `gpt-5.5`
work still goes through the visible Codex surface.
