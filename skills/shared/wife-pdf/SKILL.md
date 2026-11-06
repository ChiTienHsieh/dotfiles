---
name: wife-pdf
description: 用 Typst 做白話的 zh-TW PDF，給不懂技術的家人看、幫他們做決定。使用者要 wife PDF、給另一半或家人看的摘要，或要解釋技術、職涯、財務、家務上的選擇時用。
disable-model-invocation: true
---

# wife-pdf

用 Typst 做給家人看的 zh-TW 文件：講清楚、語氣溫暖、重點是幫忙做決定；source 和編好的 PDF 一起交。

## Resources

- 複製並改寫 `assets/career_decision_template.typ` 的版型與 helpers；把內容裡的範例事實全數換成本次資料。
- 加入 kaomoji、符號或 checkbox 前，讀 `references/kaomoji-guide.md`。
- 需要挑選章節時，讀 `references/section-patterns.md`；只取本次決策需要的部分。

## Content contract

- 用自然的 zh-TW 和日常語彙，把技術的東西講到不懂技術的家人一看就懂。
- 先說結論，再說理由；保持短句、短段落，用表格或色塊比較選項、條件、時間與風險。
- 單頁 PDF 至少自然放一個 kaomoji；多頁文件少量使用，不要每頁硬塞。

## Mobile page contract

- 把手機 PDF 當成一組直式 slides：每頁可獨立讀懂，上方有清楚標題；section 跨頁時拆成有標題的 page groups。
- Card、block、table 一律 `breakable: false`；單塊長到一頁放不下時，拆成多張有標題的完整卡片，不要讓元件硬切頁。
- 多個短區塊能舒服放同頁就合併，避免過度分頁、重複卡框或大片空白。

## Workflow

1. 確認要傳達的事實、讀者背景與決策目的。
2. 複製 template 建立 `.typ`，保留 macOS PingFang/Heiti 與 Linux/VM Noto Sans CJK 字型 fallback。
3. 先規劃 page groups，再填內容；不要讓長文自然流頁或每個小 heading 都獨佔一頁。
4. 執行 `typst compile filename.typ`。
5. 也在目標維護環境編譯；Linux/VM 需有 `fonts-noto-cjk` 或等效 CJK 字型。
6. 將 PDF 每一頁 render 成截圖並逐頁目檢。
7. 檢查字型、方塊字、截斷、切頁、頁首標題，以及過擠或過空的版面。
8. 修正 `.typ`、重新編譯與 render，直到逐頁檢查通過。

## Deliverables

- `.typ`：可維護的 Typst source。
- `.pdf`：已通過視覺驗收的最終文件。
