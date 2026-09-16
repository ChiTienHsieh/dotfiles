# 用 Grok 當 worker

給別的 runtime（Claude Code、Codex）看：怎麼用 `grok -p` 跑一個 worker。Grok 自己不走這條，用 `spawn_subagent`（見 `SKILL.md` 的 `## Who`）。

## 委派前

- SuperGrok 的 quota 是獨立的，`codexbar` 讀不到，所以 Grok 是溢流用的那條：Claude 和 Codex 都快用完時才用，並留意 Grok 自己的 rate-limit 錯誤。

## CLI 做法

```bash
SPEC=$(mktemp -t grok-spec).md; OUT=/abs/path/grok-out.md    # 先把 spec 寫進 $SPEC
grok --prompt-file "$SPEC" --sandbox cc-worker --permission-mode acceptEdits \
  --allow 'Bash(pytest:*)' --disable-web-search --no-auto-update > "$OUT"
```

- `--sandbox cc-worker` 載入 `~/.grok/sandbox.toml`（repo 裡是 `grok/sandbox.toml`）：`workspace` 基底加 kernel 層的讀寫 deny 清單。deny 清單只認那份 TOML，不要信任何複本：`grep -n -A8 deny ~/.grok/sandbox.toml`。
- `--allow 'Bash(<驗證指令>:*)'` 只放行那一個驗證指令，不要放更寬。
- 從 Claude Code 呼叫要用 `dangerouslyDisableSandbox: true` 和絕對路徑（見 SKILL.md 安全邊界第 3 條）。
- Model：`grok models` 列出，`-m` 選、`--effort` 設推理強度。其他看 `grok --help`。

## 怪癖

- headless 寫檔靠 `--permission-mode acceptEdits`（2026-09-03 實測）：`grok -p … --sandbox cc-worker --permission-mode acceptEdits` 在 profile 下成功寫了檔。
- `restrict_network` 在 macOS 沒作用（那是 Linux seccomp），`--disable-web-search` 只拿掉 Grok 自己的 web 工具，子程序 `curl` 照樣連得出去。只餵可信輸入。
- `-p`／`--prompt-file` 在呼叫端的 cwd 執行，不會自己開 worktree；要隔離就自己給它一個 worktree 路徑。
- 它會載入 `~/.claude/CLAUDE.md` 但不展開 `@` import，所以看不到 `agents/AGENTS.md`：所有限制都要寫進 spec。
- deny glob 裡的 `~` 不會展開（會變成 `<cwd>/~/.ssh`），`grok/sandbox.toml` 裡的家目錄項目要寫成絕對的單層 glob，例如 `/Users/*/.ssh/**`。
- `codexbar` 完全看不到 SuperGrok quota，`pick-worker` 會顯示 `n/a`；跑長任務前只能靠 Grok 自己的 rate-limit 錯誤判斷。
