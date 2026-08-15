# Pilates D1 Backup Hardening Debrief

## Learner Goal
- 快速確認 production database backup 與 disaster recovery 方案沒有關鍵破口。

## Current Level
- Status: mastered
- Last updated: 2026-08-14
- Confidence: high

## Evidence
- 2026-08-13: 選擇三間保險庫搶劫片類比、紮實打底、Chat Markdown；尚待逐關驗證 failure domain、key recovery、alerting 與 restore readiness。
- 2026-08-13: 正確辨識同機 immutable snapshots 仍共享 VM failure domain，並主動提出由個人 Mac 定期 pull 作為獨立 offsite copy。
- 2026-08-14: Mac-pull offsite 已以真實排程、加密與 isolated recovery 驗收，且能指出 off-device key recovery 與 independent liveness alert 仍是 residual risks。
- 2026-08-14: age recovery identity 已建立經第二裝置確認的 cross-device recovery copy；備份與解密金鑰同機遺失的 blocker 已解除。

## Known Gaps
- 沒有已確認的理解或 recovery blocker；independent liveness alert 與專用 SSH key 是可選強化。

## Teaching Notes
- 三間保險庫類比被明確評為太難、太不自然；後續改用直接、口語、短回合的技術建議，不再硬套故事或考題。
- 聚焦現有實作證據與 residual risk，不考檔名或機械細節。

## Next Suggested Levels
- 視風險接受度再補 independent liveness alert 與專用 SSH key。
