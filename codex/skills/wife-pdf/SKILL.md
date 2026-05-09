---
name: wife-pdf
description: Create a plain zh-TW, non-technical family-facing PDF with Typst when asked for a wife PDF, wife-friendly summary, family decision document, or spouse-readable explanation.
---

# Wife-Friendly PDF Generator

產生給家人閱讀的 PDF：清楚、溫暖、決策導向，而且避免把技術細節直接丟到讀者臉上。主要使用 Typst，並優先支援 Traditional Chinese (zh-TW) 與 macOS 的 PingFang TC 字型。

## 使用時機

在以下情況使用這個 skill：

- 使用者要求「create a PDF for my wife」、「wife-friendly summary」、「export to wife PDF」、「wife-approved PDF」。
- 使用者需要把技術、職涯、財務或家庭決策整理成非技術讀者能理解的文件。
- 使用者提到 wife、spouse、family，或明確要求 plain zh-TW summary。
- 輸出需要是 `.md`、`.typ`、`.pdf` 三件組，方便之後修改與重新編譯。

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

如果 PDF 是給手機閱讀，排版優先順序是「整塊好讀」高於「少一頁」：

- 不要讓同一個 card、block、section 或餐廳/活動資訊卡被分割到上下兩頁。
- 如果一個區塊放不下目前頁面，就讓它整塊移到下一頁。
- 優先使用短卡片、短段落與清楚 heading，避免靠讀者縮放來補救版面。
- 對於資訊密集內容，寧可拆成多張完整卡片，也不要做成一張過長卡片後被切頁。
- 產出前必須檢查 PDF 頁面截圖，確認沒有 block 被頁面邊界切開。

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

如果某個區塊本身長到一頁放不下，先拆內容，不要移除 `breakable: false` 讓它硬切。

### Kaomoji

可以少量使用 kaomoji 增加溫度，但只使用 PingFang TC 渲染穩定的字元。先讀 `references/kaomoji-guide.md`，不要使用容易變方塊的字元。

安全清單：

- `╰(°▽°)╯`
- `(°▽°)`
- `(￣▽￣)／`
- `┐(￣ヘ￣)┌`
- `ヽ(°〇°)ﾉ`

避免：

- `(◕‿◕)`，`‿` 常會變方塊。
- `(๑•̀ㅂ•́)و✧`，混合 script 容易壞。
- 大多數 emoji。
- Typst PDF 中的 Markdown checkbox `- [ ]` 或 `- [x]`。

## Typst 基礎樣板

```typst
// Font settings - PingFang TC for zh-TW
#set text(font: ("PingFang TC", "Heiti TC"), size: 11pt, lang: "zh")
#set page(margin: (x: 2cm, y: 1.8cm))
#set par(leading: 0.7em, justify: true)

// Heading styles
#show heading.where(level: 1): it => {
  set text(size: 20pt, weight: "bold")
  block(above: 1.5em, below: 1em)[#it.body]
}

#show heading.where(level: 2): it => {
  set text(size: 14pt, weight: "bold")
  block(above: 1.2em, below: 0.8em)[#it.body]
}

// Quote block for context
#let quote-block(body) = {
  block(
    fill: luma(245),
    inset: 12pt,
    radius: 4pt,
    width: 100%,
  )[#text(style: "italic")[#body]]
}

// Divider line
#let divider = line(length: 100%, stroke: 0.5pt + luma(200))
```

## 常用 Typst Pattern

避免 table 或 card 被切頁：

```typst
#block(breakable: false)[
  #table(...)
]
```

手機版 PDF 的每個資訊卡也應該使用 `breakable: false`。若發現整張卡太長，改成兩張有標題的卡，不要讓 Typst 在頁面中間切開它。

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
3. 建立 `.md` 草稿，讓內容容易修改。
4. 建立 `.typ`，使用本 skill 的 template patterns。
5. 執行 `typst compile filename.typ` 產生 PDF。
6. 將 PDF render 成頁面截圖，至少抽查手機版主要章節；資訊密集文件要逐頁檢查。
7. 檢查 PDF：字型、換頁、表格、kaomoji 是否有方塊或截斷，並確認沒有 card、block、section 被切到下一頁。
8. 修正 `.md` 與 `.typ`，保持兩者內容同步。

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

通常產生三個檔案：

- `.md`：plain markdown，方便閱讀與修改。
- `.typ`：Typst source，用於排版與 PDF 編譯。
- `.pdf`：最終輸出。

## Reference

- `assets/career_decision_template.typ`：完整可工作的 Typst 範例。
- `references/kaomoji-guide.md`：PingFang TC 下較穩定的 kaomoji 清單。
