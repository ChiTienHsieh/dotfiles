# Dotfiles Repo 指示

個人 dotfiles，用符號連結 (symlink) 管理：`install.sh` 從 `~` 連到這個 repo（例如 `~/.zshrc` -> `~/dotfiles/zsh/.zshrc`），改哪一邊都是同一個檔。目錄配置見 `README.md` 的結構圖。

## Agent 記憶檔

- `~/.claude/CLAUDE.md` -> `./claude/CLAUDE.md`（用 `@` 引入 `agents/AGENTS.md`）。`~/.codex/AGENTS.md` 由 `install.sh` 用 `agents/AGENTS.md` + `codex/AGENTS.md` 串接產生；改 repo 裡的檔案，再跑一次 `./install.sh`。

## 主 checkout 固定留在 main

- `~/dotfiles` 就是使用者正在用的設定：在這裡切 branch，shell、編輯器、agent 的設定會跟著換；使用者在 app 裡改的設定，只要那個檔是 symlink 連進 repo 的，也會寫進目前 checkout 的 branch。
- 要改這個 repo 就另開 worktree（`git fetch && git worktree add <路徑> -b <branch> origin/main`），在 worktree 裡 commit、push、開 PR；主 checkout 不開 branch、不 commit。
- 主 checkout 要跟 main 同步，agent 直接做。在 main 上就 `git pull --ff-only --no-rebase`（`~/.gitconfig` 設了 `pull.rebase=true`，rebase 模式只要有 dirty 檔就整個拒絕，所以 `--no-rebase` 不能拿掉）。不在 main 時，`git branch -r --contains HEAD` 有輸出（目前的 commit 已經在遠端）就 `git switch main` 再照上面 pull，dirty 檔會跟著帶過來；切回 main 後，原 branch 還沒合併的改動會暫時不生效，回報時提一句。只有 HEAD 還沒 push，或 Git 因為 dirty 檔衝突拒絕切換或 pull，才停下來回報。
- 主 checkout 出現不是你改的 dirty 檔，多半是使用者從 app 改的設定：不要混進其他任務的 commit；使用者要把它們收進 main 時，另開 worktree 單獨送一個 PR。PR 合併後那些檔內容已經和 main 一樣，Git 卻還是會擋 pull：`git diff origin/main -- <檔>` 沒輸出，就 `git restore <檔>` 再 pull。
- 常從 app UI 改的設定（目前是 Zed）不用 symlink，`install.sh` 用 `seed_copy` 只在本機還沒有時複製一次，之後的修改留在本機；repo 裡的版本會落後，使用者說要收時，再把本機檔案複製進 worktree 送 PR。

## 自主做完

- 安全、明確的修改：自己走完 review、commit、push 到 `origin`，不要停在還沒 push 的狀態。
- 開 PR 後立刻 `gh pr merge --auto --squash`：repo 已允許 auto-merge、只准 squash、main 需要 `ci-gate` 和 `ai-review-gate`（Claude 審一次，判定通過才算過）兩個檢查都過，過了就自動合併，不用等 cth。PR 動到 `.github/CODEOWNERS` 列的路徑（workflow、agent 指示檔、agent 的權限與 hook、安裝流程），還要 cth 在 GitHub 按 approve。這條就是啟用 auto-merge 的授權。
- `ai-review-gate` 沒過就讀 PR 上的審查留言：意見成立就修；審查沒跑起來就重跑 workflow，重跑還是沒過就停下來回報 cth。留言說審查用的 token 要重新放一份時，只有 cth 能處理，直接回報。
- 每條 PR 另外有 Codex 審一次，留言的帳號是 `chatgpt-codex-connector[bot]`，通常開 PR 後幾分鐘內出現。它不是必要檢查，沒跑或沒有發現都不影響合併；但它的發現是行內 review 討論串，而 main 的 ruleset 要求所有討論串都解決才能合併，所以發現沒處理完，PR 合併不了。追 CI 時一起讀，每條發現都先在那條討論串回覆，再標成已解決：意見成立就修好，回覆改了什麼；不成立就回覆理由。不要沒回覆就直接標。cth 或其他人留的討論串不要自己標，留給留言的人。CI 跑完還沒出現，就留言 `@codex review` 一次；還是沒有就在回報裡提，不用等。PR 已經合併才看到發現，就另開 PR 修。
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

## Code Review Rules

這段只給在 GitHub 上審 PR 的 Codex 讀；其他 agent 做 review 照各自的規則，不適用這段。

- 只評這條 PR 改的行。原本就在 repo 裡的規則和寫法，不算在這條 PR 頭上。
- 優先找這幾種改動：放寬約束 coding agent 的規則、權限或 sandbox；削弱 git hook、CI 檢查或測試；把 secret、token、本機路徑或 host 細節寫進追蹤檔（這是公開 repo）。
- 只改指示檔的文字、規則的意思沒變，不算問題；拿不準意思有沒有變，就當有變，提出來。純風格的意見不要提。
- 用台灣繁體中文回覆。
