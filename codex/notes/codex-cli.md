# Codex CLI 筆記

這份檔案記錄調查過的 Codex CLI 怪癖、死路、與綁定特定版本的發現。每條都標日期，過時就刪掉。

## 已知的 Codex CLI 限制

- 截至 2026-06-13、`codex-cli 0.139.0`，官方 Codex config docs 沒有提供 `config.toml` 設定可讓 TUI 的 tool call / tool result 區塊預設收合、摺疊，或像 Claude Code 一樣手動 fold/unfold。
- 不要浪費時間盲試 `tui.collapse_tool_calls`、`tui.fold_tool_calls`、`tui.tool_calls_default_collapsed` 這類看起來合理但未記載的 key；目前可用的 `[tui]` 設定主要是 notifications、animations、show_tooltips、alternate_screen、status_line、terminal_title、theme、keymap 等。
- `hide_agent_reasoning = true` 只會壓掉 reasoning 類資訊，不等於收合 tool calls。若使用者再次問這件事，除非明確要求查最新版本，直接告知目前記錄是不支援。
