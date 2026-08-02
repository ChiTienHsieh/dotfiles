# GPT-5.6 Prompting Notes

Source checked 2026-08-02: [OpenAI model guidance for GPT-5.6](https://developers.openai.com/api/docs/guides/latest-model?model=gpt-5.6).
Refresh the live page before changing durable guidance when current behavior
matters.

## Model and effort defaults

- `gpt-5.6-sol` is the frontier-capability route; the plain `gpt-5.6` alias
  points to Sol.
- `gpt-5.6-terra` balances intelligence and cost, so this skill uses Terra at
  `medium` for ordinary bounded review.
- `gpt-5.6-luna` is for efficient high-volume work. Do not switch merely
  because a task looks mechanical; compare representative results first.
- The official API efforts are `none`, `low`, `medium`, `high`, `xhigh`, and
  `max`. When tuning, hold the task fixed and compare the current effort with
  one level lower before spending more.

This wrapper deliberately disables nested multi-agent and hosted Programmatic
Tool Calling. Repo review needs native evidence and fresh model judgment
between tool results, so direct read-only shell calls are clearer here.

## Apply these principles

- Start from a prompt that already works. Remove one repeated instruction,
  example group, or irrelevant tool at a time, then rerun the same evals.
- State each instruction once. Expose only task-relevant tools and describe
  their inputs, outputs, and failure behavior precisely.
- Give the outcome, relevant context, hard constraints, required evidence,
  success criteria, and output format. Let GPT-5.6 infer ordinary mechanics.
- Put autonomy and approval boundaries in one compact policy. Repeating
  "ask first" or "do not mutate" can create unnecessary stops.
- Specify what a short answer must retain: conclusion, evidence, material
  caveats, and next action. Remove introductions and repetition first.
- Use concrete tone rules instead of broad labels such as "friendly".
- Do not ask the model to "think harder" or narrate private reasoning. Select
  model and reasoning effort through configuration, then judge the final work.

## Reusable headless prompt

```text
Outcome: [one concrete result]

Context:
- [only facts and artifact paths needed by this worker]

Boundaries:
- Read-only. Do not edit files, change external state, or expand scope.
- Inspect only [paths or supplied artifact].

Evidence and success:
- [what must be cited, measured, or demonstrated]
- Stop when [clear completion condition].

Output:
- [schema or short required structure]
- Lead with the conclusion; retain evidence and material caveats.
```

## Evaluate recurring prompts

Use representative real tasks, not one synthetic happy path. Compare:

1. the existing prompt versus one leaner candidate;
2. the same model and effort;
3. the candidate at one lower effort level;
4. `terra` versus `sol` only when quality requirements justify the comparison.

Measure task success, final-answer completeness, evidence quality, total
tokens, latency, and cost or quota usage. Fewer turns or tokens count as an
improvement only when the final result still passes the same acceptance tests.
