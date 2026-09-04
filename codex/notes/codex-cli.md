# Codex CLI 筆記

Codex CLI / app 的怪癖、死路、綁定版本的發現。每條標日期，過時就刪。委派相關的怪癖（tmux 經 Guardian、hooks、CodexBar、`codex review`）在 `skills/shared/delegate/runbook/codex.md` 的 Quirks 段。

## 已知的 TUI 死路

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

## CLI thread rename（2026-08-05、`codex 0.145.0` 驗證；2026-08-07 更新）

- TUI 的 `/rename` 是使用者入口；app-server 的對應 operation 是穩定的 `thread/name/set`，接受 `threadId` 與 `name`，可更新 loaded thread 或 persisted rollout。
- Standalone CLI 的 model 不保證擁有 Codex App 注入的 `set_thread_title` tool，也不能假裝自己在 TUI 輸入 `/rename`。曾驗證可用的 private temp-file Stop-hook fallback 已於 2026-08-07 移除：它會在正常 final answer 後產生可見 continuation，使 task 難以閱讀。現在由 `name-task` skill 在有工具時改名；沒有工具時只提出標題，由使用者用 `/rename` 套用。

## Codex.app 字級爆掉（desktop / Electron）

- 檢查 `~/.codex/.codex-global-state.json` 的 `sansFontSize`。正常值是 `15`；`150`、`1500`、`1615` 之類會讓 Electron UI 大到無法操作。
- 不要在 Codex.app 還開著時改 state：app 退出時會用記憶體狀態覆寫檔案。
- 復原流程：`osascript -e 'tell application "Codex" to quit'` → 確認 `/Applications/Codex.app/Contents/MacOS/Codex` 主 process 已消失 → 同步更新 `.codex-global-state.json` 與 `.codex-global-state.json.bak` → 驗證 JSON → 重開 Codex.app。
