# 用 Claude 當 worker

給別的 runtime（Codex、Grok）看：怎麼用 `claude -p` 跑一個 worker。Claude Code 自己不走這條，用 `Agent` tool（見 `SKILL.md` 的 `## Who`）。

## CLI 做法

```bash
SPEC=/abs/path/spec.md; OUT=/abs/path/claude-out.md
claude -p "$(cat "$SPEC")" --permission-mode auto --output-format text > "$OUT"
```

- `--permission-mode auto` 一定要帶：`bypassPermissions` 在第一次用工具時就會 exit 1。
- `claude -p --permission-mode auto` **不是** kernel 層的 sandbox profile。寫入只限 cwd 加 `~/.claude/settings.json` 的 allow 清單，escalation 由 `auto` 分類器決定，不是人。這條比 codex／grok 的弱，只餵可信的輸入。
- 這條沒有獨立的 credential deny profile，能擋什麼只看當下的 settings 檔。委派前先跑 `grep -n -A10 '"deny"' ~/.claude/settings.json`，以輸出為準。不要假設 `.env` 讀不到；除非輸出顯示有你要的 deny，否則不要指向有真 secrets 的目錄。

## 怪癖

- `claude -p` 吃的是跟互動 session 同一份訂閱 quota，不是另外的額度，會算進 `pick-worker` 報的數字裡。
- `--permission-mode bypassPermissions` 一碰到工具就 exit 1，所以「什麼都沒做」的 nested worker 通常是這個原因，不是拒絕。只有 `auto` 能用。
- 它會載入 `~/.claude/CLAUDE.md` 連同 `@` import，所以看得到共用的 `agents/AGENTS.md`；spec 跟那些規則衝突會被拒絕，不會照做。
- 輸出走 stdout，`--output-format text` 才好解析。要導向絕對路徑，因為 nested run 的 cwd 是呼叫端的 cwd。
