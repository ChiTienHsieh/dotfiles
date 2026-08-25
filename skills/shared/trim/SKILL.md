---
name: trim
description: Use when the user wants to simplify, trim, declutter, or shrink a skill, prompt, playbook, AGENTS.md/CLAUDE.md, or other agent-instruction prose. `trim` cuts prompt prose; `/simplify` cuts code.
---

# trim

砍掉 skill、prompt 與 agent instructions 裡不會改變行為的 no-op。判準在同層的
`noop-brief.md`；這裡只定義審查流程。

## 何時使用

- 使用者要求精簡 agent 指令，或剛寫完一份指令需要自我審查時使用。
- 程式碼精簡改用內建 `/simplify`；一般文章不使用本 skill。

## Workflow

1. 確認目標檔；一個檔案交給一個 worker。
2. 解析 skill-local `noop-brief.md`，把 brief path 與目標檔路徑交給 fresh、唯讀且
   沒有 parent context 的 worker。不要把 brief inline 進 prompt。
   Codex 使用可用的 multi-agent tool；其他 runtime 使用當前內建 worker。
3. 收回刪減建議，把理由相同的項目歸在一起，再由主 agent 決定是否採納。
4. 改動走 PR，逐項列出砍掉的規則、理由與約省篇幅；爭議項目留著問使用者。

## 邊界

- Worker 只提供建議，不修改或提交檔案。
- 寧可漏砍，不誤殺會改變行為的規則；`UNSURE` 預設保留。
- 這份 skill 也必須通過自己的 no-op test。
