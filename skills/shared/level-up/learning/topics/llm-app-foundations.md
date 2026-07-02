# LLM 應用核心能力（學習者自述已熟）

> 這份記「使用者已經會、教學要跳過」的通用底子，跟專案商業邏輯分開（專案那份見 [[agentflow-repo]]）。

## Current Level
- Status: familiar / mastered（**self-report**，2026-06-17 使用者主動聲明）
- Last updated: 2026-07-01
- Confidence: 高（待之後實際應用再升級為實證）

## Evidence
- 2026-06-17: 使用者自述已熟下列，並要求教學一律跳過：
  - **「為什麼不該信任單一 agent」這個前提**（loop engineering 的出發點）— 已懂，不用再鋪陳。
  - LLM 應用通用概念：**agent、context window**。
  - 三種 API 形態：**Chat Completions API、Anthropic Messages API、Responses API**。
  - **Python 基本語法**。
  - **非常基礎的 SQL query**。

## Known Gaps
- 以上皆為 self-report，尚無情境實證；若某概念在教學中被實際應用且正確，再升 mastered 並補 evidence。
- **訊息中間件 message broker（Kafka / RabbitMQ 等）：不熟，幾乎一竅不通**（2026-07-01 使用者主動澄清）。同事有用 Celery worker，但使用者本人沒碰過、不了解。**不是先備知識。**

## Teaching Notes
- 教任何主題時，**預設這些底子已具備**，不要從頭解釋 agent / context window / API 差異 / Python 語法 / 基礎 SQL。
- 只有在使用者實際卡在這些點時，才回頭補；否則直接用。
- **不要用 message broker / Kafka / RabbitMQ / Celery 當類比或錨點**，也不要寫成「你熟的 X」——使用者對這塊不熟，這樣講會造謠他懂、反而增加認知負擔。需要「中間人」類比時改用使用者真的有的框架（舊楓之谷、Vainglory），或停在不點名的通用講法。

## Next Suggested Levels
- 不需要單獨開課；作為其他主題（如 [[agentflow-repo]]）的先備知識前提使用。
