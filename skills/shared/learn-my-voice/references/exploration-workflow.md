# Local exploration workflow

只有要建立或繼續 project explore branch、保存 checkpoints、判斷 content
provenance 時讀
這份 reference。

## Branch contract

預設 branch 名為 `explore/<topic-slug>`。建立前檢查完整 refs；若已存在名為
`explore` 的 branch，造成階層名稱衝突，改用 `explore-<topic-slug>`，不要刪除或
改名既有 ref。

- 從目前 `HEAD` 建立 branch，保留 working tree 現況。
- `git switch -c` 失敗時，不得用 `reset`、`stash`、discard 或覆寫硬闖。
- Branch 不設 upstream，並依 local-only policy 管理；這不是防止 `git push --all`、
  explicit push 或 GUI publish 的技術保證。
- 未經明確要求，不得 push、merge、rebase、開 PR 或刪 branch。
- 只 stage allowlisted Markdown 與 project voice-notes file；禁止 `git add -A`、
  `git add .` 或 `git commit -a`。
- 每次 commit 前先讀 `git diff --cached --name-only`。既有 index entries 不得被
  checkpoint 消費或清除。
- 不修改 Git author、不 amend 或重寫既有 commits。

Explore branch 保存探索過程，不代表內容已定稿或獲使用者認可。

任何 push 前都要 fresh-read exact branch 相對 base 的完整 diff／commits，重掃
secrets 與不應公開的 voice data，再取得針對該 branch 與內容範圍的明確確認。
既有通用 push 授權不能代替。刪 branch 也不會立即清除 Git object database；若
內容本來就不該進 object database，必須在 checkpoint 前停止。

## Project voice notes

預設建立 `.explore/<topic-slug>/VOICE.md` 並加入 allowlist。若 repo 已有同用途的
local voice file，沿用既有 SSOT。初始格式：

```markdown
# Voice notes

Local-only working notes. Do not push or merge without explicit approval.

## Scope
- Base commit: `<sha>`
- Co-edited files: `<paths>`

## Confirmed choices
- 使用者明確說過，或具備足夠 revision evidence 的寫法。

## Working hypotheses
- 從 edits 推測、仍需更多 evidence 的偏好。

## Avoid
- 使用者已明確排斥的措辭、結構或語氣。

## Evidence
- `<commit>`：使用者把 A 改成 B，因此目前推測 C。
```

## Checkpoint loop

### 保存 agent 動筆前的版本

只要 target files 已有變更：

1. 重新讀完整相關段落與 diff。
2. 確認變更都在 allowlist，且適合進 Git history。
3. 檢查既有 staged state，再精準 stage 那些 paths。
4. 以 `explore(checkpoint): <brief intent>` commit。若 index 原本已有其他 staged
   paths，plain `git commit` 不安全；只有在 current file content 就是完整 checkpoint
   且同一路徑沒有需保留的 partial staging 時，才可用
   `git commit --only -- <exact allowlisted paths>`，並在 commit 後確認其他 cached
   diff 未改變。無法證明時停止，不得 stash、unstage 或還原任何既有 index state；
   它可能屬於使用者或同一 worktree 的另一個 agent。

`explore(user)`、`explore(agent)` 與 `explore(checkpoint)` 只描述 content
provenance，不代表 Git `Author`／`Committer` identity；repo 原有 Git identity 保持
不變。

只有能從目前 fresh evidence 確定變更由使用者完成時，才用
`explore(user): <brief intent>`。來源不明、混合或可能仍在編輯中的變更一律用
中性 `checkpoint`，也不能拿來建立使用者偏好結論。

### 保存 agent revision

交付前重新讀 status、working diff 與 cached diff。若只包含本輪 agent 的已知修改，
依上方既有 staged-state 規則，以 `explore(agent): <brief intent>` commit。

若出現 agent 無法解釋的新變更：

- 不把它標成 agent commit。
- 不為了乾淨 commit 還原它。
- 改做中性 checkpoint；若 content provenance 會影響學習判斷，停下詢問。

每個 commit 應是可閱讀的小單位，不是每次 keystroke 一個 commit，也不要把多輪
feedback 壓成單一大 commit。

### 保存 project voice inference

只有本輪出現新的可引用 evidence 時才更新。以獨立的
`explore(voice): <learned choice>` commit 保存，讓寫作內容與 agent inference 可
分開檢查。若使用者直接修改 `VOICE.md`，先依相同規則保存其版本，並以使用者
寫下的內容為準。
