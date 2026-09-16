# 用 Codex 當 worker

給別的 runtime（Claude Code、Grok）看：怎麼用 `codex exec` 跑一個 worker。Codex 自己不走這條，用內建 subagent（見 `SKILL.md` 的 `## Who`）。

## 委派前

- `codexbar usage --provider codex --source cli`：通常是週額度先用完。quota 低就改用 Claude；headless Codex 是選項，不是義務。

## CLI 做法

```bash
SPEC=/abs/path/spec.md; OUT=/abs/path/codex-out.md
mkdir -p "$(dirname "$OUT")"          # -o 不會自己建上層目錄
codex exec -p cc-worker --skip-git-repo-check \
  --model gpt-5.6-luna -c model_reasoning_effort=medium \
  -o "$OUT" - < "$SPEC"
```

- **`-p cc-worker`／`-p cc-worker-ro` 旁邊絕對不要加任何 `--sandbox` flag。** `--sandbox` 會蓋掉 profile 的 `default_permissions`，credential deny 清單就無聲失效（`codex-cli 0.153.0` 實測：`-p cc-worker --sandbox workspace-write` 讀得到 `.env.sample`；只有 `-p cc-worker` 會得到 `Operation not permitted`）。兩種情況 banner 都印 `sandbox: workspace-write`，所以 banner 不算證據。要驗證就 `cat` 一個 deny 清單裡的檔：在 scratch git 目錄建 `.env.sample`，用一模一樣的指令跑。
- 唯讀版：`codex exec -p cc-worker-ro ...`（同指令、換 profile）。它載入 `~/.codex/cc-worker-ro.config.toml`（repo 裡是 `codex/cc-worker-ro.config.toml`）：`:read-only` 基底加同一組 credential deny。單純的 `read-only` 只擋寫不擋讀，沒有 profile 它會把 `.env`／`~/.ssh` 讀進 context 送去 OpenAI。
- `codex review` 沒有 `-p` flag（`codex review --help`），所以沒有 kernel profile：只餵可信輸入。
- `-p cc-worker` 載入 `~/.codex/cc-worker.config.toml`（repo 裡是 `codex/cc-worker.config.toml`）：`:workspace` 基底（workspace-write、網路關閉）加明列的 credential deny。deny 清單只認那份 TOML，不要信複本：`grep -n deny ~/.codex/cc-worker.config.toml`。
- profile 一定要是 TOML 檔；`-c permissions...."**/*.pem"` 會失敗（dotted-key 解析器在 `.pem` 處切開），所以 deny glob 只能從 `-p` 載入的檔案生效。
- 從 Claude Code 呼叫要用 `dangerouslyDisableSandbox: true` 和絕對路徑（見 SKILL.md 安全邊界第 3 條）。
- `codex exec` 會載入 `~/.codex/AGENTS.md`。規則禁止那個任務時，它會 exit 0、空 diff、禮貌拒絕：當作被拒絕，去修規則，不要用前言把它蓋過去。
- `--search` 是頂層 flag（`codex --search exec ...`）而且會打開網路；只在可信輸入下用。
- Model：`~/.codex/config.toml` 目前預設 `gpt-5.6-sol`（重活）；`gpt-5.6-luna` 是日常 worker model。`model_reasoning_effort` 可選 low|medium|high|xhigh。其他看 `codex exec --help`。

## 怪癖

會影響委派的、有日期的觀察。哪一條不再成立就刪掉。TUI／app 的怪癖（終端機標題、字體爆掉、thread 改名）在 `codex/notes/codex-cli.md`。

- **tmux 一律經過 Guardian**（2026-07-29，`codex-cli 0.145.0`）：permissions profile 沒有 tmux socket 的 allow 清單，所以每個 tmux 指令（含唯讀）都要 scoped escalation 和 Guardian 審核。`codex/rules/tmux.rules` 把 tmux 標成 `prompt` 當第二層。不要加唯讀 tmux 例外（socket 權限看的是路徑，不是子指令）；不要做「先 deny、再叫 agent 用 escalation 重試」的 PreToolUse hook（`ask` 不支援，被 deny 的重試也證明不了有 escalation）；也永遠不要留 `["uv", "run"]` 這種寬的 command-runner allow 規則，因為 `uv run tmux …` 會命中外層 allow、跳過 tmux prompt。這個保證只涵蓋 Codex 送出的指令，不涵蓋被核准的程式自己再開的子程序。
- **Hook 只在 session 開始時載入**（2026-08-08，`codex-cli 0.145.0`）：`install.sh` 把 repo 的 `codex/hooks.json` 合併進實際的 `~/.codex/hooks.json`，那個檔絕不 symlink 或覆寫。第一次安裝或改了指令後要重啟 Codex，並在 `/hooks` 裡 trust；跑到一半的 session 永遠不會載到。依官方 hooks 手冊，統一的 `exec_command` 工具名是 `Bash`，`PostToolUse` 的輸出在 `tool_response`。
- **CodexBar 與 Keychain**：用 `codexbar usage --provider both --source cli`；不帶參數的 `codexbar usage` 會讀瀏覽器 cookie，可能跳出 macOS Keychain Safe Storage 提示，把非互動的 agent 卡住。它常常要跑約 30 秒，等 60 秒再判定卡死；sandbox 內失敗就到 sandbox 外重跑。
- **`codex review`**（2026-07-04，`0.142.5`）：在 Claude Code 的 Bash sandbox 內會死於 `failed to start managed network proxy … reserve managed loopback proxy listeners`，因為它要綁 loopback listener。只把這一個指令用 `dangerouslyDisableSandbox` 重跑，不要試 config 變體。它也不接受自訂 prompt 搭 `--commit`／`--base`；要做 simplify 視角就改跑 `codex exec` 讓它自己讀 `git diff main...HEAD`。skill 驗證有固定指令：`uv run --with pyyaml python ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py <skill-dir>`。
