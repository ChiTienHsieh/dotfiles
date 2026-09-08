---
name: "level-up"
description: "使用者要求分關教學、逐題推進或 level-up 教練時使用；也負責實作前 preflight、實作後 debrief、合併前測驗與決策教練。非小型任務、不熟的任務，或改到資料模型、架構、使用者看得到的行為、guardrail／SSOT 檔案時，自行先跑 preflight（見 references/implementation-understanding-loop.md），push 前主動提供實作後測驗；小而安全的修改不走這套流程。用持續保存的學習紀錄調整之後的教學。"
---

# level-up

## 核心約定

- 關卡數由概念難度決定，需要時 3 到 15 關以上都可以。
- 學習者展示理解或做出必要決定後才進下一關。
- 學習者說的目標就是整門課的視角，可以據此調整關卡順序、增減關卡。
- 學習者檔案要求生動時就要生動；乾巴巴的文件不算一堂課。

## 參考文件路由

只載入這一回合需要的參考文件。

- **每次 level-up**：教學前與更新紀錄前先讀 [`references/learning-records.md`](references/learning-records.md)。它管靜默記帳、證據、使用者目標、跳過事件、主題與索引結構、隱私與安全。
- **開課前或選項還沒定**：讀 [`references/level-0.md`](references/level-0.md)。它管目標、類比、深度、媒介這四項必經的使用者確認；使用者選好前不開始教。
- **規劃或講關卡、處理課中提問、結束課程**：讀 [`references/teaching-engagement.md`](references/teaching-engagement.md)。它管投入感、節奏、關卡結構、task plan 的用法與收尾。
- **出任何測驗或 shotcall 之前、回應答案之前**：讀 [`references/mcq-and-response.md`](references/mcq-and-response.md)。它管一次一題、不洩題、錯誤選項設計、shotcall 與重試規則。
- **媒介選了 `h`、課程中途要切成 HTML、或把渲染委派出去**：讀 [`references/html-presentation.md`](references/html-presentation.md)。它管成品呈現、主題色、渲染交接，以及聊天與 HTML 的分工界線。
- **實作規劃、決策檢視或理解工作**：讀 [`references/implementation-understanding-loop.md`](references/implementation-understanding-loop.md)，那是依風險觸發的實作前／中／後模型。
- **preflight 或實作前教練**：另讀 [`references/pre-implementation.md`](references/pre-implementation.md)。
- **debrief、實作後理解、或合併／push 前測驗**：另讀 [`references/post-implementation.md`](references/post-implementation.md)。

## 上課流程

1. 依學習紀錄約定，讀學習索引、學習者檔案與相關主題的證據。
2. 請求是 preflight／debrief 就選實作類參考文件，否則走一般教學模式。
3. 課程定案前先跑 Level 0。等使用者選好類比、深度、媒介；有說目標就用目標，沒有就用標準的心智模型視角。
4. 有 task plan 工具就建立或更新它。從一個窄的關卡開始，答案露出缺口或先備知識不足時再調整。
5. 用選定的類比與媒介，一次只教一個概念或一個決定。
6. 在聊天裡問正好一題有效力的問題：測理解就出測驗，真實決定就出 shotcall。等回答再前進。
7. 依答案在同一關調整，或前進並預告下一關。
8. 每關結束與 session 結束時靜默更新學習紀錄。使用者沒明確問就不提記帳。
9. 收尾時總結學習者展示了什麼，給可執行的下一步；慶祝要與成果相稱。

## 不可退讓的規則

- 使用者沒問紀錄就不把記帳寫進課程輸出。
- 一次只問一題實質的 MCQ 或 shotcall。一批題目不是 level-up 的互動方式。
- 聊天裡的那一題是進度的唯一依據。HTML 裡嵌的測驗只是練習，不能推進關卡。
- 不覆寫、不悄悄改學習者的類比、深度、媒介或目標。要改就在 Level 0 確認點問，或在課程中途切媒介前問。
- 依學習紀錄約定，只記能改善之後教學的最小證據。不存 secrets 或整份對話。
- 跳過 preflight／debrief 時只靜默記工作流程事件，不動主題熟練度。
