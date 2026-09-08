# Dotfiles Repo 指示

個人 dotfiles，用符號連結 (symlink) 管理：`install.sh` 從 `~` 連到這個 repo（例如 `~/.zshrc` -> `~/dotfiles/zsh/.zshrc`），改哪一邊都是同一個檔。目錄配置見 `README.md` 的結構圖。

## Agent 記憶檔

- `~/.claude/CLAUDE.md` -> `./claude/CLAUDE.md`（用 `@` 引入 `agents/AGENTS.md`）。`~/.codex/AGENTS.md` 由 `install.sh` 用 `agents/AGENTS.md` + `codex/AGENTS.md` 串接產生；改 repo 裡的檔案，再跑一次 `./install.sh`。

## 自主做完

- 安全、明確的修改：自己走完 review、commit、push 到 `origin`，不要停在還沒 push 的狀態。
- 這是 PUBLIC repo。push 前確認：沒有 secrets、private key、token；沒有本機的 host 細節；沒有不小心寫進去的本機路徑。
- Guardrail／SSOT 修改（CLAUDE.md、AGENTS.md、settings、skills、playbooks）：照 `agents/AGENTS.md` 的 reviewer 路由與 simplify review 規則，reviewer 依 `delegate` skill 選。本 repo 已預先授權非互動式 review，自己跑，不要問使用者是否要 review。
- 只在這些情況停下來問：安全疑慮、破壞性操作、force-push／reset／discard 的決定、付費或資料遺失風險、現有指示推不出來的產品或設計取捨。
- push 被拒或 CI 紅：先自己查，安全的問題自己修。

## Secrets

- 不進追蹤檔。Secrets 放 `~/.secrets/index.sh`（從 `templates/.secrets.template` 建），shell 啟動時 source，永不 commit。

## 維護步驟（需要時再讀）

- alias、新增 dotfile、測 shell／tmux 修改、nvim submodule 細節：碰到那些區域時讀 `agents/notes/dotfiles-maintenance.md`。速記：本機專用內容放 gitignored 的 `bash/.aliases.local`；新 dotfile 要在 `install.sh` 加 symlink 項目。
