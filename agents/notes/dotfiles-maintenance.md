# Dotfiles 維護筆記（lazy — 碰到對應區域再讀）

從 repo `AGENTS.md` 移出的維護細節。目錄總覽見 `README.md` 的結構圖。

## Aliases
- Portable aliases -> `bash/.aliases`（tracked）。
- Machine-specific aliases -> `bash/.aliases.local`（gitignored，symlink 到 `~/.aliases.local`）。放 repo 內是為了讓 Codex 在 sandbox（只能寫 cwd）也能編輯。
- 需要參數或邏輯就寫 function；alias 名字短（2-4 字元佳）。

## 新增 dotfile
1. 檔案放進對應目錄（例 `zsh/.newconfig`）。
2. 更新 `install.sh` 建 symlink。
3. 需要的話更新 `README.md` 結構圖。

## Git configuration
- Portable defaults stay in tracked `git/.gitconfig`.
- Machine-specific credential helpers and host-only overrides go in untracked `~/.gitconfig.local`, which the tracked config includes last.
- For multi-valued settings such as `credential.helper`, reset with an empty value before the machine-specific helper.

## 測試變更
- Shell config 改完：`source ~/.zshrc`（或 alias `src`）。
- tmux 改完：`tmux source-file ~/.tmux.conf`（或 tmux 內 prefix + `:source-file`）。

## Submodules / Nvim
- `nvim/` 是 git submodule（獨立 repo `ChiTienHsieh/nvim-config`）；更新用 `git submodule update --recursive`。
- Nvim 配置：LazyVim 基底；補全用 blink.cmp（從 nvim-cmp 換來，效能）；遊戲化 triforce.nvim（需 `nvzone/volt`）。
