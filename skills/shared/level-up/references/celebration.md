# 盛大收尾

只在**最後一關通關**時讀。中途停課、休息、下次再繼續，都不走這份，一個 kaomoji 就好。

目標：盛大到有點荒謬，但讓學習者覺得好玩。一個顏文字帶過不算收尾。兩段都要做，順序固定。`learning-records.md` 的靜默記帳照舊，慶祝不影響記帳。

## 第一段：當場畫 ASCII art

在聊天裡自己畫，不委派：

- 至少 8 行。獎盃、煙火、通關橫幅都可以，主題要跟這門課有關：SSH 課畫一把鑰匙或一條水管，git 課畫一棵分支樹，資料庫課畫一疊抽屜。
- 放在 code block 裡，終端機才不會跑版。
- 下面用一到兩句話總結學習者**展示了什麼**（不是「教了什麼」）：哪些關一次過、哪些關逆轉、他現在能自己做到什麼。

```text
        .-----.
       /  ___  \        ┌──────────────────────────┐
      |  /   \  |       │  SSH 十關全通  (⌐■_■)    │
      |  \___/  |       └──────────────────────────┘
       \_______/
          | |
          | |__
          |____|
          | |
          |_|
```

## 第二段：委派一份浮誇通關頁

走 `skills/shared/delegate` 的流程，控制端只寫 spec，不自己刻 HTML。

1. 跑 `~/.claude/skills/delegate/scripts/pick-worker` 挑目前配額最多的 coding agent（從 Claude Code 跑要 `dangerouslyDisableSandbox: true`）。推薦的是自己的 runtime 就用內建 subagent。
2. 把 spec 寫進 `$TMPDIR` 下的檔案，傳絕對路徑（沙盒內外的 `$TMPDIR` 不同，給 worker 的一律用絕對路徑）；遵守 delegate 的六段契約：objective、files in scope、interfaces、constraints、verification、reasoning effort。
3. 收到檔案後控制端自己驗收（下一節），再把絕對路徑給學習者。

### spec 最低要求

照 `skills/shared/html-artifacts` 的規矩產出（它的「先問要不要 HTML」在這頁不適用，學習者在 skill 層已經要了），另加下面每一條：

- 單一 `.html` 檔，CSS 與 JS 全部 inline，不用外部字型、CDN、圖片。
- 開頁有動畫：煙火、彩帶、跑馬燈任選，不能是靜態頁。
- 放學習者在 Level 0 說的目標。
- 列出十關（或實際關數）的名稱，用意思命名，照課程順序。
- 答錯又答對的關特別標「逆轉」，視覺上要跟一次過的關明顯不同。
- 最後一句是這門課的 one-liner：一句話講完這門課教的核心。
- 浮誇是要求，不是選項：字要大、顏色要多、要有一點蠢。html-artifacts 裡「避免 hero、避免裝飾」那幾條在這頁不適用，spec 裡要明講。
- 輸出路徑寫死在 spec 裡，用 worker 寫得到的地方：`$TMPDIR` 的絕對路徑或 worker 的 workspace；不進追蹤檔。控制端驗收後可再搬到 `~/scratch/`。
- 這是 taste work，依 delegate 的模型原則用最強的模型，不用預設的小模型。

### 驗收

控制端自己做，worker 說「做好了」不算：

1. 在瀏覽器打開檔案（`open` 加絕對路徑）。
2. 用 grep 找 `https?://`，確認沒有外部資源。
3. 確認動畫會跑、目標與關卡名都在、逆轉關有標、one-liner 在最後。
4. 缺什麼就帶具體回饋再派一次，最多兩次。

## 委派失敗的備案

worker 沒交出東西、交出空 diff，或兩次修正後仍不合格：控制端自己畫一個簡單版的單一 HTML（一段 CSS 動畫、大字目標、關卡清單、one-liner）就好。課程收尾不能因為委派失敗而沒有慶祝。

## 給學習者的最後一則訊息

依序：ASCII art、展示了什麼的一兩句、通關頁的絕對路徑、可執行的下一步一句。不提記帳，不提委派過程。
