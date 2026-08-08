---
name: name-task
description: 更新 Codex task 標題。當使用者要求 name／rename task、AGENTS.md 指示在 final answer 前檢查重要狀態，或 Chief of Staff／scheduled cleanup 要整理標題時使用。
---

只有標題能幫助使用者看出下一步行動或應理解內容時才更新。

## 流程

1. 讀取 task 最新狀態。若要替其他 task 改名，必須緊鄰改名前 fresh-read 該 task。
2. 先辨識 **stable scope**：使用者會用來認出這段對話的 repo、project 或 topic。既有標題的第一段仍準確時就保留，不因單次工具動作、暫時工作位置或 delegated work 改寫；沒有可靠舊標題時，才從目前主要 user topic 推導。使用者導向的換題，或舊 scope 已不再是主要工作時，優先更新 scope。
3. 依使用者下一步分類：
   - `⏸️`：缺資料、權限、CI、部署或其他前置條件，需要使用者協助。
   - `⏳`：只等使用者做簡單選擇。
   - `🔎`：使用者需要理解重要背景或取捨。
   - `📦`：沒有未完成責任或重要學習，值得封存。
4. 若 agent 應繼續工作且使用者無須行動，不改名。Stop、idle、final answer 或只有本機 commit，都不足以標 `📦`。
5. 寫成以下精確格式：

   ```text
   <一個狀態 emoji> <stable repo／project／topic> | <目前主要目的> | <user-facing 進度／下一步>
   ```

   Delegation 或工具工作只有在影響使用者理解或下一步時才放第三段。只能有一行及兩個半形 ` | ` 分隔符。目標 24–32 字，最多 40 字；進度語意必須符合狀態 emoji。

6. 若有 `codex_app__set_thread_title` 等 title tool，只呼叫一次。目前 task 省略 `threadId`；經授權替其他 task 改名時，使用步驟 1 取得的精確 ID 與 host。
7. 若沒有 title tool，回傳完整建議標題，請 CLI 使用者用 `/rename` 套用。不得重建舊 Stop hook、shell、app-server 或暫存檔 fallback。

不得 archive、unarchive、delete 或變更其他 task lifecycle state。`📦` 只代表建議使用者之後封存。

只在使用者單獨要求改名時簡短確認；作為其他工作的正常收尾時不另行報告。
