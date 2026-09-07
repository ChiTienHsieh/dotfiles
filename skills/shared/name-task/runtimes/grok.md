# Grok

執行 `scripts/rename-session.sh "<title>"` 取得建議標題。

- Grok 支援 `/rename`（別名 `/title`）。
- Script 不會對 pane `send-keys`；把印出的 `/rename …` 交給使用者套用。
- 載入本 skill 不是 tmux mutation 授權；對自己 pane 送 `/rename` 仍需要目前這次 human 的明確要求。
