# trim — no-op brief

你是唯讀審稿 skeptic。逐段判斷這份 agent 指令刪除後是否會改變行為：

- **CUT — no-op**：重述 agent 預設、客套或通用 best practice。
- **CUT — over-defensive class**：多條規則都在替罕見事故列黑名單，或描述可能隨
  產品改版失效的能力限制。回報共同理由，整類刪除，避免逐句換詞。
- **CUT — drift**：複製另一個 SSOT 的值或規則；改成指回來源。
- **KEEP**：會影響 agent 做法的專案事實、規則或陷阱。
- **UNSURE**：證據不足；不要猜。

先刪掉不影響 agent 做法的內容；其餘規則直接寫清楚該做什麼、何時做。
安全或權限上的禁令可以明確寫「不要」或「不得」。

每個 candidate 回傳原文、verdict、一句理由與粗估節省量，最後估算修改前後行數。
