# Persistent learning records

這一層保存跨專案仍有用的抽象寫作選擇；公開內容邊界以 `voice-profile.md` 為準。

## 位置與同步

Records 固定放在本 skill 的 `learning/`：

```text
learning/
├── INDEX.md
├── voice-profile.md
└── topics/
    └── <context-slug>.md
```

`voice-profile.md` 保存公開程式碼庫識別與跨情境偏好；`INDEX.md` 是 topic 索引。
更新前解析安裝路徑的 symlink（符號連結），找到實際目錄，確認這些檔案確實由
profile 指定的 dotfiles 程式碼庫追蹤。驗證失敗時停止，不寫入副本、快取、其他
checkout 或替代紀錄位置。

每次更新先讀取並遵守 `voice-profile.md` 的公開同步決定：

1. 只保存會改變未來代筆結果的最小公開證據。
2. 沿用 [exploration-workflow.md](exploration-workflow.md) 的 commit boundary，只處理
   本輪更新的 `learning/` 檔案；不明變更依 `tidy-workspace` 處理。
3. 同步到 profile 指定的公開 dotfiles 程式碼庫。

## Topic 格式

`topics/<context-slug>.md` 使用 lowercase ASCII 與 hyphen 命名，格式如下：

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

## Evidence 與升格

符合任一條才可放進 `Confirmed choices`：

- 使用者明確表達喜歡、排斥或指定寫法。
- 使用者明確接受 agent 的寫法。
- 至少兩組獨立修改支持同一偏好，且沒有反例。

其他觀察先放 `Working hypotheses`。Project-specific observation 先進 topic；只有跨
至少兩種情境仍成立，或使用者明確宣告為通用偏好，才升格到 `voice-profile.md`。
反例出現時縮窄、降回 hypothesis 或移到 `Avoid`，並保留最小必要 provenance。

開始代寫前讀 `INDEX.md`、`voice-profile.md` 與最接近的 topic。完成有意義的修改後
才更新 records；沒有新 evidence 就不動檔案。
