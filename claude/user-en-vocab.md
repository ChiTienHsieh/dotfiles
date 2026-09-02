<!-- md-zh-tw: ignore -->
# User 英文詞彙表

CC 產出含非程式碼英文詞的 zh-tw 回覆前查這張表。
被 user 抱怨看不懂（wtf is X / X 是什麼）→ 立刻把該詞加進 REJECT。
想升級某詞（REJECT→BILINGUAL→OK）→ 一律先問 user 確認。

## 使用規則

- 不在表上的詞：一般用詞優先用中文；沒有自然中文的專有名詞用英文並順手簡短解釋。
- Code、指令、路徑、錯誤訊息、工具名與 UI 原文標籤不受本表限制。
- `quality` 只寫「品質」，不用「質量」；`level` 用「水準」。
- 避免中國用語：信息→資訊、網絡→網路、優化→最佳化、視頻→影片、屏幕→螢幕、文件夾→資料夾、默認→預設、接口→介面、內存→記憶體、保存→儲存、用戶→使用者。
- 避免英文直譯怪詞：「反模式」寫「要避免的寫法」；「完封」、「落地」、「收斂」不要拿來表示完成。

## OK（直接用，不用解釋）

- commit, push, PR, repo, branch, merge
- skill, agent, prompt, token, quota
- LGTM, WIP, TL;DR
- API, CLI, JSON, HTML
- orchestration

## NATIVE-ZH（有道地中文，直接用中文）

- flame graph → 火焰圖
- dependency → 依賴
- performance → 效能
- database → 資料庫

## BILINGUAL（session 首次「中文 (English)」，之後可英文）

- sandbox（沙盒）
- symlink（符號連結）
- frontmatter（檔頭設定）
- refactor（重構）

## REJECT（每次都要「中文翻譯 (English original)」）

| 詞 | Format |
| --- | --- |
| observability | 可觀測性 (observability) |
| idempotent | 重跑安全 (idempotent) |
| custody | 保管／託管 (custody) ｜金融語意＝資產由保管機構代管，非「看管人質」 |
