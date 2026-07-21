# Codex Machine Actor Routing

## Learner Goal
- 理解多台 Mac 上 Codex actor 的可路由身份、Codex hook 心智模型與關鍵路徑，確認變更可安全 push。

## Current Level
- Status: mastered
- Last updated: 2026-07-16
- Confidence: 短版 debrief 3/3 通過

## Evidence
- 2026-07-16: 主動指出 `mac-cdx` 無法精準表達「讓 M1 Codex 等待、把工作委派給 M4/M5 Codex」；選擇以 `m1-cdx` / `m5-cdx` 作為可直接下令的 actor address。
- 2026-07-16: 正確區分 actor address 與 shared policy；拍板 `m1-cdx` / `m5-cdx` 共讀 `local-agent-playbook.md`，並提出需要時由 shared playbook 路由到 machine-specific overlay，而非複製整份共同規則。
- 2026-07-16: 正確判斷未 trust 的 project-local `SessionStart` hook 會被跳過並警告，因此不會注入 `m1-cdx` developer context。
- 2026-07-16: 正確完成檔案職責 mapping：`.codex/hooks.json` 管 lifecycle、`detect-env.sh` 管 identity、`local-agent-playbook.md` 管 shared policy、`playbooks/machines/<machine-id>.md` 管 public-safe machine overlay。

## Known Gaps
- 尚未實機走過新 task 的 `/hooks` trust UI；心智模型已掌握。

## Teaching Notes
- 使用航空塔台呼號框架。
- 短版 debrief，decisions-first；一次一題。

## Next Suggested Levels
- 未來新增第二台 Mac 時，實作 delegation transport 與 actor availability discovery。
