---
name: wife-pdf
description: Create a plain zh-TW, non-technical family-facing PDF (Typst .typ source + compiled .pdf) when asked for a wife PDF, wife-friendly summary, family decision document, spouse-readable explanation, or 「做一份給老婆／家人看的 PDF」— any request to turn technical, career, or financial decisions into a document a non-technical family reader can follow.
---

# Wife-Friendly PDF Generator

產生給家人閱讀的 PDF：清楚、溫暖、決策導向，而且避免把技術細節直接丟到讀者臉上。主要使用 Typst，並優先支援 Traditional Chinese (zh-TW)。macOS 優先用 PingFang TC；Linux / VM 環境要加入 Noto Sans CJK TC fallback。

## 核心原則

### 語言風格

用清楚自然的 zh-TW：

- 避免不必要的 technical jargon。
- 用日常語彙，不用翻譯腔。
- 句子短一點，段落也短一點。
- 先講結論，再補原因。
- 把複雜概念改寫成「聰明但非技術背景的人」可以快速理解的版本。

### 文件結構

建議使用這種層次：

- Title：大標題，加日期。
- Quote block：開頭放簡短背景。
- Sections：用清楚 heading 與 divider 分段。
- Highlight boxes：重要結論、建議、風險用色塊。
- Tables：用於比較選項、條件、時間規劃。

### 手機閱讀與換頁

如果 PDF 是給手機閱讀，排版優先順序是「整塊好讀」高於「少一頁」。防切頁的完整規則只寫在這裡：

- 把手機 PDF 當成一組直式 slides：每頁能單獨讀懂、上方有清楚標題。section 會跨頁時，拆成多個有標題的 page group（例如 `必到時間｜晚餐與大秀`、`必到時間｜其他表演`），不要讓新頁從上一頁的尾巴開始。
- 同一張 card、block、table 絕不切到上下兩頁：Typst 元件一律 `breakable: false`，放不下就整塊移到下一頁。卡片本身長到一頁放不下，先拆成多張有標題的完整卡 —— 不要移除 `breakable: false` 讓它硬切。
- 也不要過度矯正成「一小節一頁」：多個短區塊能舒服放同一頁就合併（短卡片太多可收成一張摘要卡），避免重複卡框浪費版面。
- 排版驗收（Workflow 步驟 6-7 執行）：截圖目檢要同時抓「太擠」與「太空」。

Typst card/block 預設應該避免跨頁：

```typst
#let card(title, body, fill: rgb("#ffffff")) = block(
  fill: fill,
  inset: 8pt,
  radius: 5pt,
  stroke: 0.4pt + rgb("#d8e0e8"),
  width: 100%,
  below: 6pt,
  breakable: false,
)[
  #text(weight: "bold")[#title]
  #v(3pt)
  #body
]
```

### Kaomoji

一頁 PDF 至少放一個 kaomoji 增加溫度；多頁文件可視內容自然少量使用，不必每頁硬塞。先讀 `references/kaomoji-guide.md`，避免 checkbox、emoji、或 fallback 後會變方塊的字元。

## Typst 基礎樣板

Use `assets/career_decision_template.typ` as the complete working Typst example. Key gotchas to preserve when adapting it:

- Font stack must include macOS PingFang/Heiti and Linux/VM Noto Sans CJK fallback.
- 資訊卡與表格照「手機閱讀與換頁」的防切頁規則。
- Avoid Markdown checkbox syntax in Typst output; it can render poorly in PDFs.

## 常用 Typst Pattern

table 防切頁 wrapper：

```typst
#block(breakable: false)[
  #table(...)
]
```

重點決策色塊：

```typst
#block(
  fill: rgb("#e8f5e9"),
  inset: 12pt,
  radius: 4pt,
  width: 100%,
)[
  *Key decision here*
]
```

常用顏色：

- `rgb("#e8f5e9")`：淡綠色，正向或推薦。
- `rgb("#fff3e0")`：淡橘色，重要提醒或風險。
- `luma(248)`：淡灰色，中性資訊或 timeline。

Timeline block：

```typst
#block(fill: luma(248), inset: 12pt, radius: 4pt, width: 100%)[
  #table(
    columns: (auto, 1fr),
    inset: 8pt,
    stroke: none,
    [*Date 1*], [Action 1],
    [*Date 2*], [Action 2],
  )
]
```

## Workflow

1. 先理解要傳達的內容、讀者背景、決策目的。
2. 把技術內容改寫成 plain zh-TW。
3. 建立 `.typ`，使用本 skill 的 template patterns；手機版應先規劃每一頁的 page group，而不是讓長文自然流頁，也不是把每個小 heading 都硬切一頁。
4. 執行 `typst compile filename.typ` 產生 PDF。
5. 在目標維護環境也編譯一次；若是 Linux / VM，確認有 `fonts-noto-cjk` 或等效 CJK 字型，避免中文字 fallback 出問題。
6. 將 PDF render 成頁面截圖，至少抽查手機版主要章節；資訊密集文件要逐頁檢查。
7. 檢查 PDF：字型、換頁、表格、kaomoji 是否有方塊或截斷，並確認沒有 card、block、section 被切到下一頁；每一頁上方應有清楚標題，且同主題可合併頁面不應留下大片空白。
8. 修正 `.typ` 並重新編譯 PDF。

## 常見章節

職涯決策：

- 目前的狀況
- 我考慮了哪些選項
- 我目前的想法
- 什麼時候該改變計畫？（止損點）
- 時間規劃

財務決策：

- 目前的財務狀況
- 選項比較
- 風險與報酬
- 建議的做法

家庭或生活決策：

- 我們現在面對的問題
- 有哪些選擇
- 每個選擇的好處與風險
- 我建議怎麼做
- 接下來要確認的事

## 輸出檔案

通常產生兩個檔案：

- `.typ`：Typst source，用於排版與 PDF 編譯。
- `.pdf`：最終輸出。

## Reference

- `assets/career_decision_template.typ`：完整可工作的 Typst 範例。
- `references/kaomoji-guide.md`：PingFang TC 下較穩定的 kaomoji 清單。
