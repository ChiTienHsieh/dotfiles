---
name: diagram-editor
description: Create or adapt a self-contained offline HTML editor for Mermaid flowcharts that keeps Mermaid text as the interchange format. Use when a user wants to generate, visually edit, annotate, import, or export a Mermaid flowchart; needs an agent-to-human-to-agent diagram review loop; or asks for a browser-openable single-file diagram editor with no external dependencies.
---

# Mermaid flowchart 編輯器

把 `assets/editor.html` 當成可直接使用的離線編輯器，或複製一份到任務指定位置再做最小幅度調整。除非使用者要求改產品行為，不要重寫 parser、serializer 或資料保留邏輯。

## 工作流

1. 複製 `assets/editor.html`，或直接提供它的絕對路徑。
2. 讓 agent 先產出 Mermaid flowchart；使用者可貼進 code 面板，或載入 `.mmd`／`.md`。
3. 使用者在 SVG 畫布新增、刪除、拖曳與註記；code 面板會同步 Mermaid 文字。
4. 用「複製 Mermaid」保留純圖，或用「匯出給 agent」加入一行註解慣例 preamble 後貼回 agent。
5. 若有微調 editor，重新驗證離線、手機操作與 round-trip；資料保留優先於額外功能。

## v1 支援子集

- 宣告：`flowchart TD|LR|BT|RL`，亦接受 `graph`。
- 節點：`A`、`A[方框]`、`A(圓角)`、`A{菱形}`、`A([膠囊])`。
- 邊：`-->`、`---`、`-.->`、`==>`，可用 `A -->|文字| B` 加標籤。
- 註解：以 `%%` 開頭的單行註解。

GUI 的「形狀／線型」只對應上述節點形狀與邊型；不產生 `classDef`、`style` 或其他 Mermaid 樣式語法。手動拖曳座標只存在目前瀏覽器畫布，不會寫進 Mermaid；重新匯入或自動排版會重算位置。

## 結構化註解慣例

- `%% @comment A: 內容` 綁定節點 `A`。
- `%% @comment A-->B: 內容` 綁定從 `A` 到 `B` 的邊；不論實際線型為何，key 一律寫成 `A-->B`。
- 結構化註解輸出時必須緊跟對應定義行；連續多行代表同一元素的多則註解。
- 沒有 `@comment` 的 `%%` 行是文件層級註解。
- 同一對端點有多條邊時，註解必須緊跟目標邊，否則重新匯入時無法可靠判斷；編輯器會保留原文並提出警告，不猜測綁定。
- 「匯出給 agent」會加入一行文件註解，直接說明以上 node／edge 綁定格式。

## 資料保留

- Parser 只結構化辨識支援子集。`subgraph`、`classDef`、`style` 或其他未知行要顯示警告、原樣留在來源序列，匯出時逐字吐回。
- 不得把未知語法正規化、重排或刪除。GUI 操作只改動使用者實際編輯的支援項目。
- 若功能與 round-trip 衝突，刪功能，不放寬資料保留保證。
- 修改 editor 後，用涵蓋全部節點、邊型、`@comment`、文件註解與未知語法的圖跑兩次 parse／serialize；除容許的空白差異外，結果必須一致。

## 明確不做

- sequence、gantt、ER 或 flowchart 以外的 Mermaid 圖。
- `subgraph` 的結構化編輯。
- `classDef`、`style`、主題或任意顏色等樣式編輯。
- Excalidraw 匯入／匯出與多人協作。
- `localStorage` 草稿以外的持久化。

## 交付檢查

1. 確認仍是單一 HTML，CSS／JS 全 inline，沒有 CDN、外部字型、`fetch` 或其他網路請求。
2. 直接用 `file://` 開啟，測試貼上、檔案匯入、節點／邊編輯、註解、拖曳、自動排版與兩種複製。
3. 在窄螢幕測試控制項、畫布選取與拖曳，不可只驗桌面版。
4. 執行內建 `window.__diagramEditor.runRoundTripTest()`；失敗時不可交付。
