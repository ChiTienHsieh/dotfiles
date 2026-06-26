---
name: trim
description: Hunt and cut no-ops from a skill / prompt / agent-instruction file using fresh-eyes sub-agents. Use when the user wants to simplify, trim, declutter, or shrink a skill or prompt, or asks "is this prompt bloated", "remove the no-ops", "this skill is too verbose". Spawns one skeptic sub-agent per target file that runs the no-op test line by line (delete it — does the agent's behavior change? no → cut) and returns a punch list of candidate cuts; the main agent reviews and applies via PR, never silently. Named `trim` to not collide with the built-in `/simplify` (which trims CODE, not prompt prose).
---

# trim

砍掉 skill / prompt / agent-instruction 檔裡的 **no-op**——那些不管刪不刪、都不會改變 agent 行為的句子。no-op test 的判準放在同層的 `noop-brief.md`；這裡只定義怎麼用 fresh-eyes worker 系統化地跑。

## 何時用 / 不用

- **用**：user 說某個 skill/prompt 太肥、要精簡、要 declutter；或剛寫完一個 skill 想自我審查；或定期掃 `.claude/skills/*`。
- **不用**：改 **code** 的精簡 → 內建 `/simplify`。文章散文 → tribunal。這把刀只對 **agent 指令類散文**（SKILL.md、playbook、prompt、CLAUDE.md/AGENTS.md 這種）。

## Workflow

1. **定目標**。User 指定哪個檔 / 哪個 skill；沒指就問或掃整個 `.claude/skills/`。一個目標檔 = 一個 sub-agent。
2. **Fan-out skeptic workers**。每個 worker 拿**一個檔 + brief path**，**零 parent context**——它不該知道每行「為什麼在那」，才測得出哪行其實是空話。Claude 可用 `Agent` tool（`general-purpose` 或 `Explore`）；Codex 可用可用的 multi-agent tool，或用 tmux 開一個 read-only Codex worker。多檔就平行開多個 worker。
3. **收 punch list**，自己過一遍（sub-agent 會誤殺 load-bearing 行——尤其專案特有事實、指回 SSOT 的值）。
4. **改動走 PR**，逐項列「砍什麼 / 為什麼是 no-op / 省多少」，**絕不靜默亂砍**。爭議行留著、標記、問 user。

## sub-agent 的 brief：放在檔案，別 inline 進 context

brief 全文在同層的 `noop-brief.md`。主 agent 可以依 runtime 規則解析或讀取這個檔案，但派給 worker 時只傳 brief path；不要把 brief 內容 inline 進 worker prompt，避免把 prompt 變肥。

先解析 skill-local brief path，再把路徑遞給 worker。常見 installed paths：

- Claude：`~/.claude/skills/trim/noop-brief.md`
- Codex：`~/.codex/skills/trim/noop-brief.md`
- Repo source：`~/dotfiles/skills/shared/trim/noop-brief.md`

兩種跑法：

- 叫 worker 自己讀：prompt 一句「讀 `<brief-path>`，照裡面的規則審 `<target>`」。
- 或 `cat <brief-path> | claude -p` / 等價的 worker CLI（再附上目標檔）。

主 agent 全程只持有兩個路徑（目標檔 + brief 檔），brief 內容留在檔裡。

## 鐵規

- **Sub-agent 是 recommender，不是 committer**——它回報 candidate，砍不砍主 agent 決定。
- **寧可漏砍別誤殺**：load-bearing 行被砍會讓 skill 壞掉、比留個 no-op 嚴重得多。UNSURE 一律留。
- **吃自己狗糧**：這份 SKILL.md 本身也該過 no-op test。
