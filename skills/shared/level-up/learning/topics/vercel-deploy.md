# Vercel 部署（preview vs production / link / alias）

## Current Level
- Status: familiar→mastered（核心模型紮實）
- Last updated: 2026-06-25
- Confidence: 高（4/4 MCQ 答對，且主動用 ground truth 糾正教學者假設）

## 選定類比 / 深度
- 類比：舊楓之谷「凍結存檔 + 主城公告欄」。深度 A2（紮實打底）。
- 對應：每次 deploy = 不可改的凍結存檔（各有亂碼門牌）；對外網址 = 公告欄(alias)，只是指向某存檔的可移動指標；--prod/promote/alias = 搬公告欄；rollback = 指回舊存檔（秒回）。
- 此類比一路扛到底，效果好，下次續教沿用。

## Evidence
- 2026-06-25: L1 immutable deployment 答對 B（舊存檔凍結、改動進新代號網址）。
- 2026-06-25: L2 deploy≠alias 答對 B（preview 不搬公告欄，對外仍舊內容）。
- 2026-06-25: L3 答對 B（Vercel 推整個資料夾、大門認 index.html）；並**主動拿 ground truth 糾正 CC 的錯誤假設**：`.local/deploy/.vercel` 綁定的是 dedup-system-design，不是 dedup-brief。理解「綁定靠 projectId 不靠資料夾名」。
- 2026-06-25: L4 答對 B（rollback = promote 回還活著的舊存檔，秒完成，不必刪壞存檔）。

## Known Gaps
- 成本光譜（Vercel PaaS → AWS IaaS → 自建 DX → 自買機器）是延伸題，已點到：糾正其「自己蓋只付電費」的盲點（還有頻寬/硬體/on-call/地理分散），及「Vercel 最貴」其實是「小規模最便宜、大規模才變貴」。屬延伸，非核心。
- 尚未實作過真正的 preview deploy；停在概念層。

## Teaching Notes
- 用真實檔案教效果極佳：`.local/deploy/.vercel/project.json`、deploy 目錄 serve index.html。
- 此 user 會抓 fact drift，教學者勿假設目錄↔專案對應，先讀再講。
- 實務發現（與原 deploy 任務相關）：`.local` 樹下唯一 .vercel 綁定是 `deploy/`→dedup-system-design；`dedup-brief.html` 旁無 link，dedup-brief 專案的本機綁定不在此 repo。要推 dedup-brief 需先解決 link 來源。

## Next Suggested Levels
- L5（延伸）：custom domain vs 自動 *.vercel.app、team/scope、`vercel link`/`vercel pull` 重新綁定流程。
- L6（延伸）：成本 crossover —— 何時該從 PaaS 往 IaaS/自建爬，及各層真正扛的成本。
