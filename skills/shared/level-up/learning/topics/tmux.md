# tmux

## Learner Goal
- Sprin 想實際會用 tmux 跑 Claude Code / 長任務：左右分割同時看對話與 log、SSH 斷線也不怕。偏實戰、能遷移到日常工作流。
- （第二門課，桌機）搞懂 Ghostty 分頁 vs tmux window/session 分層，拍板「cmd+t 自動開新 tmux session」設定。
- （第三門課）能根據鼠標操作與選取／複製的取捨，判斷是否關閉 tmux mouse。

## Status
- mastered（pane/window/session、持續性、多 session/nested、pane 切割與移動全通）。整條目標鏈打通，全靠推理答對、還抓出教學者兩個流程錯。剩實機養肌肉記憶。
- 第二門課（A2, 2026-06-27~07-11）L1–L5 全通關：detach 持久邊界（機器斷電=死、視窗關=活）、pane=並排、Ghostty 分頁=client 側觀景窗 vs window/session=server 側本體、session-per-tab vs 一 session 多 window 取捨（SSH 遠端→後者）、resurrect 藍圖 vs 現場（L5 頁內測驗 4/4，含微世界實驗）。抓出教材 bug（├ 樹枝橫排 vs prefix+w 直式樹）＋MCQ 出題破綻（正解最長=送分）。
- 第三門課（A3m, 2026-09-01）已鎖定舊楓之谷、深挖細節與 Chat Markdown；目標是拍板是否關閉 tmux mouse。

## Analogy（鎖定，不要換）
- 舊楓之谷（Big Bang 改版前）城鎮框架：server=世界伺服器、session=一座城鎮、window=城鎮裡一張地圖（佔滿畫面）、pane=把地圖切成並排好幾格。

## 已掌握（概念）
- pane vs window vs session 顆粒度：要同時看到就用 pane；window/session 一次只看得到一個。
- 持續性：先 SSH 再 tmux，client+server 都活在遠端 server 上，斷線/detach 後城鎮照跑、attach 接回同一座。持續性來自遠端 server 而非 detach 動作本身（優雅登出 vs 拔網路線結果相同）。
- 多 session：-t=target 非 tag；ls=list-sessions 別名；prefix n 跨不過 session，跨城用 attach -t 名字或 prefix s；nested session（$TMUX）attach 被擋要用 switch-client。
- pane 操作：% 左右、" 上下（別記方向詞、記畫面+鍵，避開 tmux `-h` 直覺相反的坑）；prefix o / prefix 方向鍵移動；exit / Ctrl-d / prefix x 關閉。
- window 切換：prefix n/p/數字/c，prefix w 是「地圖總覽選單」。

## Known Gaps
- 尚未實機操作驗證（pane 切割/移動鍵靠推理答對，缺肌肉記憶）。
- ~~resurrect 藍圖 vs 現場~~ → L5 考過（4/4）。外掛已裝（TPM+resurrect+continuum 進 dotfiles tmux.conf）。
- Ghostty cmd+t 自動進 tmux 的 zshrc gate 已設計、待使用者拍板安裝範圍（Ghostty-only vs 所有終端機）。

## Engagement Notes
- 用具體 MapleStory 城名（墮落城市/魔法森林）比抽象 city A/B 更好記，Sprin 自述更有感（"very nerdy lol"）。一路沿用。

## Teaching Notes
- 純文字環境（手機 Telegram）：不產 HTML、不給檔案路徑，課程直接打在對話。短段落、MCQ 一行一個。
- 類比承載知識，技術名詞只放一行 anchor。
- MCQ 防 tell：正解位置分散、選項長度相近、放一個搞笑選項。
- **兩條 channel 嚴格分開**：(a) 更新 learning 紀錄＝無聲副作用，永遠不送聊天室；(b) 聊天室只放課程內容＋MCQ。不要把檔案路徑/Known Gaps/「紀錄更新好了」/模型標籤這類記帳貼給學習者。
