# Grok 當 worker

**你自己就是 Grok 的話，用 `spawn_subagent` tool，絕不從 shell 呼叫 `grok -p`。**
下面的 CLI 走法只給不同 runtime 的呼叫方（Claude Code、Codex）。

## 委派前

- SuperGrok 的 quota 是獨立的，`codexbar` 讀不到，所以 Grok 是溢位用的那條路：
  Claude 和 Codex 都偏低時才用，並且留意 Grok 自己的 rate-limit 錯誤。

## CLI 走法（呼叫方是 Claude Code 或 Codex）

```bash
SPEC=$(mktemp -t grok-spec).md; OUT=/abs/path/grok-out.md    # write the spec into $SPEC first
grok --prompt-file "$SPEC" --sandbox cc-worker --permission-mode acceptEdits \
  --allow 'Bash(pytest:*)' --disable-web-search --no-auto-update > "$OUT"
```

- `--sandbox cc-worker` 會載入 `~/.grok/sandbox.toml`（repo 裡是 `grok/sandbox.toml`）：`workspace`
  基底加上 kernel 層的讀＋寫 deny 清單。deny 清單唯一的依據是那份 TOML：自己讀，不要信副本：
  `grep -n -A8 deny ~/.grok/sandbox.toml`。
- `--allow 'Bash(<verify cmd>:*)'` 只放行驗證指令本身；不要加任何更寬的。
- 從 Claude Code 跑要帶 `dangerouslyDisableSandbox: true` 並用絕對路徑（見 SKILL.md 第 3 條規則）。
- 模型：`grok models` 列出；`-m` 選模型，`--effort` 選 reasoning。其他看 `grok --help`。

## 眉角

- headless 寫入能動，靠的是 `--permission-mode acceptEdits`（2026-09-03 驗證過）：
  `grok -p … --sandbox cc-worker --permission-mode acceptEdits` 在 profile 下成功寫了檔案。
- `restrict_network` 在 macOS 上沒作用（它是 Linux seccomp），`--disable-web-search` 也只拿掉
  Grok 自己的網路工具：子程序的 `curl` 照樣連得出去。只能餵可信任的輸入。
- `-p`／`--prompt-file` 都在呼叫方的 cwd 執行，從不建 worktree：要隔離就自己開 worktree，
  把路徑交給它。
- 它會載入 `~/.claude/CLAUDE.md`，但不展開 `@` 引入，所以永遠看不到
  `agents/AGENTS.md`：每條限制都要寫進 spec 本身。
- `deny` glob 裡的 `~` 不會展開（會變成 `<cwd>/~/.ssh`），所以 `grok/sandbox.toml` 裡
  家目錄的項目要寫成絕對路徑、只用一段 `*` 的 glob，例如 `/Users/*/.ssh/**`。
- `codexbar` 完全看不到 SuperGrok 的 quota，所以 `pick-worker` 會顯示 `n/a`；長時間執行前，
  你只有 Grok 自己的 rate-limit 錯誤可以參考。
