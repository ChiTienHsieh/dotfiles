# 本機 machine notes

這個目錄是此 Mac 帳號給 agent 用的本機 SSOT。

- 唯一實體檔：`machine.md`
- Agent 入口：`~/.claude/machine.md` 與 `~/.codex/machine.md`（symlink 到這裡）
- 舊路徑 `~/.config/machine.md` 只留短導向

不要放 token value、private key、recovery code 或憑證檔。不要在這裡 `git init` 或 push。實際狀況（有哪些主機、帳號怎麼分、secret 放在哪）寫進 `machine.md`；secret 本身不行。

Agent 需要機器 context 時，打開這個目錄當 workspace。不要打開整個 `~/.local` 或 `~/.config`。
