---
name: name-task
description: 更新 Codex task 標題。當使用者要求 name／rename task、AGENTS.md 指示在 final answer 前檢查重要狀態，或 Chief of Staff／scheduled cleanup 要整理標題時使用。
---

只有標題能幫助使用者看出下一步行動或應理解內容時才更新。

## 流程

1. 讀取 task 最新狀態。若要替其他 task 改名，必須緊鄰改名前 fresh-read 該 task。
2. 若準備把目前 task 標為 `📦`，且本 turn 尚未完成 `wrap`，先讀取並執行
   `../../shared/wrap/SKILL.md` 的封存前檢查；正在執行或本 turn 已完成
   `wrap` 時不得再次呼叫。替其他 task 改名時，不得以目前 session 的
   `wrap` 代替；只有 fresh-read 顯示該 task 已完成等價的封存前檢查，才可
   使用 `📦`。
3. 依使用者下一步分類：
   - `🚨`：使用者明確指定要親自持續追蹤的關鍵或高槓桿 task；標記與 pin 必須同步，且只由使用者明示新增或解除。
   - `⏳`：task 尚未完成，下一步需要使用者注意或行動。
   - `📦`：沒有未完成責任或重要學習，值得封存。
4. 若 agent 應繼續工作且使用者無須行動，不改名。Stop、idle、final answer 或只有本機 commit，都不足以標 `📦`。
5. 寫成以下精確格式：

   ```text
   <一個分類 emoji> <repo／project／最小可辨識範圍> | <使用者目的> | <進度>
   ```

   只能有一行及兩個半形 ` | ` 分隔符。目標 24–32 字，最多 40 字；最後一欄必須反映目前進度。

6. 各自使用可用的 title、pin 或 unpin tool；每項只呼叫一次。目前 task 省略 `threadId`；經授權替其他 task 操作時，使用步驟 1 取得的精確 ID 與 host。
7. 缺少哪項 capability，就明講該項仍需手動完成；缺 title tool 時附完整建議標題。不得重建舊 Stop hook、shell、app-server 或暫存檔 fallback。

除了使用者明示的 `🚨` pin／unpin，不得 archive、unarchive、delete 或變更其他 task lifecycle state。`📦` 只代表建議使用者之後封存。

只在使用者單獨要求改名時簡短確認；作為其他工作的正常收尾時不另行報告。
