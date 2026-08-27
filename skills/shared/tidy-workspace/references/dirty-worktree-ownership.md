# Dirty Worktree 變更歸屬流程

只有共用同一個實體 worktree 時，才使用這套流程：其中出現不屬於目前任務、
且負責者不明的已暫存、未暫存或未追蹤變更。已確認屬於目前任務或使用者的變更，
仍走一般的 `review-dirty` 流程。

## 1. 凍結 worktree

- 不要暫存變更、建立 commit、執行 `stash`、`restore`、`reset` 或 `clean`、
  切換 branch，或編輯該 worktree 中的任何檔案。
- 記錄精確的 Git root、實體 worktree 路徑、branch、正在進行的 Git 操作，
  以及已暫存、未暫存與未追蹤的 path。
- 間接的 Git 中繼資料與過期快照只能當線索，不能當成歸屬證據。仍可執行不會
  修改 worktree 的 `git fetch`。

## 2. 委派一個範圍明確的調查者

Codex App 的 subagent 與 task tools 都可用時，委派一個唯讀 subagent 調查。
委派指令必須包含：

- 發起方 task/thread 的精確回覆目標；
- 唯讀權限，以及精確的 repo、worktree、branch 與 dirty paths；
- 只能使用 App 原生 task tools，不得改讀 App 原始資料庫或使用 tmux 替代方案；
- 不得修改檔案、Git index、branch 或 history，也不得 archive、handoff、rename
  或關閉 task，且不得廣播；
- 重新讀取收件 task 的最新內容後，最多只能傳送一則精準的協調訊息；
- 必須把證據與仍無法確認的部分回報給發起方。

只要其中一項能力不可用，就保留現況並詢問使用者，不要猜測。主 agent 不得默默
改用證據力更弱的方式判定歸屬。

## 3. 找出並證明負責的 task

調查者只能使用 Codex App 原生 task tools：

1. 列出近期仍活躍的 task，縮小候選範圍。
2. 讀取每個候選 task 的最新完整內容，不能只看 title 或 preview。
3. 為每個 dirty path 建立歸屬表；同一檔案混有多方修改時，細分到目前的個別
   hunk（變更區塊）。每個確認範圍都必須有直接證據，同時對得上實體 worktree
   與目前 diff；只有工作意圖、相同 repo 或相同 branch 都不夠。
4. 把每個 path 或 hunk 標成 `confirmed:<task>` 或 `unconfirmed`，並引用或摘要
   證據。不能只因另一個 Codex task 存在，就把使用者的變更歸給 Codex。

只聯絡與已確認範圍有直接關聯的 task。所有未確認或混雜的範圍都回報給發起方，
並維持原狀。

## 4. 與已確認的 task 協調隔離

傳訊前，依全域規則重新讀取該收件 task 的最新內容。讀取失敗、task 狀態已有
實質變化，或證據不再吻合時，都不要傳送。

只傳送一則精準訊息，內容包含：

- 發起方的回覆目標，以及調查者的唯讀協調角色；
- 只列出精確確認的 paths 或 hunks，並把未解決範圍分開；
- 請收件方確認歸屬與目前是否安全；
- 硬邊界：不得做破壞性清理、不得修改已證明歸屬範圍以外的內容，也不得在沒有
  重新執行 Git 檢查的情況下宣稱 worktree 已乾淨。

第一則訊息只用來確認歸屬與目前是否安全，不能授予新的修改權限。調查者必須從
收件 task 的最新內容中，找到使用者直接指令逐項授權以下操作：建立可移轉的工作
保存點（checkpoint）、移至獨立 worktree，以及在該處繼續修改。收件 agent 自己的
聲明或其他委派指令都不能代替使用者授權。缺少任何一項時，就回到發起方請
使用者決定。

不得假設或自行搬移正在執行的 task。只有使用者直接指令明確授權，而且當下工具
允許時，負責的 task 才能建立安全且可移轉的 checkpoint、改到獨立
worktree 繼續，並在不碰未確認範圍的前提下驗證兩邊狀態。

## 5. 驗證結果

- 重新讀取負責 task 的最新回覆；callback（回傳通知）只代表喚醒，不能證明
  清理已完成。
- 在同一個實體 worktree 重新執行 `scripts/inspect-workspace.sh`，包括重新執行
  `git status`。
- 只有先前的 dirty paths 都已釐清，且目前任務預計操作的範圍乾淨時，才能繼續。
  否則保留現況並回報阻擋原因。

最後回報已確認的負責者、採用的證據、訊息傳送目標、協調結果、最新 Git 狀態，
以及所有未解決事項。不要暴露無關 task 的內容。
