# Implementation Understanding Loop

這是 `level-up` 的 implementation mode 總覽。它把任務切成 pre / during / post 三段，用來暴露 unknowns、保留決策脈絡、確認 user 在 merge/push 前真的理解關鍵改動。

## 何時觸發

- user 要求逐關理解實作、preflight、debrief 或 merge-readiness quiz，或接受 agent 的教學提議。
- 陌生技術、介面或架構的重大取捨可作為提議教學的理由；單純改到這些檔案、要求一般 plan 或 review，不自動啟動課程。
- 教學提議不阻擋已授權的實作、review 或 push；只有 user 明確要求理解驗收時，才把課程完成設為該任務的門檻。

## 何時不要

- typo、純格式化、機械 rename、低風險小 patch。
- user 已明確要求只做狹窄修補，且沒有架構或使用者可見決策。
- 已有清楚 spec、diff 很小、review 不需要額外理解材料。

## 共同原則

- **Decisions-first, mechanics-last**：先放 user 最可能想改或想審的決策，機械性重構沉底。
- Pre 示例：`Write an implementation plan, but lead with the decisions most likely to change: data model, type/API contracts, and user-facing behavior.`
- Post 示例：`Write a post-implementation note, but lead with design choices, data model, interfaces, and user-facing behavior; bury mechanical refactoring at the bottom.`
- HTML 是可選輸出，不是預設義務；只有 user 明確要求或內容真的需要視覺結構時才用。

## 三段如何串起來

- **Pre**：把 unknown unknowns 變成可決策的 known unknowns，產出 decisions-first implementation plan。
- **During**：如果偏離 plan、做保守假設、或遇到會影響 review 的決策，記在既有 PR body / report / handoff note；長任務或多 agent 接力才開獨立 notes。
- **Post**：用 during 的決策紀錄加上 diff 當素材，產出 decisions-first 理解報告與 quiz。

## Mode Boundaries

`SKILL.md` 的 Reference Router 直接選擇各 mode；本檔不再路由其他
reference。口語觸發詞：**preflight** ＝ pre-implementation，**debrief** ＝
post-implementation。During notes 是一般 implementation 行為，不是純教學；
只在需要形成 post quiz 素材時拉進來。
