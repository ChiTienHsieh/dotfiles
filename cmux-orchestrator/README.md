# cmux-orchestrator

Canonical skill lives in `skills/shared/cmux-orchestrator/`.

## 為什麼住在 dotfiles

dotfiles 是「設定的源頭」（CLAUDE.md、settings.json、cmux、ghostty 等設定都在這）。把 orchestrator 的家設在這個窄目錄，等於把 agent 的預設可寫範圍框在「設定」這一小塊；要動實際專案，必須用 `--add-dir` 明確把該 repo 拉進當下 session。調度站，不是擁有整台電腦的神經中樞。

## ⚠️ 邊界與風險

- **dotfiles 會 push 到 GitHub**（origin: ChiTienHsieh/dotfiles）。任務 log / handoff / 報告一律放 `scratch/`（已 gitignore），不要讓工作內容流進公開 repo。
- **這裡是 guardrail 的源頭**：改 CLAUDE.md / settings.json 會直接影響 agent 規則。好處是能自我調校，風險是被 prompt injection（提示注入）的 agent 可能改寫自己的規則 → 所有改動都會進 `git diff`，push 前務必人工檢查。

`scratch/` is the gitignored task-artifact area.
