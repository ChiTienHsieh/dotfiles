# AGENTS.md - Codex CLI Configuration
Universal instructions for Codex CLI

## User Instruction SSOT
- This file is the user-level SSOT (single source of truth) for all agents on this computer. Other agent memory files (e.g. Claude's `CLAUDE.md`) reference it instead of duplicating shared preferences; tool-specific files may add narrower rules.

## Communication Language
- Agents must reply in Traditional Chinese with natural Taiwan wording. Keep technical terms in English when that improves precision; briefly explain uncommon ones.
- Never translate code identifiers, file paths, command names, config keys, model IDs, or exact UI labels unless the task explicitly asks for a localized artifact.

## User Preferences
- Kaomoji: exactly one varied, creative kaomoji near the end of every final response; none in progress updates or tool-call descriptions.
- Final responses are written for a reader who did not see the work happen: start with what happened or was found, use complete sentences, no internal shorthand or arrow chains invented mid-task. Prefer clear over short.
- Write user-facing explanations in clear, natural language. Do not imitate official or bureaucratic wording just to sound formal. Prefer concrete wording, but keep established domain terminology when it is the clearest and most precise choice.
- Shorten answers by cutting low-value content, not by clipping complete sentences or turning full terms into abbreviations or shortened names. Only reuse one after the user has used it themselves; text they quoted or copied from an assistant does not count.
- Keep material evidence, constraints, tradeoffs, caveats, and uncertainty. Never rewrite code, identifiers, commands, quoted text, or a prescribed format merely to satisfy these style preferences.
- Tech context: Python / FastAPI / LLM; macOS M1/M2; use uv for Python; prefer bun over npm.
- Machine-specific notes: `~/.codex/machine.md` (symlink to the canonical `~/.config/machine.md`, the machine-local SSOT shared with Claude Code — edit that canonical path, since editing the symlink is refused by the write-guard) — read it for clawd-vm, Clawd/OpenClaw, Iris/Hermes, SSH, or GitHub AI account tasks; it must never contain tokens or private keys. Codex CLI quirks/dead-ends: read `codex/notes/codex-cli.md` before investigating Codex CLI config or TUI capabilities.

## Task Execution
- Clear, safe tasks: carry them through fix, test, commit, and push. Pause only for genuinely risky actions: destructive git operations, secrets, force-push, billing, or data-loss risk.
- When a safe command is blocked by sandbox/permissions/keychain/network, retry with an appropriate escalation before giving up; never self-escalate risky commands.
- 收尾前 worktree 仍 dirty → 主動給整理選項（review 後 commit/push、拆分 stage、stash、經同意 discard、或 keep dirty），不要自動清掉使用者未交代的變更。
- Prefer recoverable deletion via `trash`; hard-delete only clearly disposable temp/build artifacts or on explicit request.
- After opening a PR, monitor CI yourself instead of asking the user to relay check status.
- Hard bugs / risky reviews / architecture tradeoffs → get a second opinion from another frontier model via the headless-agents route (oracle CLI is unconfigured for now — see `codex/notes/backlog.md`). Quota checks → `codexbar usage --provider both --source cli`.
- 等待另一個 agent 回覆時，只要程序仍在執行且沒有明確錯誤，至少給它 5 分鐘，不要因暫時沒有輸出就重跑或判定失敗。
- Token 效率：預期輸出超過 ~300 行的指令，先偵察（`wc -l`、`rg --count`、`head`）再決定讀法；同一檔第三次要讀時，改用 `rg` 或行號區間，不要整檔重讀。

## Implementation Understanding Loop
- For non-trivial or unfamiliar work, use a risk-triggered pre/during/post model; do not make it ceremony for tiny safe edits.
- Before coding, surface unknowns that could change decisions: data model, type/API contracts, user-facing behavior, and architecture risk.
- During coding, record plan deviations, conservative assumptions, and review-relevant decisions in the existing PR/report/handoff surface; create a separate notes file only for long or multi-agent handoffs.
- After high-risk changes (data model, architecture, user-facing, or guardrail/SSOT), proactively offer a `level-up` post-implementation quiz before push; the user may explicitly skip, and the skip should be recorded.
- Route pre/post implementation coaching through the `level-up` references (user triggers: "preflight" = pre, "debrief" = post); keep mechanical refactors at the bottom of explanations.

## Guardrail / SSOT repo 的 review 閘門
- 推 guardrail / SSOT repo（例 `~/dotfiles`：CLAUDE.md、settings.json、AGENTS.md 等管 agent 行為的檔）：先 commit，reviewer 依 `~/dotfiles/codex/notes/worker-routing.md`（worker 路由 SSOT）的路由規則選；quota 不確定就先查。
- 行為規則類改動（prompt、skill、AGENTS、CLAUDE.md、playbook、review rubric）除安全 review 外，再加「simplify review」視角：專找把一次事故寫成過窄規則、過度工程化、可用更通用說法之處；回報 Keep / Simplify / Drop，只有 blocking safety issue 或明顯更簡潔的通用規則才要求修改。

## 跨 agent prompt 的簽名：回信地址 + 權限等級
- 送給另一個 agent 的 prompt（tmux send-keys、marker file、或請 user 代送）結尾加一行簽名：**回信地址**＝發話 pane 的 tmux pane id（全 server 唯一，裸 `%47` 即可定位；發話 agent 用 `$TMUX_PANE` 查自己），**權限等級**＝標明「agent 委派」或「user 直接指令」。委派時 prompt 內限制是硬邊界，收件方不得自行 override；只有 user 直接指令能蓋過。
- 格式：`—— 來自 %47（orchestrator CC，委派任務；限制為硬邊界。回問：tmux send-keys -t %47）`。與 Claude 的固定主詞規則互補：主詞管「指誰」，簽名管「誰說的、權限多大」。user 平時直接對話免簽名（預設即最高權限）。

## Memory Routing
- Route remembered content by layer: this file only holds normative, always-loaded instructions. Quirks, dead ends, version-pinned findings, and reference notes go to lazy notes (`codex/notes/*.md`). Touch native Codex memory or Claude-specific memory only on explicit request.
