# Codex Thread Title Hook Preflight

## Learner Goal
- 每次 Codex 真正完成一個 task 後，自動把目前 thread 改成能精準描述成果的標題；不能因完成 hook 再觸發自己而無限續跑。

## Current Level
- Status: familiar
- Last updated: 2026-08-05
- Confidence: preflight 產品與架構決策已落地，unit 與 trusted standalone CLI end-to-end 驗證通過

## Evidence
- 2026-08-05: 選擇航空塔台類比、深度 2（紮實打底）、Chat Markdown；成功標準是每次完成 task 都自動改成精準標題。
- 2026-08-05: 指出官方欄位 `stop_hook_active` 對人與 model 都不直覺；拍板只在 wire adapter 邊界讀取，內部改用能直接表達語意的名稱，model-facing prompt 不暴露原始欄位名。
- 2026-08-05: 拍板每條 Stop continuation chain 只做一次語意檢查，確認 task 完成才改名；追問並釐清此方案預設是同一個 active model 執行兩次，不是兩個不同 model。
- 2026-08-05: 拍板由同一個 active model 在短 continuation 中判斷狀態並呼叫改名工具，不另啟第二個命名 model。
- 2026-08-05: 提出 title 必須是精簡繁中，包含使用者目的、所在範圍、進度及一個狀態 emoji；`📦` 只代表值得 archive，不授權 Codex archive。明確否定 agent stop、idle、final answer 或只有 local commit 足以判為 `📦`。
- 2026-08-05: 拍板 title 只在進入 `⏸️`、`⏳`、`🔎`、`📦` 這四種有意義的處置狀態時更新；普通 `Stop`、idle 或 agent 本來就該繼續工作時保持原 title。
- 2026-08-05: 拍板固定 title grammar 為 `emoji 在哪｜使用者目的｜進度`，優先讓同 repo／project 的 threads 在 sidebar 中可掃描分組。
- 2026-08-05: 拍板 emoji 依使用者下一個必要動作判定：外部前置條件需 user 解鎖為 `⏸️`、重要背景或取捨需理解為 `🔎`、只需簡單選擇為 `⏳`；全部未完成責任與重要學習都清空才可標 `📦`，否則 agent 應繼續工作或不改名。
- 2026-08-05: 拍板只使用 Codex 內建的一次性 Stop-chain guard；不新增 cooldown、lock file 或跨機器持久狀態。每個真實新 turn 可重新判斷，同一條 continuation chain 最多續跑一次。
- 2026-08-05: 拍板以單一 Stop dispatcher 組合 dirty-worktree 與 thread-title 兩套獨立 policy，輸出唯一一次 continuation，避免多個 matching Stop commands 並行產生競爭 prompt。
- 2026-08-05: 拍板 title 初版長度以 24–32 個字元為目標、40 為 hard cap；明確保留上線後依 sidebar 實際讀感迭代的空間。
- 2026-08-05: 拍板 capability-aware fail-open：rename capability 不存在時安靜跳過，工具存在但失敗時只顯示一次簡短警告；title failure 不得阻止 task 收尾、不得開第二條 retry continuation、不得觸發 archive。
- 2026-08-05: 實作時發現 model sandbox 不能讓 nested app-server 寫入 `~/.codex`；改由 model 寫入 private one-shot temp request，第二次 Stop 在 hook host 取走後套用。這是同一條 Stop chain 的暫態 handoff，不是 cooldown、lock 或跨 turn idempotency state。
- 2026-08-05: 完成 15 項 unit tests、global symlink、TUI `/hooks` trust，以及不帶 bypass flag 的 standalone `codex exec` end-to-end；確認只有一次 continuation，並從 persisted session index 讀回繁中三段式標題。

## Known Gaps
- 使用者不使用 IDE，因此只驗證 standalone CLI；Codex App 與 IDE surface 未納入本次範圍。
- `codex exec --json` 會留下 continuation 的空 assistant message event；互動 TUI 的實際可見讀感與同畫面即時重繪仍待日常使用觀察。

## Teaching Notes
- 使用航空塔台框架，一次一個 decision-focused shotcall。
- 可加速已掌握的 hook lifecycle 與 `stop_hook_active` 基礎，重點放在 completion semantics 與多個 Stop hook 的整合。

## Next Suggested Levels
- 依 sidebar 日常讀感迭代 24–32 字目標；需要時再跑實作後 debrief。
