# Codex CLI 筆記

這份檔案記錄調查過的 Codex CLI 怪癖、死路、與綁定特定版本的發現。每條都標日期，過時就刪掉。

## Codex App delegated-task return（2026-08-09、desktop `26.803.41515`／`codex-cli 0.147.0` 驗證）

- `Stop`／`SessionEnd` 都不是另一個 App task 的 completion callback；`SessionEnd` 可能到 archive/delete、正常關閉或無 client 開啟且 idle 30 分鐘才發生，不能偽裝成 delegation hook。
- App thread tools 的能力邊界與 canonical return contract 見 `codex/notes/codex-task-delegation.md`；執行時使用 `codex-task-return` skill。
- Private registry 是 app-coordination helper，不是 hook；不得把它加進 `codex/hooks.json`、Stop dispatcher 或 live hooks。

## tmux 一律經 Guardian（2026-07-29、`codex-cli 0.145.0` 驗證）

- `workspace-sprin` 不允許 tmux Unix socket；Codex 直接執行或 command wrapper 中明示的任何 tmux 指令，都應在第一次呼叫時要求 scoped escalation，讓 `approvals_reviewer = "auto_review"` 的 Guardian 審查。read-only 指令也不例外。
- 不要用 PreToolUse hook 做「sandbox 先擋，再叫 agent 升權重試」。目前 PreToolUse 不支援 `ask`，而 `deny` 後的 hook input 也無法可靠證明重試是否真的 escalated，容易形成失敗迴圈或被繞過。
- 不對 read-only tmux 子指令開 sandbox 例外。Unix socket 權限只辨識 socket path，不理解 tmux protocol 或 subcommand；一旦 sandbox 可連 socket，同一通道也能送出改變 server 狀態的操作。
- `codex/rules/tmux.rules` 是 outside-sandbox 的 defense in depth：明確把 tmux invocation 判成 `prompt`。真正阻止 sandbox 直連的是 permissions profile 沒有 tmux socket allowlist。
- 不可保留 `["uv", "run"]` 這類可直接指定任意 executable 的 broad command-runner `allow` rule；`uv run tmux …` 會只匹配外層 allow 而繞過 direct-tmux prompt。需要免審的 uv workflow 應核准到固定子指令，例如 `["uv", "run", "pytest"]`。
- 這個保證的邊界是 Codex 提交給 tool/execpolicy 的 command，包括 wrapper 中明示的 tmux；Guardian 不會攔截已核准程式內部自行產生的任意 child process。後者若也要逐次 mediation，需要 OS/socket proxy 級設計，不是 PreToolUse 或 prefix rules 能完整提供。

## tmux worker lifecycle hook（2026-08-08、`codex-cli 0.145.0` 官方文件與 unit/smoke 驗證；live E2E 待重開 Codex）

- `install.sh` 會把 repo 的 `codex/hooks.json` merge 進 live `~/.codex/hooks.json`，保留其他 app-managed hooks；不要直接整檔 symlink 或覆寫 live 檔。
- `track_tmux_workers.py` 只接受 `tmux-orchestration` 定義的 canonical lifecycle receipt 來維護 per-session ledger；`Stop` 發現未處理 worker 時只提醒並擋一次，不呼叫 tmux、不終止程序，所以所有 tmux 操作仍走 Guardian。custom tmux socket（例如 `tmux -L ...`）不會自動追蹤。
- Hook 設定只在 Codex session 啟動時載入。首次安裝或 command 變更後要重開 Codex，並用 `/hooks` review／trust 這個 non-managed command hook；既有 session 不會中途取得新 hook。
- Pane absence receipt 不可用 `tmux display-message -t %NN`；此版本對不存在 target 可能回 exit 0 與空輸出。Canonical receipt 先確認 `tmux list-panes` 查詢成功，再用 `grep -Fx` 區分 present（0）、absent（1）與 query error（>1）；session receipt 同樣用成功 listing 證明 absence。
- 官方 hooks manual 已確認 unified `exec_command` 的 tool name 是 `Bash`，`PostToolUse` output 位於 `tool_response`；tracker 可保留精確 matcher 與欄位，不必對所有 local tools 執行。

## CLI thread rename（2026-08-05、`codex 0.145.0` 驗證；2026-08-07 更新）

- TUI 的 `/rename` 是使用者入口；app-server 的對應 operation 是穩定的
  `thread/name/set`，接受 `threadId` 與 `name`，可更新 loaded thread 或 persisted rollout。
- Standalone CLI 的 model 不保證擁有 Codex App 注入的 `set_thread_title` tool，也不能假裝
  自己在 TUI 輸入 `/rename`。受限 model command 也不能直接讓 nested app-server 寫入
  `~/.codex`。曾驗證可用的 private temp-file Stop-hook fallback 已於 2026-08-07 移除：
  它會在正常 final answer 後產生可見 continuation，使 task 難以閱讀。現在由 `name-task`
  skill 在有工具時改名；沒有工具時只提出標題，由使用者用 `/rename` 套用。
- `thread/name/set` 與 `/rename` 改的是同一個 user-facing thread name；差別在入口與
  live UI event。舊 Stop hook 曾用 standalone `codex exec` end-to-end 驗證 persisted rename；
  同一個互動 TUI 當下是否立即重繪仍未驗證。
- Side conversation 在 0.145.0 是 `ephemeral = true` 的 fork，本身不能改名，也不建立
  persisted rollout；Stop hook payload 沒有專用的 side-chat flag，但會明確帶
  `transcript_path: null`。這不是 side-chat 專用訊號：persisted transcript path 查詢失敗
  也可能是 `null`。標題 Stop hook 已移除，因此目前不再需要依這個欄位猜測或分流。

## CodexBar usage checks

- For quota checks, prefer `codexbar usage --provider both --source cli`.
- Plain `codexbar usage` may import browser cookies and trigger macOS Keychain
  Safe Storage prompts that block non-interactive agents.
- CodexBar can take a while to load, often around 30 seconds. When using it, run
  it outside the sandbox if the sandboxed attempt fails, then wait at least 60
  seconds before deciding it is hung or unavailable.

## codex review 本機固定跑法（2026-07-04）

- `codex review --commit <sha>` 與 `--base <branch>` 都不能同時附 custom
  prompt；CLI 會拒絕（0.142.5 實測）。要 simplify lens 這類自訂視角，改用
  `codex exec` 叫它自己跑 `git diff main...HEAD` 讀 diff。
- sandbox 內遇到 `could not create PATH aliases` 警告或 `in-process app-server
  client: Operation not permitted`，直接走已核准的升權路徑重跑，不要試多種
  flag 變體。
- 在 CC 的 Bash sandbox 內跑 `codex review` 會直接掛在 `failed to start managed
  network proxy: … reserve managed loopback proxy listeners`（0.142.5 實測）——
  它要綁本機 loopback listener，sandbox 不給。固定解法：該指令用
  `dangerouslyDisableSandbox` 重跑，不用試 config 變體。
- skill 驗證固定命令：`uv run --with pyyaml python
  ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py <skill-dir>`，
  避免重踩 `ModuleNotFoundError: yaml` 或 permission denied。

## 已知的 Codex CLI 限制

- 截至 2026-06-13、`codex-cli 0.139.0`，官方 Codex config docs 沒有提供 `config.toml` 設定可讓 TUI 的 tool call / tool result 區塊預設收合、摺疊，或像 Claude Code 一樣手動 fold/unfold。
- 不要浪費時間盲試 `tui.collapse_tool_calls`、`tui.fold_tool_calls`、`tui.tool_calls_default_collapsed` 這類看起來合理但未記載的 key；目前可用的 `[tui]` 設定主要是 notifications、animations、show_tooltips、alternate_screen、status_line、terminal_title、theme、keymap 等。
- `hide_agent_reasoning = true` 只會壓掉 reasoning 類資訊，不等於收合 tool calls。若使用者再次問這件事，除非明確要求查最新版本，直接告知目前記錄是不支援。
- 截至 2026-06-14、目前 installed Codex CLI 接受 `tui.animations = false`（已用 `codex --strict-config -c tui.animations=false --help` 驗證）。這可以降低 TUI spinner/animation 的 redraw，但不等於收合 tool calls，也不會阻止大量 tool output 造成 redraw。

## TUI 終端機標題 `tui.terminal_title`（可自訂，2026-06-23、`codex 0.142.0` 驗證）

- Codex **會**主動設終端機標題（tmux 讀作 pane_title），預設 item 是 `activity, project-name`，所以閒置時看起來就是工作目錄名、像「不會動」。它不是不支援，是預設沒放動態 item。
- `[tui].terminal_title` 吃一個 **item 識別碼字串陣列**，例：`terminal_title = ["run-state", "thread-title"]`。已用臨時 `CODEX_HOME` 寫測試 config + `codex doctor` 驗證：`title source` 會從 `default` 變 `configured`、`title items` 反映設定值。
- 合法 item 識別碼（從 0.142.0 binary strings 挖出，kebab-case）：`project-name`、`current-dir`、`run-state`、`thread-title`、`git-branch`、`context-remaining`、`context-used`、`five-hour-limit`、`weekly-limit`、`codex-version`、`used-tokens`、`total-input-tokens`、`total-output-tokens`、`thread-id`、`fast-mode`、`model-with-reasoning`、`reasoning`、`task-progress`；另有 `activity`（預設值用、像 spinner 的動態活動指示）。寫到未知 item 會報 `terminal title configuration contains unknown item identifiers`。
- 驗證/除錯指令：`codex doctor` 會印 `title source / title items`；`CODEX_HOME=<暫存目錄> codex doctor` 可在不動正式設定下試 config。
- 多 pane（orchestrator）場景推薦 `["run-state", "thread-title"]`：閒置/工作中狀態 + 自訂 session 名，pane 好分辨又看得出 liveness。設定在啟動時載入，**改完要重開 codex** 才生效。
- 對照：Claude Code 的終端機標題**不可挑 item**（格式自動：spinner + session/dir 名），只能用環境變數 `CLAUDE_CODE_DISABLE_TERMINAL_TITLE=1` 整個關掉；想塞自訂狀態文字得繞 hook 的 `terminalSequence` 或 SessionStart hook 的 `sessionTitle`。

## Codex.app Local Recovery (desktop / Electron)
（從 machine.md 移來：這是 Codex.app 通用行為、非機器層級 machine 事實。）
- Codex.app 字級爆掉時，檢查 `~/.codex/.codex-global-state.json` 的 `sansFontSize`。
- 正常值是 `15`；`150`、`1500`、`1615` 之類會讓 Electron UI 大到無法操作。
- 不要在 Codex.app 還開著時改 state：app 退出時會用記憶體狀態覆寫檔案。
- 復原流程：`osascript -e 'tell application "Codex" to quit'` → 確認 `/Applications/Codex.app/Contents/MacOS/Codex` 主 process 已消失 → 同步更新 `.codex-global-state.json` 與 `.codex-global-state.json.bak` → 驗證 JSON → 重開 Codex.app。
