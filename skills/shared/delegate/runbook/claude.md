# Claude 當 worker

**你自己就是 Claude Code 的話，用內建的 `Agent` tool，絕不從 shell 呼叫 `claude -p`。**
下面的 CLI 走法只給不同 runtime 的呼叫方（Codex、Grok）。

## 內建走法（呼叫方是 Claude Code）

- 用 `Agent` tool，把六項齊全的 spec 當 prompt 傳進去。subagent 會繼承上層的 model，
  除非 agent 定義或 `model` 參數另有指定。

## CLI 走法（呼叫方是 Codex 或 Grok）

```bash
SPEC=/abs/path/spec.md; OUT=/abs/path/claude-out.md
claude -p "$(cat "$SPEC")" --permission-mode auto --output-format text > "$OUT"
```

- `--permission-mode auto` 一定要加：`bypassPermissions` 在第一次用工具時就會 exit 1。
- `claude -p --permission-mode auto` **不是** kernel 層的 sandbox profile。寫入只限 cwd
  加上 `~/.claude/settings.json` 的 allow-list，而且決定要不要放行升權的是 `auto` 分類器，
  不是人。這條路比 codex／grok 那兩條弱：只能餵可信任的輸入。
- 這條路沒有另外的憑證 deny profile。哪些被擋，唯一的依據是現場的 settings 檔：委派前一刻跑
  `grep -n -A10 '"deny"' ~/.claude/settings.json`，以那個輸出為準。不要假設 `.env` 的讀取
  有被擋；輸出裡沒有你需要的 deny，就不要把這條路指向有真實 secret 的目錄樹。

## 眉角

- `claude -p` 用的是跟互動 session 同一份訂閱 quota，不是另一筆預算，所以會算進
  `pick-worker` 回報的數字。
- `--permission-mode bypassPermissions` 在巢狀執行一碰到工具就 exit 1，所以巢狀 worker
  「什麼都沒做」多半是這個原因，不是拒絕。只有 `auto` 能用。
- 它會載入 `~/.claude/CLAUDE.md`，連 `@` 引入的也會，所以看得到共用的 `agents/AGENTS.md`：
  spec 跟那些規則衝突會被拒絕，不會照做。
- 輸出走 stdout；`--output-format text` 讓它好解析。重導向要用絕對路徑，
  因為巢狀執行的 cwd 就是呼叫方的 cwd。
