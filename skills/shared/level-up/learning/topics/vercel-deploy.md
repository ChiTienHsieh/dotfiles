# Vercel 部署（preview vs production / link / alias）

## Status
- familiar→mastered（核心模型紮實，4/4 MCQ，主動用 ground truth 糾正教學者假設）。

## Analogy / 深度
- 舊楓之谷「凍結存檔 + 主城公告欄」。每次 deploy=不可改的凍結存檔（各有亂碼門牌）；對外網址=公告欄(alias)只是可移動指標；--prod/promote/alias=搬公告欄；rollback=指回舊存檔（秒回）。效果好，續教沿用。

## 已掌握（概念）
- immutable deployment：舊存檔凍結、改動進新代號網址。
- deploy ≠ alias：preview 不搬公告欄，對外仍舊內容。
- Vercel 推整個資料夾、大門認 index.html。
- 綁定靠 projectId 不靠資料夾名（主動抓：`.local/deploy/.vercel` 綁的是 dedup-system-design，不是 dedup-brief）。
- rollback = promote 回還活著的舊存檔，秒完成，不必刪壞存檔。

## Known Gaps
- 成本光譜（Vercel PaaS → AWS IaaS → 自建 → 自買機器）是延伸題：已糾正「自己蓋只付電費」盲點（還有頻寬/硬體/on-call/地理分散）、「Vercel 最貴」其實是「小規模最便宜、大規模才變貴」。
- 尚未實作過真正的 preview deploy；停在概念層。

## Teaching Notes
- 用真實檔案教效果極佳：`.local/deploy/.vercel/project.json`、deploy 目錄 serve index.html。
- 此 user 會抓 fact drift，勿假設目錄↔專案對應，先讀再講。
- 實務發現：`.local` 樹下唯一 .vercel 綁定是 `deploy/`→dedup-system-design；要推 dedup-brief 需先解決 link 來源。

## Next Suggested Levels
- 延伸：custom domain vs 自動 *.vercel.app、`vercel link`/`vercel pull` 重新綁定。
- 延伸：成本 crossover —— 何時該從 PaaS 往 IaaS/自建爬。
