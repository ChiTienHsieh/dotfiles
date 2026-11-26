---
name: "daily-loop"
description: "挖最近的 Claude Code 與 Codex transcript，找出能長期用的工作流程改善，再問使用者要採用哪幾項。用在每日回顧、檢視最近的 session，或使用者想找反覆出現的工作流程摩擦時。"
disable-model-invocation: true
---

# daily-loop

挖最近 agent 做過的工作，提出 0 到 2 個能長期用的改善，讓使用者挑要採用哪些。
使用者同意前，不改任何規則、skill、script 或設定。

## 直接的請求轉去負責的地方

- 「記住這個／把這段指引存起來」→ 照目前的 memory policy 做。
- 「收尾這個 session／commit + push」→ `wrap` skill。
- 直接要改設定、權限或 hook → 用負責那塊的 workflow。

## 擷取

跑 helper 時帶 checkpoint，下一次 digest 才認得出哪些是新 session：

```bash
"$HOME/dotfiles/skills/shared/daily-loop/scripts/mine_transcripts.sh" --since 24 --checkpoint
```

用它產出的 digest，不要讀原始 transcript 的 `.jsonl`。script 算出來的訊號只是
頻率提示，不是結論。選項見 `mine_transcripts.sh --help`。

## 流程

### 1. 讀之前的提案

讀 `$HOME/scratch/daily-loop/state.jsonl` 裡的提案紀錄：現在的紀錄用
`kind:"proposal"`；舊格式的提案紀錄可能沒有 `kind`，但同時有 `fingerprint` 和
`status`。檔案不存在是正常的。已經記過的想法不要再提，除非 digest 顯示它明顯又
反覆出現。

### 2. 找候選

依優先順序找：

1. 反覆出現的多步驟互動 → 新 skill。
2. 一再重打的偏好 → 規則，照目前的 memory policy 歸位。
3. 重複手動下的指令或重複跳出的權限提示 → helper／設定改善。
4. 重複的錯誤或重試 → 值得點出來的摩擦，就算還沒有解法。

### 3. 過品質關卡

每個提案都要通過這四項檢查：

- **頻率**：至少在 2 個不同 session 或 2 天出現過。只出現一次的是雜訊。
- **耐久**：對之後的 session 有幫助，不只對眼前這個任務。
- **不重複**：現有規則、skill、之前的提案裡都沒有。
- **具體**：寫明負責的 owner 或目標，以及確切要改什麼。

沒過的候選就丟掉。沒有一個合格就不提案。

### 4. 列出提案並詢問

最多排兩個提案。每個都要寫：

- **改什麼、改哪裡**：類型，加上確切的目標或負責的 workflow。
- **為什麼是現在**：digest 裡的證據和預期收穫。
- **建議的修改**：確切的規則、script 改法或 skill 大綱。

問使用者要採用哪幾項。runtime 有結構化的選擇機制就用它；沒有就用編號清單，加一個
「都不要」的選項。停在這裡，等使用者同意具體項目再繼續。

### 5. 把同意的工作送去對的地方

- 規則或 memory → 目前的 memory／SSOT policy。
- 新 skill → skill 撰寫流程。
- 設定、權限或 hook → 負責那塊的 workflow。
- 現有 helper → 一般有範圍限制的實作。

### 6. 記下每個提案的結果

每一項（包括被拒絕和延後的）都在 `$HOME/scratch/daily-loop/state.jsonl` 追加一行
`kind:"proposal"` 的 JSON：

```json
{"kind":"proposal","ts":"<ISO8601>","day":"<YYYY-MM-DD>","type":"new-skill|rule|script-change","fingerprint":"<stable-id>","target_file":"<path>","summary":"<one line>","status":"accepted|rejected|deferred"}
```

`fingerprint` 由類型、正規化後的目標和 pattern key 組成。`kind:"run"` 紀錄只由
helper 寫，它帶來源前綴的 session key 也由 helper 管；不要手寫 run 紀錄。

## 隱私

digest 裡的片段是使用者 prompt 的原文。digest 和 state 都放在
`$HOME/scratch/daily-loop/` 底下；那個目錄永遠不 commit。
