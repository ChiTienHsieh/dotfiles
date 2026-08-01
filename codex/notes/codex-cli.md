# Codex CLI 筆記

只記錄已驗證、非顯而易見且仍會改變操作方式的 Codex CLI 怪癖。工作流程與 routing 規則留在 `codex/AGENTS.md`、相關 skill 或 `worker-routing.md`；版本升級後重新驗證，過時就刪除。

## tmux / Guardian 邊界（2026-07-29、`codex-cli 0.145.0`）

- 操作規則以 `codex/AGENTS.md` 與 `codex/rules/tmux.rules` 為準。`workspace-sprin` 不允許 tmux Unix socket；rules 裡的 `prompt` 是 outside-sandbox 的 defense in depth。
- 不要用 PreToolUse hook 模擬 escalation：目前不支援 `ask`，而 `deny` 後也無法可靠證明重試真的 escalated。也不能對 read-only tmux 開 socket 例外，因為 socket 權限不理解 tmux subcommand。
- 不可核准 `["uv", "run"]` 這類可指定任意 executable 的 broad runner；它能繞過 direct-tmux prompt。Guardian 只審 Codex 提交的 command，無法逐次攔截已核准程式自行產生的 child process。

## `codex review` / `codex exec`（2026-08-01、`codex-cli 0.145.0`）

- `codex review --commit <sha>` 與 `--base <branch>` 都不能附 custom prompt，兩者也不能並用。需要自訂 review lens 時，改用 `codex exec` 讀指定 diff。
- sandbox 內仍可能出現 `could not create PATH aliases: Operation not permitted`，但警告本身可伴隨成功的 exit 0；只有指令實際受阻時才依 `codex/AGENTS.md` 的 escalation 規則重跑。

## TUI（2026-08-01、`codex-cli 0.145.0`）

- current schema 沒有讓 tool call/result 預設收合的設定；不要盲試 `tui.collapse_tool_calls`、`tui.fold_tool_calls` 或 `tui.tool_calls_default_collapsed`。`hide_agent_reasoning` 與 `tui.animations` 都不是 folding。
- `[tui].terminal_title` 是 item 識別碼陣列，未知 item 會報錯；可用 item 應查當前 TUI Settings/runtime schema，不在這裡維護易過期的完整清單。
