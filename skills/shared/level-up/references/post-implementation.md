# Post-Implementation Mode（口語：debrief）

目標是讓 user 在 merge/push 前理解關鍵決策，而不是背 diff。這個 mode 適合高風險改動，也適合 user 明確說想確認自己懂這次變更。

## 觸發規則

- Data model、architecture、user-facing behavior、guardrail/SSOT 改動：agent 必須主動提議 post-implementation quiz。
- Type/API contracts、permissions、migration、跨 agent workflow 改動：通常也應提議。
- user 可明確 skip；skip 要記錄在 final response、PR note、handoff report，或任務指定報告。
- typo、純格式化、機械小改不觸發。
- 不做 git hook；這是 workflow 規範，不是硬擋。

## 素材來源

- during implementation 的決策紀錄、plan deviations、conservative assumptions。
- `git diff` / PR diff、測試輸出、review findings。
- user 原本的 intent、pre-implementation plan、任何已確認 tradeoff。

## 報告排序

使用 decisions-first, mechanics-last：

1. Design decisions and tradeoffs.
2. Data model / migration / persistence changes.
3. Type/API interfaces and compatibility.
4. User-facing behavior and edge cases.
5. Risk, tests, and residual uncertainty.
6. Mechanical refactoring and file movement.

## Quiz 設計

- 沿用 `SKILL.md` 的 MCQ anti-tell 與 distractor 規則。
- 題目測「user 能否判斷改動是否合理」，不要測背誦哪幾個檔案改了。
- 2-4 題通常夠；高風險可加一題 tiny application check。
- 正確答案應要求理解 tradeoff，例如 compatibility、migration order、failure mode、rollback path。
- user 答錯時，回到相關決策脈絡重講，不要急著放行。

## 完成條件

- user 能用自己的話說出最重要的決策與風險，或答對 quiz。
- 若 user skip，清楚記錄 skip 與原因，然後依一般 review / push 規則繼續。
