// 字體設定
#set text(font: ("PingFang TC", "Heiti TC", "Noto Sans CJK TC"), size: 11pt, lang: "zh")
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
    breakable: false,
  )[#text(style: "italic")[#body]]
}

// 手機閱讀用資訊卡：不要讓同一張卡被切到下一頁。
// 如果內容長到一頁放不下，請先拆成多張卡。
#let card(title, body, fill: rgb("#ffffff")) = block(
  fill: fill,
  inset: 12pt,
  radius: 4pt,
  width: 100%,
  below: 8pt,
  breakable: false,
)[
  #text(weight: "bold")[#title]
  #v(4pt)
  #body
]

// 分隔線
#let divider = line(length: 100%, stroke: 0.5pt + luma(200))

// ============================================
// 文件開始
// ============================================

= 職涯決策討論 - YYYY 年 MM 月

#quote-block[
  這份文件把目前的選項、取捨與下一步整理成家人能一起討論的版本。\
  討論日期：YYYY-MM-DD
]

#divider

== 先說結論

#card(
  [目前建議],
  [先維持現況到下一個檢查點，同時完成必要準備；如果關鍵條件沒有發生，再啟動替代方案。],
  fill: rgb("#e8f5e9"),
)

== 我們現在面對什麼？

- *想解決的問題*：用一句話說明這次決策。
- *最重要的限制*：列出時間、家庭、健康或財務條件。
- *決策期限*：寫下什麼時候必須拍板。

#divider

== 有哪些選擇？

#card([選項 A｜維持現況], [好處是風險較低；代價是進展較慢。])
#card([選項 B｜立即改變], [好處是更快接近目標；代價是不確定性較高。])
#card([選項 C｜設定觀察期], [先收集關鍵資訊，再於明確日期重新決定。])

== 怎麼比較？

#block(breakable: false)[
  #table(
    columns: (1fr, 1fr, 1fr),
    inset: 9pt,
    align: left,
    fill: (col, row) => if row == 0 { luma(230) } else { white },
    [*選項*], [*主要好處*], [*主要風險*],
    [A], [穩定、可預期], [可能錯過時機],
    [B], [速度快、方向明確], [壓力與成本較高],
    [C], [資訊更完整], [需要守住觀察期限],
  )
]

#divider

== 什麼情況要改變計畫？

#block(breakable: false)[
  #table(
    columns: (1.1fr, 1fr, 1.2fr),
    inset: 9pt,
    align: left,
    fill: (col, row) => if row == 0 { luma(230) } else { white },
    [*觀察項目*], [*警戒線*], [*到時候怎麼做*],
    [關鍵承諾], [在期限前沒有發生], [啟動選項 B],
    [生活負擔], [連續數週超出可承受範圍], [縮小計畫或暫停],
    [家庭影響], [影響核心生活安排], [重新一起評估],
  )
]

== 接下來的時間表 #h(0.3em) (•̀ᴗ•́)و

#block(
  fill: luma(248),
  inset: 12pt,
  radius: 4pt,
  width: 100%,
  breakable: false,
)[
  #table(
    columns: (auto, 1fr),
    inset: 8pt,
    align: left,
    stroke: none,
    [*本週*], [確認事實與不能妥協的條件],
    [*本月*], [完成必要準備並記錄變化],
    [*檢查點*], [依警戒線重新決定，不無限延期],
  )
]

== 還需要一起確認

- 哪個風險最不能接受？
- 什麼資訊會真正改變決定？
- 到了檢查點，由誰提醒我們重新討論？

#v(1em)
#align(right)[
  #text(size: 9pt, fill: luma(120))[最後更新：YYYY-MM-DD]
]
