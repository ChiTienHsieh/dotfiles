---
name: "file-review-loop"
description: "Run the `file-review-loop` workflow when a task needs iterative Builder/Reviewer passes with file-backed review reports; also use for the legacy `iterate-worker-reviewer` workflow."
---

# file-review-loop

當使用者要求 `file-review-loop`、`iterate-worker-reviewer`、迭代式 Builder/Reviewer pass，或需要 high-bar review loop 並希望把大量 review 內容透過檔案交接時，使用這個 skill。

## Purpose

執行一個把 heavy context 留在檔案裡的品質迭代 loop：

```text
Builder -> fresh Reviewer -> review report file -> Builder fixes from file -> repeat
```

Reviewer 每一輪都必須先從 fresh point of view 開始；只有在 fresh review 已寫入本輪 report 之後，才可以讀上一輪 report 並 audit 舊問題。這可以避免下一輪 review 變成狹窄的 checklist，漏掉 Builder 新引進的問題。

## Defaults

- Max iterations: 5 rounds。
- Pass condition: Reviewer 寫出 `Verdict: PASS`，且 blocking issues 為空。
- Report location: 預設使用 repo 外的 system temp directory；除非使用者要求保留 audit trail，才放進 repo。
- Report format: structured Markdown。
- Agent policy: 每一輪都使用 fresh Reviewer subagent。

## Setup

1. 只有在原始任務不可執行時才向使用者釐清。
2. 建立 temp working directory 放 loop artifacts，例如：
   - `file-review-loop-<short-task>-<timestamp>/`
   - `round-01-review.md`
   - `round-02-review.md`
   - `latest-review.md`
3. 原始任務摘要要短且穩定；詳細 feedback 的 source of truth 是 report file。
4. 如果有 task plan tool，就用它追蹤每一輪狀態。

## Round 1

### Builder Pass

請 Builder 實作使用者要求的任務。Prompt 要包含：

- 原始 user request。
- Scope 內的 files 或 subsystem。
- Expected deliverables。
- Validation expectations。
- 提醒 Builder：codebase 可能有其他 agent 或使用者變更，不可 revert unrelated changes。

### Reviewer Pass

Spawn 一個 fresh Reviewer。Reviewer 必須依序執行兩個 phase。

Phase 1: fresh review

- 只讀原始任務、acceptance criteria、目前成果。
- 這個 phase 不可以讀任何 previous review report。
- 從 fresh point of view 嚴格 review。
- 檢查 missing requirements、correctness bugs、regressions、tests、maintainability risks、user-facing issues。
- 把 fresh review 寫入本輪 report。

Phase 2: previous issue audit

- Round 1 沒有 previous report；寫 `No previous report`。
- 後續 rounds 必須等 Phase 1 寫完後，才讀上一輪 report。
- 對上一輪每個 blocking issue 標記 `fixed`、`partial`、`unresolved`、`regressed`、或 `obsolete`。
- 在任一 phase 發現的新問題，都要列為 current-round issues。

## Later Rounds

如果 latest report 是 `Verdict: NEEDS_WORK`，或仍有任何 blocking issue：

1. Spawn 一個 Builder。
2. 只給 Builder：
   - original task summary，
   - 目前 scope 內的 repo/files，
   - `latest-review.md` 的路徑，
   - 直接讀 report file 的指示。
3. 不要把完整 review report 貼進 prompt。
4. 要求 Builder 先修 blocking issues，再處理低風險的 non-blocking issues。
5. Spawn 新的 fresh Reviewer，重複 two-phase review。

當 Reviewer 通過，或達到 max iterations 時停止。

## Review Report Template

每一輪 review report 必須使用這個結構：

```markdown
# Round NN Review

## Verdict
NEEDS_WORK

## Blocking Issues
- [RNN-B1] Title
  - Evidence:
  - Impact:
  - Required fix:

## Non-blocking Issues
- [RNN-N1] Title
  - Evidence:
  - Suggested fix:

## Fresh POV Notes
- What the Reviewer noticed before reading any previous report.

## Previous Issue Audit
- Previous report: /absolute/path/to/round-NN-review.md
- [R01-B1] fixed | partial | unresolved | regressed | obsolete
  - Evidence:

## Builder Instructions
- Ordered fix instructions for the next Builder.
- Include file paths and commands to run when useful.
- Keep this section self-contained enough for the Builder to act after reading the file.

## Acceptance Checklist
- [ ] No blocking issues remain.
- [ ] Original task requirements are satisfied.
- [ ] Relevant tests/checks pass or documented why they could not run.
```

如果成果通過，使用：

```markdown
## Verdict
PASS

## Blocking Issues
None.
```

## Issue IDs

- Blocking issue IDs 使用 `R<round>-B<number>`，例如 `R2-B1`。
- Non-blocking issue IDs 使用 `R<round>-N<number>`。
- Audit previous issues 時，不要重新命名舊 issue IDs。
- 如果 previous issue 已修好但造成新問題，將 previous issue 標為 `fixed` 或 `partial`，再開一個 current-round blocking issue。

## Reviewer Prompt Requirements

Reviewer prompt 必須明確寫出：

- 從 fresh point of view 開始。
- Fresh review 寫完前，不可讀 previous review report。
- 嚴格 review；通過條件是沒有 blocking issues。
- 將完整 review 寫到指定 file path。
- Final chat output 保持簡短，指向 report file。

## Builder Prompt Requirements

Builder prompt 必須明確寫出：

- 從指定路徑讀取 latest review report。
- 不要依賴 chat prompt 取得詳細 feedback。
- 先修 blocking issues，再做 polish。
- 保留 unrelated user changes。
- 回報 changed files 與 validation results。

## Completion Report

Loop 結束時，回報：

- Final verdict。
- Number of rounds。
- Latest review report path。
- Files changed。
- Validation performed。
- 如果因 max iterations 停止，列出 remaining issues。

除非 latest report 有 `PASS` 且沒有 blocking issues，否則不要宣稱成功。
