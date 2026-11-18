# tempo

切換 Claude 的工作節奏。輸入框上方多一排 `Tempo [off] [autonomous]`，點一下就換模式：

- **off**：照平常的規則。
- **autonomous**：Sprin 不想被問的時候用。之後他每送出一則訊息，後面都會附一段他看不到、模型讀得到的短規則：能自己判斷的就做到底，硬邊界照舊先問。原文在 `hooks/register.tsx` 的 `GO_NOTE`，改字只改那裡。

band 的按鈕刻意不設數字快捷鍵：輸入框空著時打數字會觸發 band 按鈕，會把回答編號選項的「1」吃掉。

也可以打 `/tempo` 在兩者間切換，或 `/tempo off`、`/tempo autonomous`（`auto`、`go` 也可以）。目前模式會顯示在輸入框下方的狀態列。模式只記在當下這個 session，開新 session 回到 off。

## 安裝

PR 合併、主 checkout pull 之後，在 terminal 跑一次：

```bash
claude plugin marketplace add ~/dotfiles/claude/mods
claude plugin install tempo@sprin-mods
```

裝在 user scope，terminal 和 Mac app 的 Code tab 都會載入。marketplace 是本機資料夾，Claude Code 直接讀 `~/dotfiles/claude/mods/tempo`，改完檔案在 session 裡跑 `/reload-plugins` 就生效，不用重裝。

## 為什麼這樣做

- **用 `prompt.submit` 附在訊息後面，不用 `prompt.compose` 改 system prompt**：Mac app 的 session 是 SDK 啟動的（`sdk-preset`），中途加進 system prompt 的段落模型讀不到，2026-10-26 在 Mac app 實測過。附在訊息後面每輪都生效、對話壓縮後也還在，也不會打掉前面的 prompt cache。
- **規則不會跟到 subagent**：subagent 的 prompt 不走 `prompt.submit`，派出去做單一任務的 agent 照派工 prompt 做（實測過）。
- **slash command 不附規則**：避免 `/tempo off` 那一輪還帶著 autonomous 的規則。
- 切換當下另外用 `$.session.append` 留一句給模型，進行中的對話馬上知道節奏換了。

## 開發

```bash
claude plugin validate claude/mods/tempo
claude plugin test claude/mods/tempo
```

型別檢查要等 Claude Code 載入過一次 mod、生成 `.claude-plugin/types/` 之後，跑 `tsc -p claude/mods/tempo`。
