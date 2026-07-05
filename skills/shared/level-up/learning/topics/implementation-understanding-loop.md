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
- 2026-07-05: preflight mode 首次盲測 dogfood（題目＝已 shipped 的 implementation modes 導入，coach 不看 git 歷史）。MCQ 2/2：未知四象限（正確辨識「未知的已知」＝沒說出口的理所當然是 agent 翻車熱區）、風險觸發判斷（API contract 改動觸發、五十檔機械 rename 不觸發 ——「危險看決策、不看 diff 大小」）。
- 2026-07-05: 七項決策確認（重量分配、鉤子＋手冊分層、風險觸發＋排除、notes 寫既有載體、quiz 主動提議＋skip 留痕、preflight/debrief 呼號、references 分章）與實際 shipped 決策全部吻合；其中「三段重量 pre 重／post 次／during 輕」是 shipped 版未明文的隱性取捨，preflight 把它顯式化。

## Known Gaps
- 無（本主題）。

## Teaching Notes
- 航空外殼（機長/黑盒子/塔台/水泥牆/起落架警報器）全程扛住五個概念，效果好，可續用於 implementation modes。
- **重要品味訊號：user 明確糾正「一次倒完的高密度 debrief 報告太無聊」—— debrief 報告必須拆成多個可消化的 level，一關一決策＋MCQ，不可先一大篇報告再考試。**

## Next Suggested Levels
- preflight 盲測已完成（2026-07-05）；下一步是在「決策真的未知」的新任務上跑 preflight（盲測的匹配度受污染：pre references 本身就是 shipped 產物，coach 必讀才能執行 mode）。
- 若 post-implementation.md 規格更新為 level-split 報告，可回頭驗證新流程。
