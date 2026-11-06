---
name: tidy-workspace
description: "整理並同步 Git 工作區，但不結束 session。用在 $tidy-workspace，或使用者要清理、pull、同步、對齊 repo、worktree、stash、本機 commit 與遠端時。"
---

## 檢查

先找出這個 skill 的目錄，再跑 `scripts/inspect-workspace.sh [REPO_DIR ...]`，
帶上目前的 repo 和這個 session 碰過的每個 repo。它也會把 `~/dotfiles` 一起納入、
去掉重複的 Git root，並以非互動方式跑 `git fetch`；它絕不跑 pull、commit、push
或刪除。
`NEXT=` 只是建議，不是授權。非零的 exit code 就是 blocker。

## 動手

- `review-dirty`：看 staged 和 unstaged 的 diff；只測試、commit 範圍內的修改，
  然後重跑 script。
- `pull-ff-only`：跑 `git pull --ff-only`，然後重跑 script。
- `review-outgoing`：看完整的 outgoing 範圍和 diff，確認所有權和目的地，需要時
  再走 repo 的 PR 與 CI 流程 push。
- `stop:*`、敏感檔案、說不清的工作或所有權不明：停下來問。
- commit 或 push 前，檢查所有相關 diff 有沒有 secret、憑證、private key、
  未公開個資、本機機器細節。不知道 repo 是公開還是私有，就往保守的方向處理。
- 沒有明確授權，絕不 discard、reset、force-push、跑 `git clean`、刪 untracked
  檔案或丟 stash。
- 刪東西優先用可以救回來的 `trash` 指令，不用 `rm`；只有明顯可丟的暫存檔、build
  產物，或使用者明確要刪的東西才永久刪除。

## 收尾清理

自己建立的、或明確接手的 branch、worktree、PR，由建立者或目前的 controller 負責
清乾淨。只有目前的證據同時滿足下面每一項，才可以不問就刪掉一個確切的目標：

- 目標指得很精確，是自己的或明確在範圍內，而且沒有進行中的任務、process 或
  worktree 在用它；
- worktree 是乾淨的，不會弄丟任何 dirty、untracked、stash 住或還沒 push 的獨有
  資料；
- PR 已經 merge 或關閉，或那個產物已經用不到了；
- 有遠端、PR、已 merge 的 base，或其他驗證過的副本，足以在清理後把工作救回來；
- 做完確切的清理後，馬上讀回來確認目標狀態。

squash merge 的情況，光看 Git 的祖先關係不算證明。改用 PR head 的 OID、遠端副本、
patch 或 diff 內容一致，或其他簡單可靠的檢查。PR 已 merge 或關閉、worktree 乾淨且
全部 push 了，就是清理候選，但每一次刪除還是要有上面的證據；要刪遠端副本，還得
另有一份驗證過、救得回來的副本。一般的本機 branch 刪除只因為 squash merge 打斷了
祖先關係而失敗時，上面那套完整證據允許對確切目標跑 `git branch -D`；這是刪掉一個
驗證過多餘的 ref，不是改寫歷史。

下面這些情況，清理前先停下來問：worktree 是 dirty 的、資料只存在還沒 push 的
commit 或本機產物裡、還有進行中的任務或 agent 擁有或在用這個目標、所有權不清楚、
證據互相矛盾，或清理需要 force-push、改寫歷史、憑證、付費或存取權限的變更。目前的
任務還留著做收尾或回報，不算在用目標；本來安全的清理不要推到之後的 session。光是
放很久不算刪掉安全的證明。使用者和其他 agent 的產物不要碰，除非這個任務明確接管了
它們；所有無關的工作都留在原位。

## 回報

- 檢查過的 repo 和 branch；
- 做完的動作、測試和 CI；
- 做了哪些收尾清理，以及讀回來的證據；
- 保留下來的工作，或還需要做的決定。

如果本來就已經同步且乾淨，直接說。
