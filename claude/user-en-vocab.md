<!-- md-zh-tw: ignore -->
# User 英文詞彙表

CC 產出含英文詞的 zh-tw 回覆前查這張表；分級規則見 `~/.claude/CLAUDE.md` 的 Language 節。
被 user 抱怨看不懂（wtf is X / X 是什麼）→ 立刻把該詞加進 REJECT。
想升級某詞（REJECT→BILINGUAL→OK）→ 一律先用 AskUserQuestion 確認。

## OK（直接用，不用解釋）

- commit, push, PR, repo, branch, merge
- skill, agent, prompt, token, quota
- LGTM, WIP, TL;DR
- API, CLI, JSON, HTML

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
| orchestration | 多代理協調 (orchestration) |
| observability | 可觀測性 (observability) |
| idempotent | 重跑安全 (idempotent) |
