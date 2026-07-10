# MonitorControl 亮度控制

## Learner Goal
- 搞懂每個 MonitorControl toggle 的作用，深到能自己推理 DDC、軟體調光、亮度同步、USB-C / DP Alt Mode 喚醒問題，並安全實驗。

## Status
- learning，confidence medium。

## 真正目標（operational）
- 外接螢幕的硬體最低亮度太亮；overnight 跑 Codex/Claude goal 時要顯示器近乎零亮度、但機器保持運轉。
- **想要的設定：smooth on、combine on、sync off、zero on，配上 risk control。**

## 已掌握（概念）
- DDC（Display Data Channel）= 螢幕原生硬體支援的控制通道；但「有支援」不保證傳輸穩定。
- MonitorControl 顯示 XB323QK NV 為 Hardware (DDC)，該螢幕支援 DDC 硬體亮度控制。
- 黑屏風險最小化的設定方向已能推理。

## Known Gaps
- 還缺一個清楚的心智模型分辨：硬體亮度控制 vs 軟體調光 vs 亮度同步的差別。

## Teaching Notes
- 用舊楓之谷（Big Bang 改版前）衝卷軸類比。
- 縮寫首次出現要展開全名，尤其 Display Data Channel (DDC) —— user 明確要求不要背縮寫。
- 別只丟一串 toggle 清單、要配 risk model。

## Next Suggested Levels
- 三種亮度控制層。
- Display Data Channel (DDC) 與為何硬體控制會不穩。
- MonitorControl General toggles。
- 安全使用 combine 調光 + zero 亮度做 overnight run。
- Per-display toggles。
- USB-C / DP Alt Mode / 喚醒與韌體怪癖。
- 安全實驗與救援流程。
