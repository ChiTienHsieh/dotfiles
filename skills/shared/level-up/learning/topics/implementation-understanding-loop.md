# Implementation Understanding Loop（preflight/debrief）＋ send-prompt guard 決策

## Learner Goal
- Dogfood 驗證 debrief mode 本身，同時真的理解今晚 shipped 的 guardrail 改動（fcee578..faf6209）。

## Status
- mastered（debrief 5/5 + preflight 盲測 2/2，含近身 distractor）。

## 已掌握（概念）
- risk-triggered 觸發判斷：機械大改不觸發、guardrail/user-facing/API contract 改動觸發（「危險看決策、不看 diff 大小」；五十檔機械 rename 不觸發）。
- during notes 原則：能辨識「自行拍板的保守假設」是最該記的，流水帳/打勾留痕是噪音。
- quiz gate 規範 vs hook：機器判不出需不需要考、user 是否真懂 → 觸發線劃在「提議」（提議便宜、skip 權在 user）。自己超前推導出這點。
- threat model：區分 defer（backlog）vs non-goal（明文拒絕擴充）；`cat <<EOF | bash` 繞過是接受的非目標。heredoc 判準看收件人（資料匯 vs 執行器），不看內容長相。
- 未知四象限：「未知的已知」＝沒說出口的理所當然是 agent 翻車熱區。
- 展現把規則邊界推回教學者的能力（主動反駁 L1 笑點選項：乘客滿意度其實是 user-facing）。

## 決策確認
- 七項決策（重量分配、鉤子＋手冊分層、風險觸發＋排除、notes 寫既有載體、quiz 主動提議＋skip 留痕、preflight/debrief 呼號、references 分章）與實際 shipped 全部吻合。其中「三段重量 pre 重／post 次／during 輕」是 shipped 版未明文的隱性取捨，preflight 把它顯式化。

## Teaching Notes
- 航空外殼（機長/黑盒子/塔台/水泥牆/起落架警報器）扛住五個概念，效果好，可續用。
- **重要品味訊號：user 明確糾正「一次倒完的高密度 debrief 報告太無聊」→ debrief 報告必須拆成多個可消化的 level，一關一決策＋MCQ，不可先一大篇報告再考試。**

## Next Suggested Levels
- 下一步：在「決策真的未知」的新任務上跑 preflight（先前盲測匹配度受污染：pre references 本身就是 shipped 產物）。
- 若 post-implementation.md 規格更新為 level-split 報告，可回頭驗證新流程。
