// 字體設定
#set text(font: ("PingFang TC", "Heiti TC"), size: 11pt, lang: "zh")
#set page(margin: (x: 2cm, y: 1.8cm))
#set par(leading: 0.7em, justify: true)

// 標題樣式
#show heading.where(level: 1): it => {
  set text(size: 20pt, weight: "bold")
  block(above: 1.5em, below: 1em)[#it.body]
}

#show heading.where(level: 2): it => {
  set text(size: 14pt, weight: "bold")
  block(above: 1.2em, below: 0.8em)[#it.body]
}

#show heading.where(level: 3): it => {
  set text(size: 12pt, weight: "bold")
  block(above: 1em, below: 0.5em)[#it.body]
}

// 引用樣式
#let quote-block(body) = {
  block(
    fill: luma(245),
    inset: 12pt,
    radius: 4pt,
    width: 100%,
  )[#text(style: "italic")[#body]]
}

// 分隔線
#let divider = line(length: 100%, stroke: 0.5pt + luma(200))

// ============================================
// 文件開始
// ============================================

= 職涯決策討論 - 2026 年 1 月

#quote-block[
  這份文件記錄了我和酷老爹（Claude Code）討論後的職涯規劃，方便之後回顧。\
  討論日期：2026-01-07
]

#divider

== 目前的狀況

- *現在的工作*：在啟碁科技（WNC）擔任 AI 應用工程師，同時帶領後端團隊
- *工作多久了*：從 2024 年 7 月到現在，大約 18 個月
- *帶幾個人*：目前帶 5 個工程師，之後可能會升等成課長並正式帶領 6 人團隊（包括我六個人）
- *夢想的公司*：Google（最想去）、NVIDIA、Microsoft、Amazon
- *有沒有門路*：有一個在美國 Google 工作的朋友，可以幫我內部推薦
- *經濟壓力*：目前沒有急迫的用錢需求，想買房但不急

#divider

== 我考慮了哪些選項

=== 選項一：現在就開始投履歷，三四月找到新工作
- *結論*：#text(fill: red)[✗] 現在不適合
- *原因*：刷題還沒準備好、公司快要幫我升職了

=== 選項二：等四月升職，帶更大的團隊，累積經驗後再挑戰 Google
- *結論*：#text(fill: green)[✓] 推薦這個 #h(0.5em) ╰(°▽°)╯
- *原因*：履歷上「帶 6 個人 + 有升職紀錄」比現在好看很多，有更多時間準備

=== 選項三：在公司內部轉到另一個部門（資料分析 + AI）
- *結論*：#text(fill: orange)[⚠] 有些疑慮
- *原因*：從「帶 5-6 人的小主管」變成「4 人團隊的成員」，等於降級

=== 選項四：先升職，然後開始投台灣的外商公司
- *結論*：#text(fill: green)[✓] 也不錯
- *原因*：有升職紀錄後面試更有底氣，外商 offer 可以當 Google 備案

#divider

== 我目前的想法 #h(0.3em) ╰(°▽°)╯

#block(
  fill: rgb("#e8f5e9"),
  inset: 12pt,
  radius: 4pt,
  width: 100%,
)[
  *選擇選項二或四* — 先留下來升職，累積帶更大團隊的經驗，然後再挑戰 Google。
]

#divider

== 什麼時候該改變計畫？（止損點）

#block(breakable: false)[
  #table(
    columns: (1fr, 1.2fr, 1.2fr),
    inset: 10pt,
    align: left,
    fill: (col, row) => if row == 0 { luma(230) } else { white },
    [*狀況*], [*警戒線*], [*該怎麼做*],
    [在公司很痛苦], [兩週內想離職超過 10 次], [開始投履歷，有 offer 就走],
    [四月沒有升職], [老闆說的升職沒有發生], [馬上開始找工作],
    [升職後變超忙], [連續一個月沒時間刷題], [考慮辭職專心準備],
  )
]

#divider

== 時間規劃

#block(
  fill: luma(248),
  inset: 12pt,
  radius: 4pt,
  width: 100%,
)[
  #table(
    columns: (auto, 1fr),
    inset: 8pt,
    align: left,
    stroke: none,
    [*2026 年 1-4 月*], [留在公司，準備升職，每天刷題],
    [*2026 年 4 月*], [升職（希望如此）],
    [*2026 年 4-10 月*], [累積帶 6 人團隊的經驗（約 6 個月）],
    [*2026 年 5-6 月*], [可以開始投一些台灣外商試試看],
    [*2026 年 10 月*], [請朋友幫我內推 Google],
  )
]

#divider

== 關於刷題 #h(0.3em) (￣▽￣)／

=== 需要刷多久？

根據有經驗的朋友建議，需要把 75 題核心題目刷到「滾瓜爛熟」，大概要 *3-4 個月*。

=== 每天大概要刷多久？

- *平日*：下班後 1-2 小時
- *假日*：可以多刷一點，但也要休息
- *總計*：大約每週 6 天，每週約 10 小時

=== 為什麼這很重要？

#block(
  fill: rgb("#fff3e0"),
  inset: 12pt,
  radius: 4pt,
  width: 100%,
)[
  *這是進入 Google 的門票。*

  Google 的軟體工程師年薪通常是台灣一般公司的 2-4 倍。現在花 6 個月認真準備，換來的可能是未來 10 年的高薪工作，對買房會有很大的幫助 ╰(°▽°)╯
]

#divider

== 目前工作的狀況

=== 和老闆的關係
- 之前老闆（Sam）有時候脾氣不好、交代事情不清楚 #h(0.3em) ┐(￣ヘ￣)┌
- 上週我跟他坦白談過之後，這七天明顯改善了脾氣的部分
- 不確定會不會又變回去，但目前是好的

=== 升職的可能性
- 老闆說如果我繼續表現好，四月很可能會升職
- 我已經開始更積極地帶團隊
- 我覺得自己滿擅長帶人的，應該可以做好 #h(0.3em) (°▽°)

=== 升職後會不會更忙？
- 預估跟現在差不多，不會忙到沒時間刷題
- 如果真的太忙，我也可以接受辭職專心準備

#divider

== 還沒決定的事

- 一二月要拿哪幾間公司來「試水溫」練習面試？
- 什麼時候正式跟 Google 的朋友說我想請他內推？

#v(1em)
#align(right)[
  #text(size: 9pt, fill: luma(120))[最後更新：2026-01-07]
]
