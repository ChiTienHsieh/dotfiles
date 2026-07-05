# Implementation Understanding Loop（preflight/debrief）＋ send-prompt guard 決策

## Learner Goal
- Dogfood 驗證 debrief mode 本身，同時真的理解今晚 shipped 的 guardrail 改動（fcee578..faf6209）。

## Current Level
- Status: mastered
- Last updated: 2026-07-05
- Confidence: high（5/5 MCQ 全對，含近身 distractor）

## Evidence
- 2026-07-05: 航空框架 debrief，5 levels 全對：
  - risk-triggered 觸發判斷（機械大改不觸發、guardrail/user-facing 觸發）。
  - during notes 原則：能辨識「自行拍板的保守假設」是最該記的，流水帳/打勾留痕是噪音。
  - quiz gate 規範 vs hook：答對「機器判不出需不需要考、user 是否真懂」，且在 L1 就自己先推導出「提議便宜、skip 權在 user，所以觸發線劃在提議」—— 超前理解。
  - threat model：能區分 defer（backlog）vs non-goal（明文拒絕擴充），知道 `cat <<EOF | bash` 繞過是接受的非目標。
  - heredoc 判準：看收件人（資料匯 vs 執行器），不看內容長相。
- 2026-07-05: 對 L1 笑點選項主動反駁「乘客滿意度其實是 user-facing、該提議 debrief」—— 展現把規則邊界推回教學者的能力。

## Known Gaps
- 無（本主題）。

## Teaching Notes
- 航空外殼（機長/黑盒子/塔台/水泥牆/起落架警報器）全程扛住五個概念，效果好，可續用於 implementation modes。
- **重要品味訊號：user 明確糾正「一次倒完的高密度 debrief 報告太無聊」—— debrief 報告必須拆成多個可消化的 level，一關一決策＋MCQ，不可先一大篇報告再考試。**

## Next Suggested Levels
- preflight mode 的實戰 dogfood（pre-implementation 尚未跑過真任務）。
- 若 post-implementation.md 規格更新為 level-split 報告，可回頭驗證新流程。
