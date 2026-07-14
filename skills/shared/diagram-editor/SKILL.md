---
name: diagram-editor
description: Single-file HTML editor for Mermaid flowcharts — humans edit and annotate visually, agents read plain Mermaid text. Use when the user wants to hand a Mermaid flowchart to a human for GUI editing or markup, asks for the diagram editor / mermaid editor, or wants an edit-in-browser-then-paste-back-to-agent diagram workflow. Ships assets/editor.html to copy or adapt per task.
---

# diagram-editor — Mermaid 流程圖的人機交接編輯器

## 解決什麼痛點

Mermaid 對 AI 友善(token 少、純語意),但人類難以直接改文字、加註記;畫布工具(如 Excalidraw)對人友善,匯出的卻是 AI 不友善的視覺 JSON。這個編輯器兩邊都接:**人用 GUI 編輯與註記,進出口都是 Mermaid 文字**。

工作流:agent 產出 mermaid → 人在瀏覽器裡編輯、加註解 → 一鍵「匯出給 agent」貼回對話。

操作走 Excalidraw 慣例:手繪風渲染(自寫的 rough 線條與斜線填充,無外部依賴)、懸浮工具列＋數字快捷鍵(1 選取、2 方框、3 菱形、4 膠囊、5 箭頭、6 直線)、形狀工具點畫布放節點、箭頭工具從節點拖到節點建邊(拖到空白會順手長出新節點)、雙擊改字、雙擊空白新增節點、左側屬性面板改顏色/線寬/線型、滾輪平移、Ctrl/Cmd+滾輪或雙指捏合縮放、空白鍵暫時平移、Cmd+Z/Cmd+Shift+Z 復原重做、Cmd+D 複製節點。

## 怎麼用

1. 把 `assets/editor.html` 複製到任務適合的位置(通常是 `~/scratch/` 或使用者指定處),連同 agent 產出的 mermaid 一起交給使用者;或直接 `open editor.html` 再請使用者貼上程式碼。
2. 使用者編輯完按「匯出給 agent」,貼回來的文字開頭有一行 `%% [diagram-editor]` preamble,說明註解慣例——任何 LLM 不需額外解釋就能讀懂。
3. 需要客製(改預設圖、改配色、鎖定某些功能)就微調複製出去的那份;`assets/` 裡的原版保持通用。

編輯器是單一自包含 `.html`:零外部依賴、無 CDN、無網路請求,離線可用,手機可操作,草稿自動存瀏覽器 localStorage。

## 支援的 Mermaid 子集(v1 只做 flowchart)

| 類別 | 語法 |
|---|---|
| 標頭 | `flowchart TD\|LR\|BT\|RL`(也接受 `graph`、`TB`、省略方向) |
| 節點 | `A`、`A[方框]`、`A(圓角)`、`A([膠囊])`、`A{菱形}`,標籤可用 `"…"` 包特殊字元 |
| 邊 | `-->`、`---`、`-.->`、`==>`,標籤 `A -->\|文字\| B`,支援鏈式 `A --> B --> C` 與自迴圈 |
| 樣式 | `style A fill:#…,stroke:#…`(節點)、`linkStyle 0 stroke:#…`(邊,單一索引;索引照邊的宣告順序,匯出時重算)。屬性面板的顏色/線寬/虛線就存在這裡,未知的樣式 key 原樣保留。若子集外語法(如 subgraph)裡也有邊,linkStyle 索引對不準,會整行原樣保留、不掛到邊上並警告 |
| 註解 | `%%` 開頭的行(見下方慣例) |

「筆觸」(工整/手繪/潦草)與斜線填充是這個編輯器的檢視偏好,不進 Mermaid;`fill` 在真正的 mermaid 渲染裡會是實心底色。

## 結構化註解慣例(本工具的核心價值)

- `%% @comment 節點ID: 內容`——綁定節點;`%% @comment A-->B: 內容`——綁定邊(箭頭寫該邊實際的型別)。匯出時緊跟在對應定義行之後;同目標多行註解會合併、逐行輸出。
- 同端點有多條平行邊時,邊註解**靠相鄰性綁定**:緊跟在哪條邊的定義行後面就綁哪條。不相鄰又有多條候選的註解不猜——原位原樣保留並警告,要綁定就把註解移到目標邊的定義行正下方。
- 無 `@` 的 `%%` 行是文件層級註解,匯出時放在標頭後。
- 「匯出給 agent」會在最前面加一行 `%% [diagram-editor] …` preamble 說明此慣例;編輯器重新匯入時會把這行丟掉,不會越疊越多。
- 有註解的節點/邊在畫布上有 💬 標記,滑鼠停留可看內容。

## 不吞資料保證(round-trip)

- 子集外的語法(`subgraph`、`classDef`、`%%{init}%%`…)匯入時警告使用者、原樣保留,匯出時**在原位**逐字吐回——行序不變,所以 `%%{init}%%` 這類位置敏感的指令不會失效。`subgraph` 整塊(含其中節點)視為一個保留區塊,裡面的節點不會出現在畫布。
- 匯出 → 匯入 → 匯出結果一致(容許空白差異)。改動 `editor.html` 的 parse/serialize 邏輯後,必須重驗:開瀏覽器 console 跑 `window.__diagramEditor.runRoundTripTest()`,`pass` 不是 `true` 就不能交付。核心純函式圈在 `// ===== core-start =====` / `// ===== core-end =====` 標記之間(含這個自測),也可抽出來在 Node 裡跑。
- 功能與簡潔衝突時,砍功能,不砍 round-trip 保證。

## 座標不會匯出(要跟使用者明講)

Mermaid 沒有地方存座標。拖曳節點只改當下畫面,匯出不含位置,重開會重新自動排版(內建簡單分層排版)。UI 上已有這行提醒,不要拿掉。

## 明確不做

sequence/gantt/ER 圖、subgraph 編輯、`classDef`/`class` 樣式類別(只支援上表的 `style`/`linkStyle` 直接樣式)、Excalidraw 匯入、協作、localStorage 草稿以外的持久化。不打包 mermaid.js 或 rough.js(體積不符單檔原則,parser 與手繪渲染都是自寫的精簡實作)。
