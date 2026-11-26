# 委派教訓

`tmux-orchestration` skill 的事故教訓，每條標日期。長期有效的委派規則放在 SKILL.md（委派合約），不要在這裡重講。只開相關的段落；新教訓提煉成標了日期、可重用的規則，不貼原始 log。

## tmux 操作

從 controller 操作 tmux pane 裡的互動式 agent 時看這段。

- `workspace-sprin` 刻意沒有 tmux socket 的存取權；每個 tmux 指令都要走 Guardian 的自動審核。
- 用 `codex --sandbox workspace-write` 啟動 worker。worker 只讀另一個 repo、但要寫報告時，cwd 設成可寫的暫存目錄（例如 `/tmp` 底下）；worker 要改目標 repo 時，cwd 設成那個 repo。
- 對 agent pane `send-keys` 之前先 capture，確認它沒有停在 AskUserQuestion 或審核 UI 這類互動對話框上。文字加 Enter 送進那個對話框，會替使用者選掉一個選項（2026-07-04）。等使用者回應的對話框只能由使用者操作。
- Claude Code 的 ghost text（2026-09-29）：閒置時，Claude Code 可能在 `❯` 後面空的輸入框裡顯示一句建議的下一個 prompt。單純 `capture-pane -p` 會丟掉樣式，建議看起來就跟使用者打了還沒送出的文字一模一樣。把它當成使用者的草稿（或 worker 的下一個指示）之前，先跑 `tmux capture-pane -p -e -t PANE | grep -F '<substring>' | cat -v`，substring 從第二個字元開始取：escape code 緊接在第一個字元後面，grep 整句永遠對不上。建議是暗色的：第一個字元是反白（游標），後面接 `^[[0;2m`，例如 `^[[7mR^[[0;2mead .dedup-orch/...`。暗色代表輸入框其實是空的，可以放心用 `agent-send-prompt.sh` 送。不要按一個光禿禿的 Enter 想「清掉」它。文字不是暗色，就是真的還沒送出的草稿：不要蓋掉，問使用者。
- 共用工作樹的 commit 互斥（2026-07-04）：另一個 controller 也在改同一個 working tree 時，commit 前先通知它、等到 ACK；不然一邊 stage 的檔案會跑到另一邊的 commit message 底下。
- Claude worker 的 cwd 要設成它要操作的 worktree。worker 的指令都是 `cd <other-dir> && git ...` 的話，永遠對不上它 `Bash(git ...)` allowlist 的前綴，每一步都要人工審核（2026-07-06）。
- 偏驗證的任務，allowedTools 要先把驗證會用到的工具放進去：`gh run *`、`gh api *`、`curl *`、preview server 和截圖工具；不然 worker 剛好在驗證那步卡在審核上。

失敗模式：

- `/quit` 之後要等一下才能下一個啟動指令；重啟前先 sleep。
- Codex 第一次在新目錄啟動會跳目錄信任提示；答 1。
- pane 停在審核對話框上時 `agent-send-prompt.sh` 會失敗（輸入被吃掉）：先清掉對話框再送。

## hook 與 merge commit

worker 的 commit 被 pre-commit／pre-push hook 擋住時看這段。

- 逐檔檢查、不認得 merge 的 hook，會把 merge 從 main 帶進來、內容沒變的檔案再標一次（它們在自己的 PR 已經過了 CI）。這是誤判，不是違規；但要修還是需要授權。
- 絕不 `--no-verify` 或任何等效做法（蓋掉 hooksPath、動環境變數）。沒有 hook 擋這件事（2026-07-06）；這是一條長期的 prompt 層規則，規則技術上沒被強制，不等於可以做。
- 處理順序：(1) 向使用者提長期的修法：把 hook 改成認得 merge，或 commit 一條永久的 ignore 項目（這是 repo／機器的政策，由使用者決定）；(2) 只有使用者已經明確授權了「結果」（例如「兩個都 merge」），而且 hook 是使用者自己機器層的檢查對沒變的檔案誤判時，才可以暫時改磁碟上檢查器自己的 ignore 設定，但要在任務報告裡寫得一清二楚、不進 commit（前面用 `git status --short -- <file>`、後面用 `git show HEAD --stat` 確認），再用 `git restore` 還原（不是 `rm`，那個檔有被追蹤），並跟 HEAD 比 diff 確認每個 byte 都一樣。沒講或沒寫下來 = bypass。拿不準就問。

## worker prompt

替被委派的 worker 寫 prompt 檔時看這段。（合約欄位、固定名詞、副作用邊界：見 SKILL.md「委派合約」。）

- 省 token 的委派，就是不讀 worker 的輸出串流（2026-07-02）：省下來的是靠輪詢 marker／報告，不是靠選互動式還是 exec 的 surface。
- 先找最便宜的事實來源：簽下任何「重現／複製／比對 X」的任務之前，先花一次唯讀檢查找 X 的直接來源（`*.github.io` 頁面背後的公開 repo、套件、匯出檔）。來源直接拿得到卻從畫面輸出重現，整趟 worker 都白跑。
- 繼承來的紅燈：worker 合約要寫「合約範圍外的 CI 失敗 = 回報，不修」；不然每個平行的 worker 都各自修同一個繼承來的失敗，同一個修法進去 N 次。

## 驗證

worker 回報做完、controller 要決定收不收時看這段。（關鍵宣稱的檢查和全新 reviewer 的原則：見 `delegate` skill 的 `## Accept`。）

- 開大檔前先 `wc -l`；只讀關鍵段，不讀整份。
- 長的 pane／transcript review 也是同一個原則：controller 不自己讀完整的 scrollback；叫一個便宜的 subagent 去 capture pane、回報重點，自己只核對關鍵的那幾段（2026-07-06）。
