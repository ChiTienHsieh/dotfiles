---
name: html-artifacts
description: 做自包含的 HTML artifact：計畫、review、報告、研究整理、圖解、prototype、dashboard、自訂編輯器等工作產出，用在 Markdown 會失去結構、互動、導覽，或沒辦法把結果匯出回 agent 的場合。使用者明確要 HTML artifact、互動文件、單檔 prototype、圖解、簡報、報告，或能在瀏覽器打開的成品時用；學習／教學頁改用 html-explainer skill。
---

# HTML Artifacts

## 概要

工作需要瀏覽器才有的介面——版面、導覽、表格、圖解、控制項、複製／匯出按鈕，或輕量互動——就做一個單檔 `.html` artifact。

預設**先問再做 HTML**，除非使用者明確要 HTML。這個 skill 是要讓人 review 得更順，不是把每個回答都變成一個有自己意見的小網站。

## 怎麼決定

使用者要這些時直接做 HTML：

- HTML artifact、互動文件、能在瀏覽器打開的成品，或自包含頁面
- 視覺化的計畫、研究整理、報告、狀態頁、review artifact、圖解、簡報、prototype，或自訂編輯器
- 可分享的本機 artifact，而且 tab、篩選、複製按鈕、匯出控制項或視覺層次對它真的有幫助

這些情況先建議 HTML：

- Markdown 會把並排比較、空間結構、狀態或互動壓平
- 同一份資料要有好幾種檢視
- 使用者要檢查、排序、篩選、加註結構化輸出，或把它複製回 agent
- 回答長到有導覽和逐步展開 (progressive disclosure) 會改變好用程度

這些情況留在 Markdown：

- 回答很短、是聊天、只有 code，或大多是指令操作
- 輸出是會常常修改的原始檔
- 真正要交出來的是一個真的應用程式、套件或上線的前端
- HTML 只是裝飾

除非明確是教學需求，不要加測驗、教學類比或微世界——教學需求轉給 html-explainer skill。

## Artifact 要求

做成單一 `.html` 檔，除非使用者要更大的 app。

- CSS 和 JavaScript 全部 inline。
- 不用外部 CDN、字型、圖片或 build 步驟，除非任務真的需要。
- 用語意化 HTML、鍵盤能操作的控制項、無障礙標籤、足夠的對比，以及響應式版面。
- 優先放真的有用的操作元件 (affordance)：tab、篩選、搜尋、可排序表格、折疊區、複製按鈕、匯出成 Markdown／JSON，以及輕量的本機狀態。
- 守住 artifact 的任務：幫使用者決定、檢查、理解、比較，或接著做下去。
- 主要內容放第一屏。不要做 landing page 的 hero 版頭，除非使用者要簡報或對外頁面。

## 流程

1. 先弄清楚 artifact 的任務：review、計畫、比較、解說、prototype、圖解、報告，還是編輯。
2. 挑對那個任務有幫助的最小互動模型。
3. artifact 有重複的實體、篩選或匯出行為時，先定資料模型再寫 markup。
4. 在任務合適的位置建一個自包含的 `.html` 檔。
5. 可行時確認檔案在本機打得開；UI 比重高的 artifact 用瀏覽器實際看過。
6. 最後說一下檔案放在哪、支援哪種流程。

## 模式參考

挑 artifact 結構、互動模式或起手版面時讀 `references/patterns.md`。裡面有計畫、code review、設計、prototype、圖解、簡報、研究、報告和自訂編輯器的模式。

## 要避免的寫法

- 不要只因為 HTML 比 Markdown 好看就做 HTML。
- 不要把有用的輸出埋在裝飾性的外框底下。
- 不要做成一鍋卡片：重複項目用重複卡片沒問題，但密集的操作資訊通常該放表格、分割面板、時間軸或圖解。
- 不要落回模型預設的長相——漸層 hero 頁、emoji 或「01/02/03」編號的段落標籤、裝飾用 SVG、米白或灰白背景、標題裡的斜體強調字、monospace 標籤、膠囊形按鈕——除非使用者的主題或內容真的需要。
- 不要把 artifact 當成會長期維護的產品。使用者需要能維護的 app，就去做 app。

## 靈感來源

這個 skill 沿用 Thariq Shihipar 的 HTML effectiveness 範例和公開的 `dogum/html-artifacts` skill 示範的想法。把它們當靈感和模式詞彙；不要把大段文字原封不動抄進產出的 artifact。
