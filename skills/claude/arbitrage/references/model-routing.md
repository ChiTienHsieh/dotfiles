# Model Routing

Read this reference only when model choice materially affects delegated work,
long-running work, quota use, or review quality. Subscription state and
provider priority live in `~/dotfiles/codex/notes/worker-routing.md`; read that
first. This file maps task shape to model role and does not maintain subjective
numeric rankings.

- When quota state might affect model choice or long-running delegation, use
  the `quota` skill. Do not duplicate CodexBar command details here.
- Use `gpt-5.6-terra` at `medium` for ordinary headless research, repo
  exploration, review, and mechanical work with explicit acceptance criteria.
- Use `gpt-5.6-luna` at `low` for simple extraction, classification, or broad
  screening whose result is cheap to verify.
- Use `gpt-5.6-sol` at `high` for architecture, security, difficult debugging,
  polished user-facing work, and final-judge passes. Do not default to `max`.
- For recurring work, compare the current effort and one level lower on the
  same representative tasks. Keep the lower setting only when it preserves
  task success and required evidence.
- Use Claude or Grok when cross-provider independence is materially useful,
  especially for reviewing a Codex-authored guardrail or architecture choice.
  Query the installed CLI for current model aliases instead of pinning
  short-lived Claude/Grok names in this reference.
- Prefer the model that meets the acceptance criteria with the least quota and
  latency. Upgrade once when a cheaper route misses the bar; do not run
  same-prompt voting fan-out without a distinct hypothesis for each worker.

OpenAI's live GPT-5.6 guidance is summarized in
`skills/shared/headless-agents/references/prompting-gpt-5.6.md`. Refresh the
official guide before changing durable prompt or model guidance.
