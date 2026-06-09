# cmux-orchestrator — Claude Code 調度站

## 這是什麼
這個資料夾是 orchestrator Claude Code（主控 CC）的家。CC 從 `~/dotfiles` 啟動，tmux session 命名為 `cmux-orchestrator-pit`。它的工作：看設定、調設定、指揮多個 codex agent 平行幹活，並在使用者想進迴路時回報。

## 為什麼住在 dotfiles
dotfiles 是「設定的源頭」（CLAUDE.md、settings.json、cmux、ghostty、tmux 設定都在這）。把 orchestrator 的家設在這個窄目錄，等於把 agent 的預設可寫範圍框在「設定」這一小塊；要動實際專案，必須用 `--add-dir` 明確把該 repo 拉進當下 session。調度站，不是擁有整台電腦的神經中樞。

## ⚠️ 邊界與風險
- **dotfiles 會 push 到 GitHub**（origin: ChiTienHsieh/dotfiles）。任務 log / handoff / 報告一律放 `scratch/`（已 gitignore），不要讓工作內容流進公開 repo。
- **這裡是 guardrail 的源頭**：改 CLAUDE.md / settings.json 會直接影響 agent 規則。好處是能自我調校，風險是被 prompt injection（提示注入）的 agent 可能改寫自己的規則 → 所有改動都會進 `git diff`，push 前務必人工檢查。

## 委派硬規則
- **一律 tmux + 互動式 codex CLI（approve-for-me / auto-review）。禁用 `codex exec` 與任何 YOLO / bypass 旗標。** 理由：exec 不是被沙盒擋，就是得開 YOLO；YOLO 下 codex 讀到惡意網頁/檔案內容會照做（prompt injection）。互動式 approve-for-me 在每個有副作用的動作前多一道自我審查閘門。
- CC 自己只做：唯讀調查、驗收 codex 產出、單檔 ≤10 行瑣修。其餘（實作、跨檔、新建檔、debug）一律委派 codex。
- **務必驗證 codex 的宣稱** — 它會自信地唬爛，要用唯讀工具自己查證。

## 完成偵測：marker-file 慣例
不要靠「pane 不再顯示 Working」判斷完成（approve-for-me 暫停等核准時也不是 Working → 會誤判）。改用：叫 codex 把報告寫到一個檔案、檔尾單獨一行放約定 marker（例 `INSTALL_DONE` / `SCAFFOLD_DONE`）。driver 輪詢該 marker；逾時沒出現 = 可能卡在 approve，人工看一眼那一格。

## driver：drive_codex.sh
用法：

    drive_codex.sh TARGET PROMPTFILE MARKER OUTFILE TIMEOUT NEWWIN

- NEWWIN 非空 → 開新 window 跑 codex；空 → 用既有 TARGET pane。
- 背景跑（run_in_background），跑完叫醒 CC，CC 只在收尾讀一次 → 省 Claude token。
- 長 prompt 放檔案、用單行指令叫 codex 去讀，避免 send-keys 把換行當 Enter 送出。

## tmux 導航
- `Ctrl-b 0/1/2…` 切 window；`Ctrl-b o` 切 pane；`Ctrl-b w` 列出所有 window 選。
- session 名：`cmux-orchestrator-pit`。

## scratch/
gitignored。放任務 prompt、codex 報告、log。可隨意清。
