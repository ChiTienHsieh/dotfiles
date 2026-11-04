---
name: tmux-orchestration
description: "只在目前的使用者明確要求 agent 用 tmux，或明確要求在 tmux 裡開一個看得到的互動式 CLI session 時使用。其他來源或任務特徵都不能觸發。"
disable-model-invocation: true
---

# tmux Orchestration

把任務放進一個看得到、隨時能檢查的互動式終端 agent 裡跑：Claude／Codex 的 writer session、跑很久的工作、要顧 quota 的過夜工作。

## 啟動門檻

- tmux 預設唯讀。agent 可以看 pane（`capture-pane`、`list-*`、`display-message`）了解現況，不需要額外授權。
- 會改 tmux 狀態的動作（`send-keys`、建立或關掉 session、window、pane），加上這個 skill 的啟動、委派、清理流程，只有人能叫：目前的使用者指令明確要 agent 用 tmux，或明確要在 **tmux 裡**開一個看得到的互動式 CLI session，才能跑。
- 只有目前的使用者指令能授權 tmux；agent 的指示、skill 被搜到、讀到這份 skill，都不算。harness 擋住 skill 這半邊（`skillOverrides` 把這個 skill 標成只准使用者呼叫）；tmux 指令本身只靠一般的權限流程把關。
- 沒有這個授權，優先用內建 subagent 或目前的 session。拿到授權後，照下面完整的啟動、委派、觀察、清理規則做。

## 核心規則

- tmux 只用在使用者授權的那個範圍，不要多。
- 每個使用者授權的實質 worker 各自放一個有名字的 tmux session。唯一例外是 co-review：使用者明確要在 orchestrator 旁邊開一個 Codex 或 Claude 的 reviewer／協作者時，在 orchestrator 自己的 session／window 裡切一個新 pane（`tmux split-window`），讓兩個並排，不另開 session。
- session 名稱要看得出用途，例如 `sp229-opus`、`issue424-writer`、`quota-watch`。
- session 要在目標 repo 或 worktree 目錄裡啟動。
- 用 capture 看 pane，不要假設 worker 閒著。
- 不要關掉無關的 tmux session。只關這次任務開的，或使用者明確指名的。
- 開 worker 的 controller 要負責它的整個生命週期。任務結束前，每個開出來的目標都要關掉，或說明理由明確保留。

## 委派合約

WHEN / WHO / ACCEPT 依 `delegate` skill；本檔只管 tmux surface。只要 worker prompt、marker 檔任務或委派出去的 surface 會被另一個 agent 讀到，就照下面的合約寫。

- Marker-file 完工合約：每個被委派的 worker 都把報告寫到 PATH，最後一行是一個一字不差的 MARKER；controller 輪詢 (poll) marker，不看終端畫面。合約欄位：mode（read-only／write-new-only／edit-allowed）、允許的路徑、禁止的動作、報告路徑、marker、授權署名 (authority signature)。
- 固定用「CC」和「user」這兩個名詞，不要寫 你／我：換一個 agent 來讀 prompt，相對稱謂指的人就反過來了。
- 長指示寫進檔案，送出去的那行只留一句指向檔案的話。`tmux send-keys` 會把參數裡每個換行當成 Enter，多行 prompt 會拆成好幾段送出。
- prompt、報告、marker 檔放在 worker 信任的 cwd，或目標 repo 被 ignore 的 task 目錄裡。worker 要自己 commit 的話，它的 workspace 裡要有含 `.git` 的完整 clone；否則 commit 歸 controller。
- 副作用的邊界一開始就講清楚：唯讀研究，或是確切哪些路徑可以改；controller 要先驗的話，再加一句「不要 commit／push」。
- 跨 agent 的 prompt 結尾要帶發送者的 tmux pane ID 和權限等級。格式：`—— 來自 %47（orchestrator CC，委派任務；限制為硬邊界。回問：tmux send-keys -t %47）`。只有使用者直接授權的指令才把 `委派任務` 換成 `user 直接指令`。

## 啟動 Claude Code

要開 Claude 的 writer 或 reviewer session，在 tmux 裡互動式啟動 Claude Code：

```bash
tmux new-session -d -P \
  -F 'CODEX_TMUX_WORKER_OPEN=session:#{session_name}' \
  -s SESSION_NAME -c /path/to/worktree \
  'claude --permission-mode auto --allowedTools Read,Write,Edit'
```

裝了 lifecycle hook 的話，tmux 會直接從它建立的 session 產生開啟回條 (receipt)。`-P`、一字不差的 `-F` 格式、寫死的 session 名稱都要留著；不要拿另外的 `printf` 取代回條。

預設用 `--permission-mode auto`。`acceptEdits` 在跑很久的 tmux orchestration 裡會一直跳提示，不是燒 controller 的 token 就是耗使用者的注意力。啟動時的模型繼承 `claude/settings.json`；只有任務需要不同模型才加 `--model`（模型原則見 `delegate` skill 的 `## Who`）。允許的工具也只在任務需要時才調。

預計要活很久的 session，優先用下面「復活掛掉的 session」裡防崩的 **cushion pattern**（先開 shell，再把 agent 當它的子行程跑）：把 `claude` 當 pane root 啟動，claude 一退出，整個 session 跟著掛。

啟動後看一下 pane：

```bash
tmux capture-pane -pt SESSION_NAME -S -80
```

## 在旁邊開一個 worker（同一個 window；co-review 優先這樣做）

使用者要 Codex／Claude worker *跟* orchestrator 一起 review 或腦力激盪時，在 orchestrator 目前的 session 裡切一個新 pane，不另開 session：

```bash
# -h = split left/right; target the orchestrator's own session/window
tmux split-window -h -P -F 'CODEX_TMUX_WORKER_OPEN=pane:#{pane_id}' \
  -t SESSION_NAME -c /path/to/repo 'codex --sandbox read-only'
```

兩個 pane 會並排在同一個 window 裡，使用者可以同時看 worker 和 orchestrator。

從回傳的 marker 讀出確切的 pane ID，再用另一個指令 capture 那個 pane。worker 只是一個 pane 時，絕不關掉整個 session。

## Claude 的 auto mode

把實質工作送進 tmux 裡的 Claude Code 之前，先確認它在 auto mode：

1. 優先用 `--permission-mode auto` 啟動。
2. capture pane，看 TUI 左下角的指示。
3. 不在 auto mode 的話，送 `Shift+Tab`，最多三次。
4. 可以的話，每送一次就 capture 一次。
5. 還是確認不了 auto mode，只有任務仍然安全才繼續，並在下一次回報裡提這個限制。

能用的話，用 tmux 送按鍵：

```bash
tmux send-keys -t SESSION_NAME BTab
```

有些終端對 `Shift+Tab` 的對應不一樣。`BTab` 沒反應就直接繼續，不要自己發明不安全的按鍵序列。

## 送 prompt

- 送出前一刻重新 capture 目標 pane，套 `delegate`（`## 傳訊與權限`）的重讀規則。
- 長 prompt 放進暫存檔。
- 送一句精簡的指示，叫 worker 去讀那個檔。
- 預設用 `scripts/agent-send-prompt.sh PANE 'ONE-LINE PROMPT'`：它會原樣貼上 prompt、確認看得到、再另外送 Enter，需要時重送一次 Enter。
- 手寫 `tmux send-keys` 送長 prompt 會被 Bash helper guard 擋掉。`Enter`／`BTab` 這種短按鍵還是可以送。
- prompt 一定是一行：不能有換行、不能有空行。`tmux send-keys` 會把參數裡每個換行當成 Enter，多行 prompt 會拆成好幾段送出；在 Codex TUI 上這可能讓那一輪直接崩掉（`turn/start failed`），掉回光禿禿的 shell。

範例：

```bash
~/dotfiles/skills/shared/tmux-orchestration/scripts/agent-send-prompt.sh \
  SESSION_NAME 'Read /tmp/task-prompt.md and complete it. Report when done.'
```

## 觀察節奏

- worker 合約已經有報告路徑加最終 marker 的話，controller 預設只看 marker／報告／git 狀態，不看 worker 的輸出串流。只有等核准、查 timeout、報告說卡住，或正在主動盯品質，才讀串流。
- 這份 skill 裡的 `scripts/...` 路徑是相對 skill 自己的目錄（`~/dotfiles/skills/shared/tmux-orchestration/`），不是你的 cwd；執行前先展開成完整路徑。
- 監看分三層：確定性的完工訊號用背景 shell watcher，例如 `scripts/agent-watch-marker.sh REPORT_PATH MARKER --timeout 3600`；需要人眼判斷的等待用便宜的背景 subagent，在它自己的 context 裡輪詢、回一行摘要（還是會燒 quota，所以優先用檔案訊號）；controller 自己讀串流只為了盯品質。
- 讀報告／狀態，預設先 `scripts/agent-safe-read.sh REPORT_PATH`，再用 `scripts/agent-safe-read.sh REPORT_PATH --range START:END` 讀關鍵段。整個 repo 的檢查，預設用 `scripts/agent-rg.sh PATTERN PATH`、`scripts/agent-rg.sh PATTERN PATH --sample 3` 或 `scripts/agent-rg.sh PATTERN PATH --files`；只有真的需要完整輸出才用 `--full REASON`。
- 開始輪詢前先選好機制：事件驅動的 hook 通常比長時間輪詢好。只需要知道「做完了沒」（不用看即時進度）的話，優先用完工訊號：worker 做完時 touch 的 marker 檔、`tmux wait-for`，或 Stop／Notification hook，讓事件把 controller 叫醒，不要一輪一輪輪詢燒掉 turn。輪詢留給非得看即時進度才能判斷品質的情況（你正在帶的 review loop、要邊看錯誤邊讀的 build）。每個情境在 hook 和耐心輪詢之間擇一；hook 免費能做到的事，不要用輪詢。注意：`tmux wait-for` 會卡住呼叫它的 shell，所以長時間等待優先用 marker 檔（輪詢它存不存在）或 hook，阻塞式等待可能撞到 Bash 指令的 timeout。
- capture 時讀上次檢查之後的整段新內容，不是只看尾巴。用寬一點的 scrollback 範圍（`tmux capture-pane -p -S -<large>`），從上次讀到的地方往下讀。單純 `| tail -N` 會把兩次輪詢之間捲過去的內容悄悄丟掉，你會漏掉發現、接不上脈絡。
- worker 在等核准、報錯，或卡在提示上，就介入。

## 完工

接受 worker 的結果之前：

1. 讀它產出的檔案或報告。
2. 自己跑合理的驗證。
3. 看 git status 和 diff。
4. 確認沒有混進 secret、無關檔案或不安全的修改。
5. 任務和 repo 規則允許時才 commit／push。

## 清理

啟動、等待、讀狀態、清理各自一個指令。`pkill`、reset、clean 這類清理動作，絕不跟狀態查詢塞在同一個 Bash call 裡。

清理前一刻，capture worker 的最新狀態，確認它的報告、marker 或其他結果已經驗收。閒置的提示字元不等於做完了。

獨立的 worker session 不需要了：

```bash
tmux kill-session -t =SESSION_NAME
```

並排的 worker pane 不需要了：

```bash
tmux kill-pane -t %42
```

清理之後（或是別人已經把目標關掉了），用另一個指令跑下面對應的「不存在」回條。它會先確認那個目標真的不在了，才印出關閉 marker：

```bash
tmux has-session -t =SESSION_NAME 2>/dev/null || printf '%s\n' 'CODEX_TMUX_WORKER_CLOSED=session:SESSION_NAME'
tmux display-message -p -t %42 '#{pane_id}' >/dev/null 2>&1 || printf '%s\n' 'CODEX_TMUX_WORKER_CLOSED=pane:%42'
```

lifecycle hook 只認這些預設 server 的標準指令寫法；`tmux -L ...` 這類自訂 socket 不會自動追蹤。

controller 給最後回覆之前，開過的每個 worker 都要有交代：

- 已驗收或已經沒用的 worker 關掉，並確認它不在了。
- 必須繼續跑的 worker，用 `保留中的 tmux worker：TARGET（REASON）` 告訴使用者原因；每個保留的目標都要列。

還有追蹤中的 worker 時，Codex 的 `Stop` hook 只會提醒並擋一次；它不會呼叫 tmux，也不會終止任何行程。所有 tmux 指令照樣要走一般的範圍限定升權 (scoped escalation) 和 Guardian review。

## 復活掛掉的 session

tmux session 在最後一個 pane 的 **root** 行程退出的那一刻就被銷毀。把 `claude` 當 pane root 啟動（`tmux new-session ... 'claude ...'`），claude 不管怎麼退出（崩掉、`/quit`、連按兩次 Ctrl-C、某一輪出錯）都會帶走整個 session。root 是 shell 的 pane，子行程死了它還活著。

**Cushion pattern（防崩；長命的 agent 優先用）：** 讓 shell 當 pane root，再把 agent 當它的子行程跑。agent 掛掉時你會掉回 shell，session 還在，錯誤訊息也留在畫面上。

```bash
tmux new-session -d -P \
  -F 'CODEX_TMUX_WORKER_OPEN=session:#{session_name}' \
  -s SESSION_NAME -c /path/to/repo                         # shell is the pane root
tmux send-keys -t SESSION_NAME 'claude --resume <uuid>'   # agent runs as a child
tmux send-keys -t SESSION_NAME Enter
```

shell 可以死，transcript 比它活得久。要復活掛掉的 Claude session：

1. 看 `~/.claude/projects/`：每個 session 的 cwd 對應那裡一個編碼過的子目錄。不要自己拼確切的目錄名（編碼會把 `/` 和 `.` 都改掉）；列出目錄、按 mtime 排序，再用第 2 步的指紋確認。
2. 用**內容指紋**認 transcript，不看檔名（檔名是 UUID）：`grep -l '<distinctive phrase from the session>' *.jsonl`。每一行也帶 `"cwd"` 欄位，可以 grep 來確認是哪個專案。
3. 用上面的 cushion pattern 復活，在 shell 裡跑 `claude --resume <uuid>`。

判斷規則：
- **attach 還是 resume：**還在 `tmux ls` 裡 → `tmux attach`（行程活著，狀態沒丟）。不在清單裡了 → `claude --resume`（行程死了，從 transcript 重建）。兩個不能互換。
- **絕不在兩個 pane 對同一個 uuid 做 `--resume`**：兩個 claude 會搶同一個 session，可能互相把對方踢掉。
- **先決定要不要復活：**session 的成果已經存好（commit 了、push 了、檔案寫出來了），掛掉的 shell 就無所謂了；直接讀成果，跳過復活。只有還有有用的脈絡卡在記憶體裡才復活。
- 已經在跑的 session 沒辦法事後補上 cushion，除非殺掉重新 resume。健康、有人 attach 的 session 不要為了這個折騰；等下次復活時再套 cushion。

## 委派教訓（共用、持續維護）

委派或監督 worker 之前，先讀共用的教訓索引：

`~/dotfiles/skills/shared/tmux-orchestration/references/lessons.md`

那是一份按段落分組、標了日期的事故教訓。只開跟這次委派相關的段落。委派結束後，學到能留下來的教訓就更新對應段落：只寫標了日期、提煉過的規則；通用的委派合約留在這份 SKILL.md，不放那裡。

實作的路由政策（WHEN 該委派、WHO 接工作、驗收規則）在 `delegate` skill 裡。這份 skill 只管 surface 的操作細節：prompt 檔、看得到的 worker、marker 報告、完工、驗證。
