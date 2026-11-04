# Dotfiles 維護筆記（lazy — 碰到對應區域再讀）

從 repo `AGENTS.md` 移出的維護細節。目錄總覽見 `README.md` 的結構圖。

## Aliases
- 每台機器都用的 alias -> `bash/.aliases`（tracked）。
- 本機專用的 alias -> `bash/.aliases.local`（gitignored，symlink 到 `~/.aliases.local`）。放 repo 內是為了讓 Codex 在 sandbox（只能寫 cwd）也能編輯。
- 需要參數或邏輯就寫 function；alias 名字短（2-4 字元佳）。

## 新增 dotfile
1. 檔案放進對應目錄（例 `zsh/.newconfig`）。
2. 更新 `install.sh` 建 symlink。
3. 需要的話更新 `README.md` 結構圖。

## macOS 設定
- 鍵盤快捷鍵之類的 `defaults` 放 `macos/defaults.sh`，冪等、手動執行（`install.sh` 只提示不自動跑）。新增項目前先 `defaults read <domain>` 讀本機實際值，不背數字。

## Git 設定
- 每台機器都用的預設值放 tracked 的 `git/.gitconfig`。
- 本機專用的 credential helper 和只有這台要的覆寫放 untracked 的 `~/.gitconfig.local`，tracked 的設定檔最後會 include 它。
- 像 `credential.helper` 這種可以多值的設定，先用空值 reset 掉，再寫本機專用的 helper。

## 測試變更
- Shell config 改完：`source ~/.zshrc`（或 alias `src`）。
- tmux 改完：`tmux source-file ~/.tmux.conf`（或 tmux 內 prefix + `:source-file`）。

## Submodules / Nvim
- `nvim/` 是 git submodule（獨立 repo `ChiTienHsieh/nvim-config`）；更新用 `git submodule update --recursive`。
- Nvim 配置：LazyVim 基底；補全用 blink.cmp（從 nvim-cmp 換來，效能）；遊戲化 triforce.nvim（需 `nvzone/volt`）。
- 新機器先跑 `nvim/scripts/bootstrap.sh`（要裝的套件見腳本）；沒有 node 的話 Mason 裝不了 LSP，啟動會噴一排 `failed to install`。
- headless e2e 測 nvim 時，不靠 `:sleep` 等 LSP；用 `nvim file -c 'luafile check.lua'`，在裡面以 `vim.defer_fn` 或 `vim.wait` 非同步讀 `vim.lsp.get_clients()`／`:messages` 再 `qa!`。
- headless `:checkhealth` 裡 Snacks.image、kitty、`site` 不在 rtp、TERM 那幾條是假警報，以真實 TTY 為準。
