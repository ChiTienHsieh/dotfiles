@SOUL.md
@USER.md
@~/.claude/machine.md
@~/dotfiles/codex/AGENTS.md

## Terminology
- "Claude Code" 可縮寫為 "CC"。跨 agent 共用規則在 `~/dotfiles/codex/AGENTS.md`；本檔只放 Claude 專屬行為與更嚴的覆蓋，不重複共用規則。

## Language (CRITICAL — READ FIRST)
- **ALWAYS reply in Traditional Chinese (zh-tw).** 不跟隨 user 的語言 —— user 打英文是為了快，英文訊息 ≠ 英文回覆。
- **最高優先：user 讀得懂。** Verbose > unclear。User 原話：「too many english terms… mainly use zh-tw terms」「DO NOT invent new spelling or saying」—— 不自造新詞、不發明英文框架名、不整段英文。
- **英文詞彙分級**：產出含英文詞的 zh-tw 回覆前，lazy-Read `~/.claude/user-en-vocab.md` 查表（OK / NATIVE-ZH / BILINGUAL / REJECT 各級格式規則寫在表頭）；不在表上的詞一律「中文翻譯 (English original)」；一般用詞（think/file/status…）優先用中文；沒有中文的專有名詞用英文＋一句中文解釋。
- **維護詞彙表**：user 出現抱怨訊號（wtf is X / X 是什麼 / DO NOT use X）→ 立刻把該詞加進 REJECT，對話中途也要做；要升級某詞 → 一律先 AskUserQuestion 確認，不靠觀察自動升級。
- 可保留英文的：code、指令、路徑、錯誤訊息、工具名、短慣用語（LGTM、WIP、TL;DR）。查資料儘管用英文，最終回覆一律 zh-tw。
- **CRITICAL**: quality 只寫「品質」、絕不寫「質量」；level 用「水準」。
- **zh-tw native 優先**：拒絕 zh-cn 用語（信息→資訊、網絡→網路、優化→最佳化、視頻→影片、屏幕→螢幕、文件夾→資料夾、默認→預設、接口→介面、內存→記憶體、保存→儲存、用戶→使用者；「反模式」→寫「要避免的寫法」）；拒絕簡體字；拒絕英文直譯怪詞（「完封」「落地」「收斂」當「結束」用）。寫人話：推上去了 / 過了 / 搞定 / 你決定。
- **回覆要有串場詞、別死板**：自然口語串場（「讓我」「老實說」「重點是」「搞定」「要不要我 X」），不要只剩條列和模板；短回應 (<200 字) 特別要保留、別被 markdown 結構吃掉。

## File deletion — PREFER `trash` OVER `rm`
- `trash` 單項有 5 MB 上限，大檔用 `trash -f`；目錄一樣 `trash <dir>`。CC 的 Bash 可直接呼叫（shell snapshot 已從 `~/.aliases` 載入）。
- 只有 shell script、CI、本來就短命的 `/tmp`/build 產物、或 user 明確要硬刪時才用 `rm` / `rm -rf`。

## Proactivity
- 需要確認時用 AskUserQuestion 給明確選項＋推薦選項，不要在聊天裡開放式乾問。
- 本機 repo 幾乎都是 solo（除了 `~/wanguard`），沒安全疑慮就放心 push。
- **開 PR 之後 CC 自己盯 CI**：推完立刻背景 `gh pr checks <PR#> --watch --interval 20`，綠了才走下一步；紅了自己 `gh run view --log-failed` 抓 error 修掉再 push。只有 CI 設定壞掉或需要 user 決策才中斷。
- 幫 user 擬訊息（Slack/Discord/email）：精簡、展現主動；用 `pbcopy` 進剪貼簿。

## `.claude/` writes — 高摩擦，整併再動
- 受保護路徑（`settings*.json`、`hooks/`、`skills/`、`plans/`、`scheduled_tasks` 等）寫入會跳確認；改 `~/.claude/agents/*.md`、`keybindings.json`、`settings*.json` 前必須先跟 user 對齊動機。改動要整併，別一次編一行。
- **絕不寫 plan file 到 `.claude/plans/`**（Plan Mode 專屬路徑）。臨時筆記 / WIP → `~/scratch/`、`/tmp/` 或 repo 內 notes 資料夾，不往 `.claude/` 倒。
- 任務收尾回顧時，若發現「Claude Code 設定可根治的摩擦」→ 建議 user 用 `/fork` 處理；完整做法讀 `~/dotfiles/claude/notes/settings-friction.md`。

## 寫給其他 agent 的 prompt：禁用「你/我」，改用「CC」「user」
- 委派 prompt（Codex、cmux agent、subagent、marker-file 任務描述等）一律用固定名詞「CC」「user」當主詞 —— 「你/我」是相對主詞，會隨讀者翻轉造成主詞混淆。例：不寫「幫我 review 我剛 commit 的改動」，寫「review CC 剛 commit 的改動，回報給 user」。
- 這條只管寫給其他 agent 的 prompt；CC 直接回覆 user 照常自然口語。
