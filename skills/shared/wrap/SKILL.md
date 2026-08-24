---
name: "wrap"
description: "結束目前 session。當使用者呼叫 $wrap，或要求 wrap up、完成目前工作、收尾並交付時使用：完成未竟工作、更新必要文件、清理外部 agent target、交由 $tidy-workspace 整理 Git，並用精簡 zh-TW 收尾。"
---

1. 檢查對話與 task 狀態，找出使用者已要求但尚未完成的工作。完成安全且在 scope 內的項目；只回報真正的 blocker。
2. 若本 session 改變了 setup、指令、架構或行為，更新必要的 user-facing docs。
3. 在宣告本 session 可封存前，盤點本 session 建立且擁有的精確 external-agent targets，以及使用者明確納入 cleanup scope 的其他精確 targets。緊鄰處理前 fresh-read 每個 target 的執行狀態與最新輸出；idle、標題或舊 snapshot 都不是 completion evidence。只關閉已有可接受 completion evidence 且不再需要的 target，並遵守該 surface 的授權與 cleanup SSOT；關閉後確認該精確 target 已不存在。若 cleanup 未獲授權或無法執行，或 target 屬於使用者、原本就存在、仍在執行或被刻意保留，則保留並回報原因。
4. 完整讀取 `../tidy-workspace/SKILL.md`，並依其規則整理本 session 觸及的每個 repo。`~/dotfiles` 存在時也要檢查，因為經由 home-directory symlink 的修改可能不會被 dirty-worktree tracker 發現；該 skill 是 Git workflow 的 SSOT。
5. 本 skill 由其他 skill 呼叫時必須明示 mode；mode 只存在於當前呼叫鏈。只有使用者直接呼叫 `wrap` 時才沒有 mode；其他無 mode 呼叫一律停止並回報 blocker：
   - `archive-check-only`：回傳以上檢查的完成證據給呼叫端，不得呼叫 `name-task`。
   - 使用者直接呼叫：若以上檢查確認沒有未完成責任或阻止封存的 blocker，且目前 surface 同時提供 `name-task` skill 與 task title capability，完整讀取 `~/dotfiles/skills/codex/name-task/SKILL.md`，並以 `rename-only` mode 執行一次，把目前 task 標為 `📦`；此 mode 不得呼叫 `wrap`。
6. 用精簡 zh-TW 摘要已完成、驗證、commit 與 push 的內容，以及仍待決定的事項或 blocker。

若使用者只要 Git cleanup 或 remote synchronization，直接使用 `$tidy-workspace`。保持 dependency 單向：`$wrap` 可以呼叫 `$tidy-workspace`；`$tidy-workspace` 不得呼叫 `$wrap`。
