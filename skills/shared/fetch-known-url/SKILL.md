---
name: fetch-known-url
description: 將 chatgpt.com/share 的公開對話擷取成 Markdown 與 JSON；讀取或整理這類分享連結時使用。
disable-model-invocation: true
metadata:
  short-description: Fetch a supported URL into readable files
---

# Fetch Known URL

## 支援的網址

- `chatgpt.com/share/...`：抓原始 HTML，取出分享對話的資料，寫成 Markdown 加 JSON。

不要隨手加新的網址類型。要學新類型時，先看它抓下來長什麼樣、找到穩定的內嵌資料或乾淨的內容來源，再加 parser 並更新這份清單。

## 流程

1. 確認網址符合支援的類型。
2. ChatGPT 分享對話用 `scripts/fetch_chatgpt_share.py`。
3. 輸出放在任務目錄下，通常是 `fetched-chatgpt/`。
4. agent 讀 Markdown，後續結構化處理用 JSON。
5. 盡量留著原始 HTML，之後改 parser 不用重抓。

## 抓 ChatGPT 分享對話

執行：

```bash
python3 "${CLAUDE_SKILL_DIR:-${CODEX_HOME:-$HOME/.codex}/skills/fetch-known-url}/scripts/fetch_chatgpt_share.py" \
  "https://chatgpt.com/share/SHARE_ID" \
  --out-dir fetched-chatgpt
```

輸出：

- `chatgpt-share-<id>.html`：原始 HTML
- `chatgpt-share-<id>.json`：結構化的 metadata 與訊息
- `chatgpt-share-<id>.md`：給 agent 讀的乾淨逐字稿

結構化 parser 失敗或逐字稿看起來不完整時，留著 HTML、改跑啟發式的抽取器：

```bash
python3 "${CLAUDE_SKILL_DIR:-${CODEX_HOME:-$HOME/.codex}/skills/fetch-known-url}/scripts/extract_chatgpt_share_text.py" \
  fetched-chatgpt/chatgpt-share-SHARE_ID.html
```

啟發式抽取的結果只當參考筆記，不是正式逐字稿。需要精確又抽不完整時，明講。

sandbox 擋網路時，用合適的網路核准重跑抓取指令。
