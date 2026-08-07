# Pilates 薪資頁 release readiness

## Learner Goal
- 判斷 PR #30 產品上實際交付什麼，以及它要滿足哪些條件才稱得上可上線的好 release。

## Current Level
- Status: completed
- Last updated: 2026-08-08
- Confidence: 四項產品與 release 決策已由 PR、main CI、exact-source Sites deployment 與 production health checks 驗證。

## Evidence
- 2026-08-07：選擇 Vainglory 類比、深度 2、Chat Markdown。
- 2026-08-07：拍板 PR #30 定位為薪資第一階段；交付 Vita／BM 每月預排堂數與明細，金額明確標示尚未計算。
- 2026-08-07：拍板堂數口徑為整月所有未取消的預排課，包含未來課與待補學生；不代表已完課或可領薪堂數。
- 2026-08-07：拍板保留「薪資」長期入口，但主卡先突出本月預排堂數；薪資金額降為待設定提示，移除每堂破折號金額。
- 2026-08-08：拍板走完整 release train；以 lease 保護更新 rebase 後 branch，PR 與 main CI 雙層通過後才部署 exact merged source，並完成 production 驗證與 branch cleanup。
- 2026-08-08：PR #30 與 main 的 Quality gates、WebKit、GitGuardian 全數通過；merged commit `7034973` 已部署為 Sites version 39，登入導向、匿名 API 401、crawler 阻擋與 runtime logs 驗證正常，短期 branch 已安全清理。

## Known Gaps
- 薪資金額仍刻意不在本次範圍內，待提供正式計算規則後再設計。

## Teaching Notes
- Decisions-first，一次一關一題；產品價值先於 Git／部署 mechanics。
- 用 Vainglory objective call 承載整段課程，不混搭其他遊戲世界。

## Next Suggested Levels
- 下一階段可從 Vita／BM 的正式薪資公式、例外規則與可稽核明細開始。
