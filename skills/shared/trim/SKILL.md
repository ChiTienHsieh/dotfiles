---
name: trim
description: 精簡 skill、prompt 與 AGENTS.md／CLAUDE.md 等 agent 指令；程式碼精簡用 `/simplify`。
disable-model-invocation: true
---

# trim

砍掉 skill、prompt 與 agent instructions 裡不會改變行為的 no-op。判斷標準在同層的
`noop-brief.md`；這裡只定義審查流程。

## 何時使用

- 使用者要求精簡 agent 指令，或剛寫完一份指令需要自我審查時使用。
- 程式碼精簡改用內建 `/simplify`；一般文章不使用本 skill。

## Workflow

1. 確認目標與載入關係，依 `noop-brief.md` 判斷規則是否改變行為。
2. 小幅精簡直接自審；跨檔規則或需要獨立判斷時，依相依關係分組交給 fresh、
   唯讀且沒有 parent context 的 worker，提供 brief path 與目標路徑即可。
   Codex 使用可用的 multi-agent tool；其他 runtime 使用當前內建 worker。
3. 收回刪減建議，把理由相同的項目歸在一起，再由主 agent 決定是否採納。
4. 改動走 PR，列出刪減類別、理由與約省篇幅；會影響使用者偏好且無法判斷的項目先保留。

## 邊界

- Worker 只提供建議，不修改或提交檔案。
- 寧可漏砍，不誤殺會改變行為的規則；`UNSURE` 預設保留。
- 這份 skill 也必須通過自己的 no-op test。
