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
- 新機器先跑 `nvim/scripts/bootstrap.sh`（brew 裝 node/ripgrep/fd/lazygit/tree-sitter-cli）；沒 node 的話 Mason 裝不了 pyright/vtsls/jsonls/markdownlint-cli2，啟動會噴一排 `failed to install`。
- e2e 測 nvim 不要用 `:sleep` 等 LSP（會擋事件迴圈），用 `nvim file -c 'luafile check.lua'` 裡的 `vim.defer_fn` 非同步讀 `vim.lsp.get_clients()`／`:messages` 再 `qa!`；headless `:checkhealth` 裡 Snacks.image、kitty、`site` 不在 rtp、TERM 那幾條是 headless 假警報，以真實 TTY 為準。
