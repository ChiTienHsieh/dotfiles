---
allowed-tools: [Task, TodoWrite, Read, Glob, Grep]
argument-hint: "[task description] [target quality: 8|9|10]"
---

# Worker-Reviewer-Iteration Pattern

Execute a quality-driven iteration loop using Opus subagents.

## Pattern Overview

```
Worker (do task) → Reviewer (score & critique) → [if score < target] → Worker' (fix issues) → ...
```

## How to Use

### Arguments
- `$ARGUMENTS` will contain: `[task description] [target quality score]`
- Example: `/iterate-worker-reviewer "scrape and document the API" 10`

### If No Arguments Provided
Ask user:
1. What task should the Worker do?
2. What's the target quality score? (default: 9)

## Execution Steps

### Step 1: Initialize Todo List

```
TodoWrite:
- [ ] Worker Round 1: [task]
- [ ] Reviewer Round 1: Score & critique
- [ ] (pending iterations as needed)
```

### Step 2: Spawn Worker

Use Task tool with `subagent_type: opus-specialist`:

```
Prompt the Worker with:
- Clear task description
- Expected output format
- Output file path(s)
- Quality expectations
```

### Step 3: Spawn Reviewer

Use Task tool with `subagent_type: opus-specialist`:

```
Prompt the Reviewer with:
- Files to review
- Checklist of quality criteria
- Score format: X/10
- Specific feedback for improvements
- Output: review_report.md or similar
```

### Step 4: Iterate If Needed

If Reviewer score < target:
1. Update todo list
2. Spawn new Worker with:
   - Original task context
   - Reviewer's specific feedback
   - Items to fix
3. Spawn Reviewer again
4. Repeat until target reached

### Step 5: Report Completion

```
Final Summary:
| Round | Worker Action | Reviewer Score |
|-------|---------------|----------------|
| 1     | Initial work  | X/10           |
| 2     | Fixed A, B    | Y/10           |
| ...   | ...           | target/10 ✓    |
```

## Tips for Good Results

### Worker Prompts Should Include:
- Concrete deliverables (file paths)
- Format requirements
- Context from previous rounds (if iterating)

### Reviewer Prompts Should Include:
- Clear scoring rubric
- "Be strict" instruction
- Specific items to check
- Request for actionable feedback (not vague)

### Common Quality Criteria:
- Completeness (nothing missing)
- Accuracy (correct information)
- Format (proper structure, no placeholders)
- Polish (no typos, consistent style)

## Example Invocation

User: `/iterate-worker-reviewer "document the codebase architecture" 10`

CC Response:
1. Create todo list
2. Spawn Worker to analyze and document architecture
3. Spawn Reviewer to check completeness, accuracy
4. If < 10, iterate with specific fixes
5. Report final result

---

**Note**: This pattern is token-intensive but produces high-quality results. Use for important deliverables where quality matters.
