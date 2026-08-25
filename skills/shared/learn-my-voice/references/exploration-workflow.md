# Local exploration workflow

只有要建立或繼續 project explore branch、保存 checkpoints、判斷 authorship 時讀
這份 reference。

## Branch contract

預設 branch 名為 `explore/<topic-slug>`。建立前檢查完整 refs；若已存在名為
`explore` 的 branch，造成階層名稱衝突，改用 `explore-<topic-slug>`，不要刪除或
改名既有 ref。

- 從目前 `HEAD` 建立 branch，保留 working tree 現況。
- `git switch -c` 失敗時，不得用 `reset`、`stash`、discard 或覆寫硬闖。
- Branch 不設 upstream，永遠視為 local-only。
- 未經明確要求，不得 push、merge、rebase、開 PR 或刪 branch。
- 只 stage allowlisted Markdown 與 project voice-notes file；禁止 `git add -A`、
  `git add .` 或 `git commit -a`。
- 不修改 Git author、不 amend 或重寫既有 commits。

Explore branch 保存探索過程，不代表內容已定稿或獲使用者認可。

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
3. 精準 stage 那些 paths。
4. 以 `explore(checkpoint): <brief intent>` commit。

只有能從目前 fresh evidence 確定變更由使用者完成時，才用
`explore(user): <brief intent>`。來源不明、混合或可能仍在編輯中的變更一律用
中性 `checkpoint`，也不能拿來建立使用者偏好結論。

### 保存 agent revision

交付前重新讀 status 與 diff。若只包含本輪 agent 的已知修改，精準 stage 並以
`explore(agent): <brief intent>` commit。

若出現 agent 無法解釋的新變更：

- 不把它標成 agent commit。
- 不為了乾淨 commit 還原它。
- 改做中性 checkpoint；若 authorship 會影響學習判斷，停下詢問。

每個 commit 應是可閱讀的小單位，不是每次 keystroke 一個 commit，也不要把多輪
feedback 壓成單一大 commit。

### 保存 project voice inference

只有本輪出現新的可引用 evidence 時才更新。以獨立的
`explore(voice): <learned choice>` commit 保存，讓寫作內容與 agent inference 可
分開檢查。若使用者直接修改 `VOICE.md`，先依相同規則保存其版本，並以使用者
寫下的內容為準。
