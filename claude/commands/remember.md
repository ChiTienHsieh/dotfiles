---
disable-model-invocation: true
allowed-tools: [Read, Edit, Grep]
argument-hint: [category]
---

# Memory Update Command

Your task is to review this conversation session and decide what's worth remembering long-term by updating CLAUDE.md files.

## Step 1: Analyze the Conversation

Scan the entire conversation history for:

**Personal-level insights** (→ `~/.claude/CLAUDE.md`):
- New preferences or habits discovered about the user
- Communication style adjustments that worked well
- General workflows or approaches the user prefers
- Learning style insights
- Tool preferences (e.g., "prefers uv over conda")

**Project-level insights** (→ `./CLAUDE.md` in project root):
- Tech stack decisions
- Architecture choices and reasoning
- Code patterns or conventions established
- Known issues, gotchas, or workarounds discovered
- Project-specific workflows
- Important dependencies or configurations

**Skip these**:
- Temporary context (one-off tasks)
- Trivial details that won't matter in future sessions
- Information already well-documented elsewhere
- Session-specific references (e.g., "Option 8 we discussed")

## Step 2: Quality Filter

For each potential memory, ask:
- Would a fresh Claude instance benefit from knowing this?
- Is this a pattern or just a one-time thing?
- Would forgetting this cause repeated explanations?
- Is this specific and actionable enough?

If NO to most → don't record it.

## Step 3: Present Proposals

For each memory worth recording, present in this format:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
### Proposed Entry [Number]

**Target File**: [~/.claude/CLAUDE.md | ./CLAUDE.md]
**Category**: [e.g., Tech Stack | Preferences | Workflows | Known Issues]

**Proposed Content**:
```markdown
[The actual markdown content to add]
```

**Why Remember This**: [Brief justification]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Step 4: Get User Confirmation

After presenting all proposals, ask:
```
要更新這些記憶嗎？

選項：
- Y: 全部加入
- n: 取消所有
- [1,3,5]: 只加入指定編號
- edit: 我想修改內容
```

## Step 5: Update Files

Once confirmed:
1. Read the target CLAUDE.md file(s) to check current structure
2. Find the appropriate section to add the new content
   - If section doesn't exist, create it
   - If similar content exists, note it and ask user before overwriting
3. Use the Edit tool to update the file(s)
4. Confirm completion with file path and line numbers

## Writing Guidelines

**DO**:
- Write concise, actionable entries
- Use consistent markdown formatting
- Make entries self-contained (no session references)
- Be specific: "Use `uv` for Python dependency management" > "User likes modern tools"
- Include brief context when needed

**DON'T**:
- Write long paragraphs (use bullet points)
- Include temporary information
- Reference "this session" or "today" (use dates if needed: [2025-11-15])
- Duplicate information already in CLAUDE.md

## Example Output Structure

```
我分析了這次對話，發現 3 個值得記住的內容：

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
### Proposed Entry 1

**Target File**: ./CLAUDE.md
**Category**: Tech Stack

**Proposed Content**:
```markdown
## Tech Stack
- Backend: FastAPI 0.104+
- Database: PostgreSQL 14+ with SQLAlchemy 2.0
- Testing: pytest with pytest-asyncio
```

**Why Remember This**: Established the core technology choices for this project. Will guide all future implementation decisions.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[... more proposals ...]

要更新這些記憶嗎？[Y/n/edit/1,2,3]
```

---

## Important Notes

- **Quality over Quantity**: Better to record 2 high-quality insights than 10 trivial ones
- **User Control**: Always get confirmation before updating files
- **Transparency**: Show exactly what will be added to which file
- **Context-Independent**: Write for a future Claude instance that hasn't seen this conversation
