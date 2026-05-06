# Codex Machine Notes

這份文件記錄這台 Mac 的 secret-free machine-specific 行為。不要寫 token value、private key、recovery code，或完整 secret env var 內容。

## Global Git Hooks

- 這台 Mac 的 global Git config 設定 `core.hooksPath = ~/.config/git/hooks`，來源由 dotfiles 管理：`git/.config/git/hooks/`。
- global `pre-commit` 會檢查 staged `.md` prose 的繁中比例，預設門檻是 `80%`。
- 檢查器位置：`~/.config/git/hooks/lib/check-md-zh-tw-ratio.mjs`。
- 檢查會略過 frontmatter、code block、inline code、URL，並允許常見 English technical terms。
- repo 可以用 `.md-zh-tw-policy` 調整或關閉規則；例如 `enabled=false` 可關閉整個 repo 的檢查。
- repo 可以用 `.md-zh-tw-ignore` 排除路徑，語法接近 `.gitignore`。
- 單檔可以加 `<!-- md-zh-tw: ignore -->` opt out。
- 全域術語可以放進 `~/.config/git/md-zh-tw-allow` 或 `~/.md-zh-tw-allow`，一行一個 English term；repo-local `.md-zh-tw-allow` 仍可補專案專屬詞。
- 若某個 repo 自己設定 local `core.hooksPath`，它會蓋掉 global hook；這種 repo 需要在自己的 hook 裡手動呼叫同一支 checker。
