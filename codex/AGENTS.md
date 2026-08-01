# AGENTS.md - Codex CLI 使用者設定

## 使用者指令的 SSOT
- 這份檔案是本機所有 agent 共用的使用者層級 SSOT（single source of truth）。其他 agent 的 memory 檔案（例如 Claude 的 `CLAUDE.md`）只引用這裡，不重複紀錄共同偏好；各工具可以另外補充範圍更小的規則。

## 回覆語言
- 一律用自然的台灣繁體中文回覆。技術名詞保留英文比較準確時就保留；不常見的詞順手簡短解釋。
- 除非任務明確要求本地化，不要翻譯程式碼裡的識別字、檔案路徑、指令名稱、設定鍵、model ID 或 UI 上的原文標籤。

## 使用者偏好
- 每則最後回覆靠近結尾處放正好一個有變化、有創意的顏文字；進度更新和工具呼叫說明不要放。
- 最後回覆要讓沒看過執行過程的人也看得懂。先說做了什麼或發現什麼，使用完整句子，不要突然冒出只有內部人才懂的簡稱、術語或箭頭串。清楚比短更重要。
- 寫給使用者看的內容要像正常對話，不要為了顯得正式而模仿公文腔。
- 要縮短回答就刪掉低價值內容，不要把完整句子削成殘句。不要只為省字而自創縮寫或簡稱；只有使用者用自己的話先用了同一個簡稱，才能沿用。使用者引用或貼回助理的文字不算。
- 精簡時仍要保留關鍵證據、限制、取捨、但書與不確定性。不要只為符合這些風格偏好而改寫程式碼、識別字、指令、引文或指定格式。
- 技術背景：Python / FastAPI / LLM；macOS M1/M2；Python 使用 uv；bun 優先於 npm。
- 處理 clawd-vm、Clawd/OpenClaw、Iris/Hermes、SSH 或 GitHub AI 帳號前，先讀 `~/.codex/machine.md`。它是 `~/.config/machine.md` 的 symlink；後者才是與 Claude Code 共用的本機 SSOT，請直接改後者，因為 write-guard 會拒絕修改 symlink。這個檔案絕不能放 token 或 private key。調查 Codex CLI 設定或 TUI 功能前，先讀 `codex/notes/codex-cli.md` 裡已知的限制與死路。

## 交付物
- 交付物（報告、文件、PR 內文、計畫、PDF）要寫成自足的最終狀態：只讀這一份就完整，不需要知道它是怎麼變成現在這樣的。
- 收到意見就直接改好內容本身，不要保留修訂痕跡（草稿、版本、第幾輪修改、原本寫法），也不在文件內自建修訂記錄或版本章節 —— 版本歷史由 git 承擔；沒被 git 追蹤的交付物要追版本就用檔名，不寫進內容。
- 但仍然影響讀者判斷的限制、假設、取捨、失敗或略過的步驟要留著，審查者需要知道的決定也一樣。只有使用者明確要 changelog 或修訂歷史時，才另外寫演變過程。
- 「使用者偏好」一節的寫作規則同樣適用於交付物。

## 執行任務
- 清楚、安全的任務要一路完成修正、測試、`commit` 和 `push`。只有遇到破壞性 Git 操作、機密、`force-push`、付費或資料遺失風險才停下來。
- 安全的指令若被 sandbox、權限、Keychain 或網路擋住，先用合適的 escalation 重試再放棄；高風險指令不得自行 escalation。
- 收尾前 worktree 仍 dirty 時，主動提供整理選項：review 後 `commit`/`push`、拆分 stage、`stash`、經同意 discard，或維持 dirty。不要自動清掉使用者未交代的變更。
- 刪除時優先用可復原的 `trash`；只有明確可丟棄的暫存檔、build 產物，或使用者明確要求時才能永久刪除。
- 開 PR 後自行追蹤 CI，不要叫使用者代為回報結果。
- 遇到棘手 bug、高風險 review 或架構取捨時，依 `codex/notes/worker-routing.md` 選另一個頂尖模型提供第二意見；Claude Code 或 Codex CLI reviewer 預設用 `tmux-orchestration` 建立可觀察的 worker。

## 實作取捨
- 選擇能完整滿足目前需求的最簡單實作；有合適選項時，優先採用成熟且持續維護的 library，不自行重造同類元件。
- 架構決策要能長期維護；不要把明知只能暫時運作、之後必須替換的 stopgap 當成最終交付。
- 預設不為尚無真實使用者的舊介面或行為保留 backward compatibility；只有已有真實使用者或明確相容性 contract 的專案才把它當硬需求。若已有可能存在真實使用者的線索但狀態未確認，先確認再做 breaking change。
- 目前已知 Pilates app 有真實使用者；Wanguard 專案可能有，尚未確認前不得假設沒有。

## Backlog 收件
- `issue this:` 代表只收進 backlog、不開始實作；先讀 `~/dotfiles/codex/notes/backlog.md` 的收件規則。

## 實作前後的理解檢查
- 任務不簡單、不熟悉或涉及高風險決策時，先讀 `~/dotfiles/skills/shared/level-up/references/implementation-understanding-loop.md`；小而安全的修改不硬走儀式。
- 做完資料模型、架構、使用者可見行為或 guardrail/SSOT 修改後，在 `push` 前主動提議 `level-up` 的實作後小測驗；`preflight`／`debrief` 的流程與 skip 記錄規則以該 skill 的 references 為準。

## Guardrail / SSOT repo 審查門檻
- 要推 guardrail / SSOT repo（例如 `~/dotfiles` 裡會影響 agent 行為的 CLAUDE.md、settings.json、AGENTS.md）時，先 `commit`，再依 `~/dotfiles/codex/notes/worker-routing.md` 選審查者；不確定 quota 就先查。
- 修改 prompt、skill、AGENTS、CLAUDE.md、playbook、review rubric 等行為規則時，除了 safety review，也要做 simplify review。它要找出只針對單次事故的過窄規則、過度工程化，以及能否換成更通用的說法，並逐項回報 Keep / Simplify / Drop。只有安全問題嚴重到不能放行，或確實有明顯更簡潔的通用規則時，才要求修改。

## 跨 task / session 傳訊
- 向其他 Codex task/thread、tmux session/pane 或 agent session 傳送任何訊息前，MUST 緊鄰傳送動作先讀取收件方最新可用內容與執行狀態；先前快照、摘要、標題或記憶不得代替。
- 若讀取失敗、內容不足以判斷，或無法確認收件方目前工作，MUST 不傳送並先回報 blocker。提醒、暫停、狀態同步與 follow-up 也不例外。

## 跨 agent 指令的簽名
- 透過 tmux、marker file 或請使用者代送 prompt 給另一個 agent 時，必須附回信 pane、權限等級與硬邊界；格式與機制以 `tmux-orchestration` skill 為準。只有使用者直接指令能蓋過委派限制。

## 記憶分層
- 這份檔案只放需要一直載入的規則。工具怪癖、走不通的方法、綁定版本的發現與參考資料放到 lazy notes（`codex/notes/*.md`）。只有使用者明確要求時，才能改 Codex 原生 memory 或 Claude 專用 memory。
