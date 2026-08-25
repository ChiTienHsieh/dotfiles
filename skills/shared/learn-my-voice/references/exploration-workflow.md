# Local exploration workflow

## Branch contract

預設 branch 名為 `explore/<topic-slug>`，從目前 `HEAD` 建立。

- 探索分支預設只留本機；公開前重新檢查完整 diff 與 commits，掃描不應公開的
  內容，並取得使用者確認。
- Checkpoint 只包含本輪明確範圍內的 Markdown 與專案 voice notes。
- 同一 worktree 出現任務外或來源不明的變更時，依 `tidy-workspace` 的
  `dirty-worktree-ownership.md` 處理；未確認的檔案或 diff 區塊不得納入 commit。

Explore branch 保存探索過程，不代表內容已定稿或獲使用者認可。

## Project voice notes

預設使用 `.explore/<topic-slug>/VOICE.md`；若 repo 已有同用途檔案，就沿用既有
SSOT。初始格式：

```markdown
# Voice notes

## Scope
- Base commit: `<sha>`
- Co-edited files: `<paths>`

## Confirmed choices
- 使用者明確說過，或具備足夠修改證據的寫法。

## Working hypotheses
- 從修改推測、仍需更多證據的偏好。

## Avoid
- 使用者已明確排斥的措辭、結構或語氣。

## Evidence
- `<commit>`：使用者把 A 改成 B，因此目前推測 C。
```

## Checkpoint loop

### Agent 動筆前

重新讀取目標內容與 diff。若範圍內已有適合進 Git 歷史的變更，只保存明確檔案
路徑：只有能確認由使用者完成時才用 `explore(user): <brief intent>`；來源不明或
混合時用 `explore(checkpoint): <brief intent>`，且不能拿來建立使用者偏好。

### Agent 修改後

重新讀取未暫存與已暫存的 diff，只把本輪已知修改保存成
`explore(agent): <brief intent>`。無法解釋的新變更留在原處，依共用 dirty-worktree
protocol 查明來源；不要把多輪 feedback 壓成一個無法追溯的大 commit。

### Voice inference

只有本輪出現新的可引用證據時才更新 `VOICE.md`，並以
`explore(voice): <learned choice>` 分開保存。若使用者直接修改 `VOICE.md`，先保存
其版本，並以使用者寫下的內容為準。
