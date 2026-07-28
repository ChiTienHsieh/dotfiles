# Codex CLI 筆記

這份檔案記錄調查過的 Codex CLI 怪癖、死路、與綁定特定版本的發現。每條都標日期，過時就刪掉。

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
