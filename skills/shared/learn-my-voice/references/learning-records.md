# Persistent learning records

這一層保存跨專案仍有用的寫作選擇。Storage mode 的 SSOT 是
`voice-profile.md`；只保存可公開的抽象偏好，不得複製長篇原文、secrets、未公開
個資或客戶資料。

## 建立結構

Records 固定放在本 skill 目錄的 `learning/`：

```text
learning/
├── INDEX.md
├── voice-profile.md
└── topics/
    └── <context-slug>.md
```

`INDEX.md` 與 `voice-profile.md` 是 tracked SSOT；topic files 依實際 evidence 建立。
不要建立第二份全域 voice store。`.publication-consent` 是每台裝置 local-only 的
一次性授權 marker，不追蹤、不跨裝置同步。

## Public sync contract

`voice-profile.md` 保存預期的 public repo identity 與 storage mode，但 clone／copy
不可自行繼承 publication authorization。每次 session 第一次更新前：

1. 解析 installed skill symlinks，取得 `learning/` 的 physical target。
2. 確認 target 位於 Git worktree，repo identity 是 `ChiTienHsieh/dotfiles`，且
   `INDEX.md`、`voice-profile.md` 與既有 topic files 由該 repo 追蹤。新 topic 必須
   位於同一 `learning/topics/`，並在本輪以 exact path 新增。
3. 確認同一 `learning/` 內存在未追蹤的 `.publication-consent`。若缺少，向使用者
   說明 exact repo、remote 與 public write，再取得一次授權並建立 marker。
4. 任一驗證失敗就 fail closed：不寫 copy／cache／錯誤 checkout，回報 sync
   blocked，也不建立替代 store。

Remote URL 可為 HTTPS 或 SSH 表示法，但 normalize 後 owner／repo 必須精確相同。
若 sandbox 不允許寫入 resolved target，只要求 exact `learning/` path 的 scoped
permission，不可擴張到整個 home。

驗證通過後，每次更新仍須：

1. Fresh-read `learning/`、dotfiles branch、working diff 與 cached diff。
2. 只寫會改變未來代筆結果的最小抽象 evidence；不複製原始段落。
3. 掃描 secrets、識別性個資、客戶資料與其他不適合 public repo 的內容。

成功更新後，只 stage `learning/` 內本輪已知 paths，並沿用
[exploration-workflow.md](exploration-workflow.md) 的 staged-index isolation：有既有
cached changes 時，只有 exact paths 且沒有同路徑 partial staging 才能用
`git commit --only -- <paths>`；commit 後確認其他 cached diff 完全不變。無法證明
就停止。之後依 dotfiles repo 當前的 review、commit、push／PR contract 同步。

`INDEX.md` 是短而可排序的 routing table；`voice-profile.md` 保存跨情境成立的
偏好與 publication contract。兩者的 tracked files 是格式 SSOT，不在本 reference
複製一份。

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

開始代寫前讀 `INDEX.md`、`voice-profile.md` 與最接近的 topic，只採用有 evidence
且符合當前 audience／document type 的規則。完成一個有意義的 revision pair 後
才更新 records；沒有新 evidence 就不動檔案。
