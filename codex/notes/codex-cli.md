# Codex CLI 筆記

這份檔案記錄調查過的 Codex CLI 怪癖、死路、與綁定特定版本的發現。每條都標日期，過時就刪掉。

## 已知的 Codex CLI 限制

- 截至 2026-06-13、`codex-cli 0.139.0`，官方 Codex config docs 沒有提供 `config.toml` 設定可讓 TUI 的 tool call / tool result 區塊預設收合、摺疊，或像 Claude Code 一樣手動 fold/unfold。
- 不要浪費時間盲試 `tui.collapse_tool_calls`、`tui.fold_tool_calls`、`tui.tool_calls_default_collapsed` 這類看起來合理但未記載的 key；目前可用的 `[tui]` 設定主要是 notifications、animations、show_tooltips、alternate_screen、status_line、terminal_title、theme、keymap 等。
- `hide_agent_reasoning = true` 只會壓掉 reasoning 類資訊，不等於收合 tool calls。若使用者再次問這件事，除非明確要求查最新版本，直接告知目前記錄是不支援。
- 截至 2026-06-14、目前 installed Codex CLI 接受 `tui.animations = false`（已用 `codex --strict-config -c tui.animations=false --help` 驗證）。這可以降低 TUI spinner/animation 對 cmux terminal renderer 的壓力，但不等於收合 tool calls，也不會阻止大量 tool output 造成 redraw。

## cmux socket access in Codex sandbox

- 截至 2026-06-13、`codex-cli 0.139.0`，讓 sandboxed Codex command 連到 cmux Unix socket 需要 custom permission profile，而不是只加 `sandbox_workspace_write.writable_roots`。
- 已驗證可行的 installed `config.toml` 形狀：`default_permissions = "workspace-cmux"`，`[features] network_proxy = true`，`[permissions.workspace-cmux] extends = ":workspace"`，以及 `[permissions.workspace-cmux.network] enabled = true`, `mode = "limited"`, `unix_sockets = { "$HOME/.local/state/cmux 的絕對路徑" = "allow" }`。`codex/config.toml` 保持 portable，`install.sh` 會在 copy 到 `~/.codex/config.toml` 後用當下 `$HOME` 寫入絕對 socket path。
- 實測 `codex sandbox -P workspace-cmux cmux ping` 會回 `PONG`；`codex sandbox -P workspace-cmux curl https://example.com` 仍會被 limited proxy 擋下，避免順手打開一般 outbound network。
- 已踩過的死路：top-level `network.allow_unix_sockets = [...]` 會被 config parser 接受，但 `codex sandbox cmux ping` 仍會 `Operation not permitted`；`sandbox_workspace_write.network_access = true` 也不會放行 AF_UNIX socket。
