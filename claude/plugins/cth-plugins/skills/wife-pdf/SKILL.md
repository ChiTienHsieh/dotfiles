---
name: wife-pdf
description: This skill should be used when the user asks to "create a PDF for my wife", "generate a wife-friendly summary", "make a document my wife can understand", "export to wife PDF", "wife-approved PDF", or needs to create a clear, non-technical document summary in Traditional Chinese (zh-TW) using Typst.
---

# Wife-Friendly PDF Generator

Generate clear, decision-focused PDF documents that non-technical family members can easily understand. Uses Typst for beautiful typography with proper Traditional Chinese support.

## When to Use

- Summarizing technical decisions for family discussion
- Creating career planning documents
- Any document that needs to be understood by non-technical readers
- When user mentions "wife", "family", or needs plain-language summaries

## Core Principles

### 1. Language Style

Write in **plain zh-TW** (Traditional Chinese):
- Avoid technical jargon entirely
- Use everyday vocabulary
- Keep sentences short and clear
- Explain concepts as if talking to a smart person who knows nothing about tech

### 2. Document Structure

Use clear visual hierarchy:
- **Title**: Big, clear, with date
- **Quote block**: Brief context at top (grey background)
- **Sections**: Clear headings with dividers
- **Highlight boxes**: Colored backgrounds for key decisions
- **Tables**: For comparing options or listing criteria

### 3. Kaomoji Usage

Use kaomoji sparingly for warmth, but **only these safe ones** that render properly in PingFang TC:

**Safe kaomoji (use these):**
- `╰(°▽°)╯` - Happy/excited
- `(°▽°)` - Simple happy
- `(￣▽￣)／` - Casual/relaxed
- `┐(￣ヘ￣)┌` - Shrug/frustrated
- `ヽ(°〇°)ﾉ` - Surprised

**Avoid these (render poorly):**
- `(◕‿◕)` - The `‿` becomes a square
- `(๑•̀ㅂ•́)و✧` - Thai characters don't render
- Any kaomoji with special combining characters

### 4. Typst Template Structure

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

### 5. Key Typst Patterns

**Prevent table page breaks:**
```typst
#block(breakable: false)[
  #table(...)
]
```

**Colored highlight box (for decisions):**
```typst
#block(
  fill: rgb("#e8f5e9"),  // Light green for positive
  inset: 12pt,
  radius: 4pt,
  width: 100%,
)[
  *Key decision here*
]
```

**Color options:**
- `rgb("#e8f5e9")` - Light green (positive/recommended)
- `rgb("#fff3e0")` - Light orange (important/warning)
- `luma(248)` - Light grey (neutral/timeline)

**Timeline/schedule block:**
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

1. **Gather content**: Understand what needs to be communicated
2. **Simplify language**: Rewrite technical content in plain zh-TW
3. **Structure document**: Use clear sections and visual hierarchy
4. **Add warmth**: Include appropriate kaomoji (sparingly)
5. **Create .typ file**: Use the template patterns above
6. **Compile**: Run `typst compile filename.typ`
7. **Review PDF**: Check for rendering issues, especially kaomoji
8. **Iterate**: Fix any visual problems

## Common Sections

For **career decisions**:
- 目前的狀況 (Current situation)
- 我考慮了哪些選項 (Options considered)
- 我目前的想法 (Current thinking)
- 什麼時候該改變計畫？（止損點）(Stop-loss criteria)
- 時間規劃 (Timeline)

For **financial decisions**:
- 目前的財務狀況 (Current finances)
- 選項比較 (Option comparison)
- 風險與報酬 (Risk vs reward)
- 建議的做法 (Recommended approach)

## Output Files

Generate two files:
1. **`.md` file**: Plain markdown for easy editing
2. **`.typ` file**: Typst source for beautiful PDF
3. **`.pdf` file**: Final compiled output

Keep both .md and .typ in sync for future updates.

## Example Reference

See `assets/career_decision_template.typ` for a complete working example.
