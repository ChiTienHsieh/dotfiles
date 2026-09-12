# Dotfiles

[![CI](https://github.com/ChiTienHsieh/dotfiles/actions/workflows/ci.yml/badge.svg)](https://github.com/ChiTienHsieh/dotfiles/actions/workflows/ci.yml)

[English](README.md) | 繁體中文

macOS／Unix 用的個人 dotfiles，用符號連結 (symlink) 管理。除了一般的 shell、git、tmux、編輯器設定，這個 repo 也放了我用的 coding agent（Claude Code、Codex CLI、Grok）的指示檔與 skills。

## 快速開始

需要 Python 3.11 以上，且 `python3` 在 `PATH` 上。

```bash
git clone --recursive https://github.com/ChiTienHsieh/dotfiles.git ~/dotfiles
cd ~/dotfiles
./install.sh
source ~/.bash_profile
brew bundle   # 可選：依 Brewfile 安裝 CLI 工具、cask、字型與 npm 全域套件
```

`Brewfile` 是主力 Mac 直接 `brew bundle dump` 的結果；工具鏈變動時用 `brew bundle dump --force` 重新產生。

`install.sh` 把 `~` 下的每個檔案連結到這個 repo。會被覆蓋的檔案先備份到 `~/.dotfiles_backup/<時間戳>/`，要移除就把備份複製回去。

## 內容

```
dotfiles/
├── bash/ zsh/ vim/ tmux/ ghostty/   # shell、編輯器、終端機設定
├── git/                             # .gitconfig、全域 ignore、pre-commit hooks
├── gh/                              # GitHub CLI 設定
├── bun/ npm/ pnpm/                  # 本機套件管理器防護的種子檔
├── nvim/                            # Neovim 設定（git submodule）
├── agents/                          # 所有 agent 共用的 AGENTS.md 與 notes
├── claude/                          # Claude Code：CLAUDE.md、settings、hooks、agents
├── codex/                           # Codex CLI：config 種子、hooks、sandbox 設定
├── grok/                            # Grok：sandbox 設定
├── skills/                          # shared/、claude/、codex/ 三類 skills
├── hooks/                           # pre-commit hook 用的英文詞彙 allowlist
├── scripts/                         # sync-skills.sh 與安裝輔助腳本
├── userscripts/                     # 瀏覽器 userscript（Tampermonkey）
├── templates/                       # secrets 與本機專用檔的範本
├── tests/                           # 安裝與 hook 測試（CI 會跑）
└── install.sh
```

## Agent 怎麼載入規則

所有 agent 共用一份規則檔，各 runtime 用自己支援的方式拿到它：

```text
~/.claude/CLAUDE.md -> claude/CLAUDE.md                 # 用 @ 引入 agents/AGENTS.md
~/.codex/AGENTS.md  =  agents/AGENTS.md + codex/AGENTS.md  # install.sh 串接產生
```

改 repo 裡的檔案，再跑一次 `./install.sh`。`~/.codex` 只連結受管理的檔案，既有的 `config.toml` 與 session 資料不動。

`skills/shared/` 同時裝進 Claude Code 與 Codex；`skills/claude/`、`skills/codex/` 只裝各自的 runtime。只想重新同步 skills：

```bash
./scripts/sync-skills.sh
```

## 只在本機的檔案

從範本建立，永不 commit：

- `~/.secrets/index.sh`：API key 與 token，shell 啟動時 source
- `~/.aliases.local`：本機專用 alias
- `~/.gitconfig.local`：credential helper 與只有這台機器要的 git 設定

## 更新

```bash
cd ~/dotfiles
git pull
git submodule update --recursive
./install.sh
```
