---
name: "remember"
description: "Run the `remember` workflow when the user explicitly asks the agent to remember, save, update, or forget durable guidance."
---

# remember

Use this skill when the user explicitly asks the agent to remember, save, update, or forget durable guidance.

## Purpose

Route durable knowledge to the right memory or documentation layer. Do not blindly append to `AGENTS.md`; that file is for normative, always-loaded instructions only.

Always get explicit confirmation before every write, replacement, or removal.

## Step 1: Identify Candidate Memories

Review the conversation for durable items that may help future agents. Skip temporary/session details, one-off task state, trivial facts, and anything already documented in the right place.

For each candidate, ask:
- Would a fresh agent benefit from this later?
- Is it a durable pattern, preference, workflow, or finding?
- Is it specific and actionable enough to record?
- Must this be always loaded for every future agent?

If the answer to "must this be always loaded" is no, do not put it in `AGENTS.md`; route it to lazy notes, project docs, or skip it.

## Step 2: Classify by Layer

Choose the narrowest correct owning layer:

1. **Normative always-loaded instructions/preferences/workflows**
   - Use `~/dotfiles/codex/AGENTS.md` (repo path `codex/AGENTS.md`) for user-level rules every future agent should obey.
   - Use `./AGENTS.md` for project-scoped rules that should always load only in that project.
2. **Investigated quirks, dead ends, version-pinned findings, reference notes, research summaries**
   - Use lazy notes such as `codex/notes/*.md` or the relevant project docs/notes file.
   - Example: Codex CLI quirks belong in `codex/notes/codex-cli.md`, not `codex/AGENTS.md`.
3. **Tool-specific or skill-specific operational rules**
   - Use the relevant tool, skill, or project instruction file only when it is clearly the owning file.
4. **Codex-native memory**
   - Use only when the user explicitly asks to update native Codex memory.
   - Do not make this the default route.
5. **Claude-only project memory**
   - Use only when the user explicitly asks for Claude-specific memory.
6. **Temporary/session details**
   - Skip.

If the requested target is outside the current sandbox, unavailable, or high-friction, explain the safest next step instead of silently writing somewhere else.

## Step 3: Check for Duplicates and Bloat

Before proposing any `AGENTS.md` change:
- Read the target file and check whether similar content already exists.
- Check whether the information really belongs in always-loaded instructions.
- Prefer lazy notes for quirks, dead ends, version-pinned findings, reference notes, and research summaries.
- Keep entries concise and self-contained.

For non-`AGENTS.md` targets, still check nearby existing notes/docs to avoid duplicates.

## Step 4: Present Proposals

For each proposed memory, show:

````markdown
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
### Proposed Entry [Number]

**Target Layer**: [Normative always-loaded | Lazy notes | Tool/skill/project instructions | Codex-native memory | Claude-only memory | Skip]
**Target File**: [path or "none"]
**Category**: [Preferences | Workflow | Quirk | Dead End | Version-Pinned Finding | Reference Note | Tool Rule | Project Rule | Other]

**Proposed Content**:
```markdown
[The exact content to add, replace, or remove]
```

**Why This Target Is Correct**: [Brief routing justification, including whether it must be always loaded]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
````

Then ask for confirmation:

```text
要更新這些記憶嗎？

選項：
- Y: 全部執行
- n: 取消所有
- [1,3,5]: 只執行指定編號
- edit: 我想修改內容
```

## Step 5: Write Only After Confirmation

After confirmation:
1. Re-read the owning target file before editing.
2. Apply only the confirmed additions, replacements, or removals.
3. Preserve existing structure and avoid unrelated cleanup.
4. Report the changed file path and line number when possible.

## Forget and Update Requests

For "forget" or "update" requests:
1. Locate the existing entry in the owning layer.
2. Propose the exact removal or replacement.
3. Explain why that layer owns the entry.
4. Get confirmation.
5. Edit only the owning layer.

If no matching entry is found, say so and list the locations checked.

## Writing Guidelines

- Write concise, actionable entries.
- Use consistent markdown formatting.
- Make entries context-independent; avoid "this session" or relative dates.
- Keep path, command, config key, and model identifiers literal.
- Do not store secrets, tokens, private keys, or machine-specific host details in shared memory.
