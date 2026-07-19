# Personal Eval Set 框架 preflight

## Learner Goal
- 三合一（user 明說三個都要）：(1) 新模型一出，30 分鐘內判斷「對我的工作變強在哪 vs benchmark 灌水」；(2) 找能力邊界，決定哪些事放手全自動、哪些要盯；(3) 撞邊界變成可重複的好玩儀式。
- 加碼 lens：**eval set = user 的個人護城河 (moat)** —— 每關要帶一條 moat 檢查點。
- 深度 3（深挖細節）：版本比較、自動化排程、eval 腐化防治都要進地圖。
- 場景：蓋在 dotfiles repo；未來 Mac 本機讓 Claude Code 讀取 Claude Code / Codex 的 local chat history 當挖題素材。這次先抽象框架＋現有 skills。

## Current Level
- Status: learning（preflight 進行中，Level 0 類比未定）
- Last updated: 2026-07-19
- Confidence: n/a

## Evidence
- 2026-07-19: user 拒絕雙類比制既有 frame，主動要求全新類比（世界觀疲勞訊號？先觀察）。
- 2026-07-19: 類比拍板＝**私房賽道（車廠試車手）**，user 自曝看跑跑卡丁車 (KartRider) 賽事、是爆哥粉絲 → 賽道 frame 可加 KartRider 風味（甩尾、計時、幽靈車）。專有名詞紀律比照 Vainglory：機制層直接用，具體賽道名/數據不可憑印象掰。

## Decisions
- L1 彎道形狀＝**B 規格彎（rubric replay）**：凍結任務＋輸入素材，驗收檢查表打分；A（golden test）與 C（難度階梯）視為 B 的特例。與 skill-creator `evals.json` 的 `expectations` 欄位同形。
- L2 基建接電＝**A+C 混合（user 自提加碼案）**：skill-specific eval 放各 skill 目錄旁（`<skill>/evals/`，skill-creator 原生位置）；跨 skill／無 skill 的能力彎放中央 `evals/` 園區。兩邊共用 skill-creator schema＋grader＋benchmark。
- 命名＝**`evals/`（複數）**：跟 vendored skill-creator 的 `evals/evals.json` 慣例一致，工具零改動直接吃。
- L3 打分政策＝**B 分層計時**：script 硬判 → grader agent → 路感彎掛人工抽查標記。user 隨即自提關鍵問題：抽查不滿意時的校準迴圈（→ L3.5）。
- L3.5 校準迴圈＝**A 判例庫制**：不滿意→歸檔人工判例（replay＋判決＋理由）→先升格明文 expectation、升不了才調 grader prompt→改完整本判例庫重考過關才恢復信任。user 原提案（judge alignment 盲測迭代）納為第二步。

## Known Gaps
- （尚無）

## Research Notes（2026-07-19）
- skill-creator 已 vendored 在 `skills/claude/skill-creator/`，含完整 eval 基建：evals.json schema、grader/comparator/analyzer agents、benchmark mode（pass rate/time/tokens ± stddev）、eval-viewer。
- Anthropic 官方 blog（claude.com/blog/improving-skill-creator...）的 skill 二分法：**capability uplift**（補模型做不到的事，模型變強會過時）vs **encoded preference**（把既有能力照個人流程/品味編排，耐久但要測 fidelity）。user 最愛的 chill/level-up/html* 幾乎全是 encoded preference 型。
- blog 明說 benchmark mode 適合「model updates 後重跑」——正中 user 的 30 分鐘新車驗收目標。

## Teaching Notes
- 航空外殼照常當 preflight 語氣殼；概念類比另選新 frame（候選：私房賽道／木人巷／米其林密探）。

## Next Suggested Levels
- 類比拍板後出地圖骨架：eval 單位形狀 → 存放結構 → 評分方式 → 挖題管線 → 版本比較 → 排程 → 腐化防治。
