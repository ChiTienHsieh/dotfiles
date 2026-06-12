---
name: chatgpt-share-fetch
description: 讀取並萃取 ChatGPT shared conversation URL 的可讀 transcript/context。當使用者提供 `https://chatgpt.com/share/...`、要求 fetch/read/study/summarize shared ChatGPT chat，或要從分享對話整理 prompt 時使用。優先於臨時 curl/browser scraping；若萃取不完整要明確說明。
---

# chatgpt-share-fetch

讀取 ChatGPT shared conversation URL，並整理成可用的 transcript notes。重點不是單純下載頁面；`chatgpt.com/share/...` 常回傳 React / React Router shell 加上 streamed hydration data，所以天真地看 `curl` 輸出通常又吵又容易誤讀。

## 使用時機

當使用者提供類似這種 URL 時使用：

```txt
https://chatgpt.com/share/<id>
```

也適用於使用者要求 fetch、read、study、summarize、reuse ChatGPT shared conversation，或從分享對話草擬 prompt。

## Workflow

1. 將頁面 HTML 存到 temporary file：

```bash
curl -L --fail --silent --show-error -o /private/tmp/chatgpt-share.html '<url>'
```

2. 萃取可能的 transcript / context strings：

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/chatgpt-share-fetch/scripts/extract_chatgpt_share_text.py" /private/tmp/chatgpt-share.html
```

3. 把萃取結果當成 notes 讀，不要當成完美 canonical transcript。優先找：
   - 使用者原始 prompt 文字
   - assistant final answer 文字
   - 能解釋任務意圖的 reasoning summaries 或 progress messages
   - 具體檔案、timestamps、requirements、acceptance criteria

4. 檢查完整度：
   - 如果輸出只有 metadata、UI labels、assets 或短片段，視為不完整。
   - 如果任務依賴精準 wording，改用 Browser / Chrome 視覺檢查頁面，或請使用者貼 transcript。
   - 如果萃取不完整，要明確說明；不要假裝已完整讀完 transcript。

## Notes

- 手動 grep raw HTML 之前，優先用這個 skill。直接 grep ChatGPT share page 很容易抓到大型 hydration blobs 和無關 UI strings。
- sandboxed environment 可能需要 approval 才能使用網路。
- extraction script 是刻意設計成 heuristic。ChatGPT share page format 可能改變；script 目標是先提供足夠可讀文字讓 agent 定向，再由 agent 判斷對使用者任務是否夠完整。
