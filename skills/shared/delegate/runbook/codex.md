# Codex 當 worker

**你自己就是 Codex 的話，用 Codex 內建的 subagent，絕不從 shell 呼叫 `codex exec`。**
下面的 CLI 走法只給不同 runtime 的呼叫方（Claude Code、Grok）。

## 委派前

- `codexbar usage --provider codex --source cli`：通常是週額度先用完。
  quota 偏低就退回 Claude；headless Codex 是選項，不是非用不可。

## CLI 走法（呼叫方是 Claude Code 或 Grok）

```bash
SPEC=/abs/path/spec.md; OUT=/abs/path/codex-out.md
mkdir -p "$(dirname "$OUT")"          # -o does not create parent dirs
codex exec -p cc-worker --skip-git-repo-check \
  --model gpt-5.6-luna -c model_reasoning_effort=medium \
  -o "$OUT" - < "$SPEC"
```

- **`-p cc-worker`／`-p cc-worker-ro` 旁邊絕不能加任何 `--sandbox` flag。** `--sandbox`
  會覆蓋 profile 的 `default_permissions`，憑證 deny 清單就悄悄失效
  （`codex-cli 0.153.0`：`-p cc-worker --sandbox workspace-write` 讀 `.env.sample`
  讀得好好的；只給 `-p cc-worker` 則是 `Operation not permitted`）。開頭的 banner 兩種情況都印
  `sandbox: workspace-write`，所以它不算證據。驗證方式是 `cat` 一個 deny 清單裡的檔案：
  例如在一個暫用的 git 目錄建 `.env.sample`，在那裡跑一模一樣的指令。
- 唯讀走法：`codex exec -p cc-worker-ro ...`（同一條指令，換 profile）。它載入
  `~/.codex/cc-worker-ro.config.toml`（repo 裡是 `codex/cc-worker-ro.config.toml`）：`:read-only`
  基底加上同一組憑證 deny。單純的 `read-only` 只擋寫入、不擋讀取，所以沒套 profile 的話，
  它會把 `.env`／`~/.ssh` 讀進 context 再送到 OpenAI。
- `codex review` 沒有 `-p` flag（`codex review --help`），所以跑起來沒有 kernel profile：
  只能餵可信任的輸入。
- `-p cc-worker` 載入 `~/.codex/cc-worker.config.toml`（repo 裡是 `codex/cc-worker.config.toml`）：
  `:workspace` 基底（workspace-write 加關閉網路）加上明寫的憑證 deny。deny 清單唯一的依據是
  那份 TOML：自己讀，不要信副本：
  `grep -n deny ~/.codex/cc-worker.config.toml`。
- profile 一定要是 TOML 檔；`-c permissions...."**/*.pem"` 會失敗（dotted-key 解析器
  在 `.pem` 那裡切開），所以 deny glob 只有從 `-p` 載入的檔案才有效。
- 從 Claude Code 跑要帶 `dangerouslyDisableSandbox: true` 並用絕對路徑（見 SKILL.md 第 3 條規則）。
- `codex exec` 會載入 `~/.codex/AGENTS.md`。那些規則禁止這項任務的話，它會 exit 0、diff 是空的，
  外加一句客氣的拒絕：當成拒絕處理，去修規則，不要在開頭塞一段前言矇混過去。
- `--search` 是最上層的 flag（`codex --search exec ...`），而且會把網路打開；只能用在可信任的輸入上。
- 模型：`~/.codex/config.toml` 目前的預設是 `gpt-6-astra`（最強的一級）；
  `gpt-5.6-luna` 是日常 worker 用的模型。自己讀設定檔，不要信這一行：
  `grep -n '^model' ~/.codex/config.toml`。`model_reasoning_effort` 有 low|medium|high|xhigh|max|ultra；
  每個模型支援的等級不同，以 `~/.codex/models_cache.json` 為準。
  其他看 `codex exec --help`。

## 眉角

有日期的觀察紀錄，會影響委派。哪一條不再成立就刪掉。TUI／app 的怪癖
（terminal 標題、字體爆大、thread 改名）放在 `codex/notes/codex-cli.md`。

- **tmux 一律走 Guardian**（2026-07-29，`codex-cli 0.145.0`）：permissions profile
  沒有 tmux socket 的 allowlist，所以每一條 tmux 指令（唯讀的也一樣）都要限定範圍的升權
  加 Guardian review。`codex/rules/tmux.rules` 把 tmux 標成 `prompt`，當第二層。不要加
  唯讀 tmux 的例外（socket 權限看到的是路徑，不是子指令）；不要做「先 deny、再叫 agent
  升權重試」的 PreToolUse hook（`ask` 不支援，被 deny 後的重試也證明不了有升權）；也絕不保留
  `["uv", "run"]` 這類寬的指令執行器 allow 規則：`uv run tmux …` 會對上外層的 allow，跳過 tmux
  的 prompt。這個保證只涵蓋 Codex 自己送出的指令，不涵蓋已核准的程式自己 spawn 的子程序。
- **Hooks 只在 session 開始時載入**（2026-08-08，`codex-cli 0.145.0`）：`install.sh` 把 repo 的
  `codex/hooks.json` merge 進現場的 `~/.codex/hooks.json`，絕不用符號連結 (symlink) 或覆寫那個檔。
  第一次安裝或改了指令之後，重開 Codex 並用 `/hooks` 信任該 hook；已開著的 session 永遠不會吃到。
  照官方 hooks 手冊，統一後的 `exec_command` 工具名是 `Bash`，`PostToolUse` 的輸出會放在
  `tool_response`。
- **CodexBar 與 Keychain**：用 `codexbar usage --provider both --source cli`；光跑
  `codexbar usage` 會去匯入瀏覽器 cookie，可能跳出 macOS Keychain Safe Storage 的提示，
  把非互動的 agent 卡住。它常常要跑 30 秒左右：等 60 秒再判定它卡死；在 sandbox 裡跑失敗
  就到 sandbox 外面重跑。
- **`codex review`**（2026-07-04，`0.142.5`）：在 Claude Code 的 Bash sandbox 裡會死在
  `failed to start managed network proxy … reserve managed loopback proxy listeners`，因為它
  要綁一個 loopback listener：把那一條指令用 `dangerouslyDisableSandbox` 重跑就好，不要去試
  各種 config 變體。它也不接受自訂 prompt 跟 `--commit`／`--base` 一起用；要做 simplify
  角度的 review，改跑 `codex exec`，讓它自己讀 `git diff main...HEAD`。Skill 驗證有固定指令：
  `uv run --with pyyaml python ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py <skill-dir>`。
