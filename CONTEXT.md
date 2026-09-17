# CONTEXT.md — dotfiles 共用詞彙

這個 repo 裡人與 agent 講話、命名都用這套詞；同一件事不換第二個名字。其他 repo 各自維護自己的 `CONTEXT.md`。

- **guardrail / SSOT 檔**：會改變 agent 行為的檔案：`CLAUDE.md`、`AGENTS.md`、`settings.json`、skill、playbook。改動要 commit → fresh reviewer → push。
- **shared skill**：放 `skills/shared/<name>/SKILL.md`，由 `scripts/sync-skills.sh` 連到 `~/.claude/skills`、`~/.codex/skills`、`~/.agents/skills`。只給單一 agent 的放 `skills/claude/` 或 `skills/codex/`。
- **controller / worker**：controller 是目前對話的 agent，負責判斷、驗收；worker 是被委派做實作、研究或 review 的 subagent 或 headless CLI。規則在 `delegate` skill。
- **fresh reviewer**：沒有本次工作脈絡的 worker，做 safety review 與 simplify review，逐項回 Keep / Simplify / Drop。
- **preflight / debrief**：`level-up` skill 的實作前對齊與實作後講解。
- **user-profile**：`skills/shared/level-up/learning/user-profile.md`，跨 repo 的教學偏好與類比世界。
- **jargon allowlist**：`hooks/jargon-allowlist.yml`，英文詞彙與台灣用語的 allow / reject 表，pre-commit 會擋。
- **本機 SSOT**：`~/.local/share/machine/machine.md`，本機 host、帳號、工具鏈偏好；不進 repo。
