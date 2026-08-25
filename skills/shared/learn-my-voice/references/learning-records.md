# Persistent learning records

這一層保存跨專案仍有用的寫作選擇。它是 local-only 個人資料，不是可推送的
shared skill 內容；不得複製長篇原文、secrets、未公開個資或客戶資料。

## 建立結構

在本 skill 目錄建立：

```text
learning/
├── INDEX.md
├── voice-profile.md
└── topics/
    └── <context-slug>.md
```

`learning/.gitignore` 已讓動態檔案保持 untracked。若所在環境不是這個 dotfiles
安裝，仍須先確認 records 不會被公開或同步到未授權位置。

## Write authorization

先從目前載入的 `SKILL.md` 解析同層 `learning/` 的實際位置，不要假設目前 project
就是 skill source。讀取通常不需額外權限；寫入前先確認該目錄是否在目前
writable roots。

若 installed skill symlink 回 read-only dotfiles 或其他 sandbox 外路徑：

1. 只針對解析後的 `learning/` exact path 要求 scoped write approval，並說明用途是
   更新 local-only voice records。
2. 不要求整個 home、dotfiles repo 或其他 broad path 的寫入權。
3. Approval 不可用或被拒絕時，不建立替代的 global store；繼續 project-local
   exploration，並回報 persistent update blocked。
4. 不得把「本輪看過」描述成已跨專案保存；下一次仍從現存 records 判斷。

`INDEX.md` 是短而可排序的 routing table：

```markdown
# Voice learning index

| Context | Status | Evidence summary | Updated | File |
| --- | --- | --- | --- | --- |
| Technical essays | learning | Two revision pairs prefer claim-first openings. | 2026-08-25 | topics/technical-essays.md |
```

`voice-profile.md` 保存跨情境成立的偏好：

```markdown
# Voice profile

## Confirmed choices
- ...

## Working hypotheses
- ...

## Avoid
- ...
```

每個 `topics/<context-slug>.md` 保存情境專屬 evidence：

```markdown
# <Context>

## Scope
- Audience:
- Document types:

## Confirmed choices
- ...

## Working hypotheses
- ...

## Avoid
- ...

## Evidence
- YYYY-MM-DD, `<repo>:<explore commit>`: observed revision and narrow inference.
```

Slug 使用 lowercase ASCII 與 hyphen，例如 `technical-essays.md`、
`private-notes.md`、`product-specs.md`。

## Evidence 與升格

以下任一條成立，才可放進 `Confirmed choices`：

- 使用者明確說「我喜歡／不要／改成這樣」。
- 使用者明確接受 agent 的寫法。
- 至少兩個獨立 revision pairs 支持同一偏好，且沒有反例。

其他觀察只放 `Working hypotheses`。每條 inference 附最小必要 provenance，例如
日期、repo label 與 local explore commit；不要複製長篇原文。

Project-specific observation 先進 topic。只有跨至少兩種情境仍成立，或使用者明確
宣告為通用偏好，才升格到 `voice-profile.md`。反例出現時保留 decision context：
把規則縮窄、降回 hypothesis 或移到 `Avoid`，不要無聲覆寫。

## Read／write discipline

開始代寫前：

1. 讀 `INDEX.md` 找到相關 context。
2. 讀 `voice-profile.md` 與最接近的 topic。
3. 只採用有 evidence 且符合當前 audience／document type 的規則。

完成一個有意義的 revision pair 後才更新 records。每輪最多寫入少量、未來確實會
改變代寫結果的 observations；沒有新 evidence 就不動檔案。聊天中不回報純
bookkeeping，除非使用者明確詢問。
