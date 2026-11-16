# Claude 桌面 app（Code 分頁）

使用 app 提供的原生 `set_session_title` tool（完整名稱 `mcp__ccd_session_mgmt__set_session_title`）改標題，不需要執行 `scripts/rename-session.sh`。

- 這個 tool 可能列在 deferred tools 裡：先用 `ToolSearch` 以 `select:mcp__ccd_session_mgmt__set_session_title,mcp__ccd_session_mgmt__get_session` 載入，再呼叫。
- 讀目前標題與狀態：`get_session`，`session_id` 傳 `"self"`。
- 目前 task：`session_id` 傳 `"self"`。
- 經授權替其他 task 操作：先用 `list_sessions` 找到精確的 `sessionId`，改名前用 `get_session`（需要看對話內容時加 `list_events`）重新讀取，再把那個 `sessionId` 傳進去。
- 現有標題是使用者自己取的，app 會先請使用者同意才改；app 自動產生的標題直接換掉。使用者拒絕就保留原標題並回報，不重試。
- Subagent 改不了它所在 session 的標題，由主 session 改。
- 使用者明示要 pin／unpin 時，用 `set_pinned`（完整名稱 `mcp__ccd_sidebar__set_pinned`，同樣可能要先用 `ToolSearch` 載入）。
