# Personal Eval Set — Preflight Plan（2026-07-19）

Decisions-first implementation plan，產自 level-up preflight（七關 shotcall 全數拍板）。
類比世界觀：私房賽道（車手＝模型、彎道＝eval case、計時台＝grader、圈速牆＝版本比較）。
詳細教學紀錄在 `skills/shared/level-up/learning/topics/personal-eval-set.md`。

## 1. Decisions（依影響面排序，全部已拍板）

1. **Eval case 形狀＝rubric replay**：凍結任務描述＋輸入素材，驗收標準是 expectations 檢查表。
   golden test（單一標準答案）與難度階梯（同任務疊難）都是其特例。與 skill-creator
   `evals.json` 的 `prompt` + `expectations[]` 同形，基建直接吃。
2. **存放＝混合制**：skill 專屬 eval 放 `<skill>/evals/`（skill-creator 原生位置）；
   跨 skill／無 skill 的能力題放中央 `evals/`。命名一律複數 `evals/`。
3. **打分＝分層計時**：可程式驗證的 assertion 用 script 硬判 → 其餘交 grader agent →
   品味類（encoded preference）彎道掛「人工抽查」標記，驗車日只抽看這些。
4. **校準＝判例庫制**：人工抽查不滿意 → 歸檔判例（replay＋人工判決＋理由）→
   優先升格成明文 expectation，升不了才調 grader prompt → 改完整本判例庫重考
   過關才恢復對 grader 的信任（防打地鼠式過擬合）。
5. **入庫＝先全私有**：`evals/` 掛 private remote 的 git submodule（沿 nvim 前例）。
   累積夠了再議把 prompt/rubric 層開源、敏感素材留私有；去識別化成本延後到開源日才付。
6. **版本比較＝圈速牆＋條件複賽**：benchmark 按「模型＋日期＋彎道版本」歸檔；
   同彎道版本才可比，rubric 改版即作廢該彎舊紀錄。意外結果（新旗艦輸舊模型）
   才加開新舊模型當場對跑＋blind comparator 複賽。
7. **觸發＝手動鑰匙**：user 喊「驗車」→ 管線全自動（每組跑 3 輪、收 metrics、
   analyzer 報告、圈速牆歸檔）；抽查與拍板的儀式部分保留人工。
8. **養護＝驗車日順檢**：驗車日尾聲附巡檢單（analyzer notes 標飽和彎、非鑑別
   assertion、廢路），當場拍板：退役進名人堂／轉職 fidelity test／加難度層／除籍。

## 2. Confirmed intent

- 三合一目標：(a) 新模型 30 分鐘內判斷「對我變強 vs benchmark 灌水」；
  (b) 找能力邊界決定放手/盯梢；(c) 撞邊界是可重複的好玩儀式。
- 總 lens：**eval set＝個人護城河**。核心洞察（Anthropic skill 二分法）：
  capability uplift 題人人會過期；encoded preference 題（品味/流程）才是別人
  抄不走的部分 —— user 最愛的 chill/level-up/html* 全屬此類。
- 品味複利機制：每次人工抽查的不滿意，都要逼一條隱性品味變成明文 rubric 資產。
- 路感彎「洩題進 skill」＝畢業非作弊：該彎轉職為 skill fidelity test，掛回該 skill 的 evals/。

## 3. Known unknowns

- Mac 本機 Claude Code / Codex chat history 的實際格式與挖掘方式（挖題訊號已定：
  糾正瞬間、重試迴圈、user 親手改的 diff；管線待 Mac 到手後探）。
- grader agent 寬鬆偏誤的實際嚴重度 → 判例庫要累積多少筆才夠校準。
- 一次驗車日的 token 成本（決定每組 3 輪是否要降）。
- private submodule 的 URL 會在 .gitmodules 公開露出 → 可接受度待確認；
  install.sh 與外人 clone 須容忍 submodule 缺席。

## 4. Implementation outline（Mac 到手後的一期）

1. 開 private repo，掛進 `evals/` submodule；目錄骨架照 skill-creator schema
   （`evals.json`、`graderbook/` 判例庫、`wall/` 圈速牆歸檔）。
2. 憑記憶＋現有 chat history 手工播種 5–10 條彎道（先不等自動挖題管線）。
3. 接線 vendored skill-creator（`skills/claude/skill-creator/`）的 grader/
   benchmark/aggregate/viewer，跑第一次「驗車」對現任模型 —— 這一輪就是第一台幽靈車。
4. 首次驗車日走完整儀式：抽查路感彎 → 有皺眉就開判例庫第一筆 → 巡檢單收尾。

二期（另議）：skill 改動自動回歸受影響彎（CI 感）、chat history 自動挖題管線、
開源 split、per-skill evals 鋪開。

## 5. Mechanical refactors（可放心交給 agent）

- 目錄鷹架、.gitmodules／install.sh 的 submodule 容錯、schema 檔照抄。
- benchmark 歸檔的命名慣例（`<model>-<date>-<track-version>`）與圈速牆索引生成。
