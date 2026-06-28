# tmux

## Learner Goal
- Sprin 想實際會用 tmux 來跑 Claude Code / 長任務：左右分割同時看對話與 log、SSH 斷線也不怕。偏實戰、能遷移到日常工作流。

## Current Level
- Status: tmux 全條 mastered（L2 pane/window/session、L3 持續性、L4 多 session/nested、L5 % 切 pane、L6 pane 間移動/關閉）。整條目標鏈打通。剩實機養肌肉記憶。
- Last updated: 2026-06-27
- Confidence: 高，全程靠推理答對、還抓出教學者兩個流程錯誤

## Analogy (鎖定，不要換)
- 舊楓之谷（Big Bang 改版前）城鎮框架：
  - tmux server＝世界伺服器
  - session＝一座城鎮
  - window＝城鎮裡的一張地圖（佔滿整個畫面，靠 prefix → n/p/數字/c 傳送）
  - pane＝把一張地圖切成並排好幾格（同畫面同時看到多個 shell）

## Evidence
- 2026-06-27: L2 答對 B——分辨「要同時看到就用 pane」，且知道 window/session 一次只看得到一個、Ghostty 分頁與 tmux 無關。pane vs window vs session 顆粒度 mastered。
- 2026-06-27: L3 持續性——Sprin 自己正確複述「先 SSH 再 tmux，client+server 都活在伺服器上，斷線/ detach 後城鎮照跑、attach 接回同一座」。持續性心智模型 mastered。
- 2026-06-27: window 切換 gap 浮現——Sprin 試 Ctrl-b w 進到「怪面板」（其實是 tree 總覽選單，非壞掉）。已教 prefix n/p/數字/c，並把 prefix w 定位成「地圖總覽選單」。記法 n=next/p=prev/數字=傳送門編號。
- 2026-06-27: L3 加深——面對「關 SSH build 還會跑嗎」回「A or B both work」。正確且超前：抓到 A(主動 detach) 與 B(SSH 硬斷) 結果相同，因為持續性來自遠端 server 而非 detach 動作本身。能分辨「優雅登出 vs 拔網路線」差別。持續性顆粒度真的 mastered，不是背答案。
- 2026-06-27: L4 選 B（陷阱）後，主動追問「已在 session 內 attach 別座會怎樣」「-t 是不是 tag」「ls vs list-sessions 差別」。已澄清：-t=target 非 tag；ls=list-sessions 別名；prefix n 跨不過 session；跨城用 attach -t 名字或 prefix s。多 session 顆粒度修正中→clicked。
- 2026-06-27: 教城中城 nested session（$TMUX 章 → attach 被擋、改用 switch-client / prefix s）。Sprin 吃進去並表示「具體城名比抽象 city A/B 有感」。進 L5（pane 切割鍵 % 左右 / " 上下）。
- 2026-06-27: L5 答對 B（% = 左右 pane）。主動追問 horizontal/vertical 命名，已拆 tmux `-h` 旗標與直覺相反的坑，定錨「別記方向詞、記畫面+鍵：% 左右、" 上下」。
- 2026-06-27: L6 答對——自己猜出 prefix o（other）與 prefix 方向鍵兩種 pane 移動法。補關閉 pane（exit / Ctrl-d / prefix x）。tmux 結業。

## Known Gaps
- pane 切換/分割鍵（prefix % 左右、prefix " 上下、prefix 方向鍵移動）L5 進行中，尚未實機操作驗證。

## Engagement Notes
- 用具體 MapleStory 城名（墮落城市/魔法森林）比抽象 city A/B 更好記、Sprin 自述更有感（"very nerdy lol"）。一路沿用。

## Teaching Notes
- 純文字環境（手機 Telegram）：不產 HTML、不給檔案路徑，課程直接打在對話。短段落、MCQ 一行一個。
- 類比承載知識，技術名詞只放一行 anchor。
- MCQ 防 tell：正解位置分散（L2 用過 B，下一關避開 B）、選項長度相近、放一個搞笑選項。
- **兩條 channel 嚴格分開（2026-06-27 踩雷）**：(a) 更新 learning 紀錄＝無聲副作用，永遠不送聊天室；(b) 聊天室只放「課程內容＋MCQ」。絕對不要把「更新了哪些檔 / 檔案路徑 / Known Gaps / 等你回 LX / [claude-cli/...] 模型標籤 / 『紀錄更新好了』」這類內部記帳貼給學習者。Sprin 明確點名要所有 clawd 不再犯。

## Next Suggested Levels
- L3: detach/attach + session 持續性（SSH 斷線任務照跑）。
- L4: prefix key（Ctrl-b）是什麼、為什麼所有指令都要先按它。
- L5: 實際操作——建 session、切 window、切 pane 的鍵。
