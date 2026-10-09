# Dotfiles Repo 指示

個人 dotfiles，用符號連結 (symlink) 管理：`install.sh` 從 `~` 連到這個 repo（例如 `~/.zshrc` -> `~/dotfiles/zsh/.zshrc`），改哪一邊都是同一個檔。目錄配置見 `README.md` 的結構圖。

## Agent 記憶檔

- `~/.claude/CLAUDE.md` -> `./claude/CLAUDE.md`（用 `@` 引入 `agents/AGENTS.md`）。`~/.codex/AGENTS.md` 由 `install.sh` 用 `agents/AGENTS.md` + `codex/AGENTS.md` 串接產生；改 repo 裡的檔案，再跑一次 `./install.sh`。

## 主 checkout 固定留在 main

- `~/dotfiles` 就是使用者正在用的設定：在這裡切 branch，shell、編輯器、agent 的設定會跟著換；使用者在 app 裡改設定（例如 Zed），也會寫進當下 checkout 所在的 branch。
- 要改這個 repo 就另開 worktree（`git worktree add <路徑> -b <branch> origin/main`），在 worktree 裡 commit、push、開 PR。主 checkout 只跑 `git pull --ff-only`，不切 branch、不 commit。
- 主 checkout 出現不是你改的 dirty 檔，多半是使用者從 app 改的設定：不要收進自己的 commit，寫進回報。

## 自主做完

- 安全、明確的修改：自己走完 review、commit、push 到 `origin`，不要停在還沒 push 的狀態。
- 開 PR 後立刻 `gh pr merge --auto --squash`：repo 已允許 auto-merge、只准 squash、main 需要 1 個 approval 加 `ci-gate`。Sprin 在 GitHub 按 approve 後就自動合併，不用再回來按 merge；這條就是啟用 auto-merge 的授權。
- 這是 PUBLIC repo。push 前確認：沒有 secrets、private key、token；沒有本機的 host 細節；沒有不小心寫進去的本機路徑。
- Guardrail／SSOT 修改（CLAUDE.md、AGENTS.md、settings、skills、playbooks）：照 `agents/AGENTS.md` 的 reviewer 路由與 simplify review 規則，reviewer 依 `delegate` skill 選。本 repo 已預先授權非互動式 review，自己跑，不要問使用者是否要 review。
- 只在這些情況停下來問：安全疑慮、破壞性操作、force-push／reset／discard 的決定、付費或資料遺失風險、現有指示推不出來的產品或設計取捨。
- push 被拒或 CI 紅：先自己查，安全的問題自己修。

## 寫進 repo 的 zh-TW

- 這個 repo 裡的中文（指示、skills、學習紀錄）會被所有 agent 讀進去，agent 會照讀到的語氣講話、寫文件。寫歪一句，之後每個 agent 都跟著歪。
- 寫進來前唸一遍：台灣人會這樣講嗎？聽起來有 AI 腔、從英文硬翻，或要讀兩遍才懂，就改到自然、清楚為止。拿不準就挑最白話的寫法，在回報裡標出來。
- 已知的地雷詞不列在這裡，交給 pre-commit 和 CI 擋：被擋就照提示改；誤擋就把整段片語加進 `hooks/jargon-allowlist.yml` 的 `zh_tw_exceptions`。發現新的，沒有正當用法的補進同檔的 `zh_tw_terms`，其他寫進回報讓使用者決定。

## Secrets

- 不進追蹤檔。Secrets 放 `~/.secrets/index.sh`（從 `templates/.secrets.template` 建），shell 啟動時 source，永不 commit。

## 維護步驟（需要時再讀）

- alias、新增 dotfile、測 shell／tmux 修改、nvim submodule 細節：碰到那些區域時讀 `agents/notes/dotfiles-maintenance.md`。速記：本機專用內容放 gitignored 的 `bash/.aliases.local`；新 dotfile 要在 `install.sh` 加 symlink 項目。
