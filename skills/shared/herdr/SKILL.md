---
name: herdr
description: "Operate and inspect terminal workspaces managed by Herdr. Use when the user explicitly invokes $herdr, says the current terminal is in Herdr, or asks to inspect or interact with a Herdr workspace, tab, pane, or agent."
---

# Herdr

把 Herdr 當成目前 terminal workspace 的 control plane。啟用這個 skill 只會改變 terminal routing；不會擴張使用者授權，也不會自動安裝 integration、建立 config 或遷移既有 workflow。

## 建立目前狀態

1. 先跑 `herdr status`，需要定位自己時再跑 `herdr pane current`。
2. 需要完整拓樸時只跑一次 `herdr api snapshot`；較小的問題優先用 `herdr workspace list`、`herdr pane list` 或 `herdr agent list`。
3. Herdr socket 若被 sandbox 擋住，對原本的 Herdr 指令要求 scoped escalation。不要因此改查 tmux。
4. 若 CLI 不存在、server 未執行或 socket 仍無法讀取，回報具體 blocker。除非使用者要求，否則不要自行安裝、啟動或修改 Herdr。

使用者明確說目前在 Herdr 或啟用 `$herdr` 時，不要先用環境變數猜測 multiplexer，也不要先查 tmux。只有使用者明確要求 tmux，或 fresh Herdr state 顯示指定工作確實由 tmux 管理時，才切換到 tmux workflow。

## 解析與讀取目標

- 把 workspace label、pane label、agent name 與精確 ID 分開處理。先 fresh-run list command，再從結構化輸出解析目標；不要假設名稱就是 ID。
- 人類提供的 pane 名稱（例如 `grok-gu-log`）先用 `herdr pane list` 找到 `pane_id`，再用 `herdr pane get ID` 或 `herdr pane read ID --source recent-unwrapped --lines N`。
- Agent 目標優先用 `herdr agent list` 定位，再用 `herdr agent get TARGET` 或 `herdr agent read TARGET --source recent-unwrapped --lines N`。
- `current`、`focused` 與使用者點名的 target 可能不同；除非任務真的問目前 pane，否則以使用者點名的 target 為準。
- 子命令或參數不確定時跑最窄的 `herdr <area> <command> --help`，不要憑記憶拼 CLI。

## 互動與傳訊

任何跨 pane 或跨 agent 訊息都遵守 fresh-read contract：

1. 緊鄰傳送前重新列出或取得目標，確認 ID、agent status 與 cwd。
2. 重新讀取目標最近輸出；舊 snapshot、摘要、label 或 task title 不能代替。
3. 內容不足、目標不唯一、讀取失敗，或無法判斷對方正在做什麼時，不傳送並回報 blocker。
4. 對已辨識 agent 優先使用 `herdr agent prompt TARGET TEXT`；需要等待時給明確 `--until` 與 `--timeout`，不要無限期阻塞。
5. 只有非 agent terminal 才用 `herdr pane send-text` / `send-keys`，並記住 `send-text` 不等於按 Enter。

傳送、focus、rename、split 等可逆操作仍須符合使用者任務範圍。Close、刪除 session/workspace 或其他難以復原的操作，先解析精確 target 並遵守一般 destructive-action 規則；不要關閉整個 Herdr server 來清理單一 pane。

## 邊界

- 不要因為 agent integration 顯示 `not installed` 就安裝它；一般 pane 操作不依賴 integration。
- 不要把 Herdr pane、Herdr agent、tmux pane 與 Codex subagent 視為同一種 execution surface。
- 不要把 skill 啟用視為「目前每個 pane 都不是 tmux」的證明；它只表示先從 Herdr 的 live state 開始查證。
