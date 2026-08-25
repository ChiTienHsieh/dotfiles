---
name: learn-my-voice
description: 透過持續共同編輯 Markdown、local explore branch checkpoints 與可成長的 local-only learning records，學習並套用使用者的寫作聲音。使用者想讓 agent 越寫越像自己、減少重打時使用；不要用於被動監控、一般一次性校稿或推測人格。
---

# Learn My Voice

這個 workflow 學的是可觀察的寫作選擇，不是假裝擁有使用者的經歷或身份。它只
在目前 turn 被喚起時 fresh-read；不得聲稱會在背景持續監看。

## 兩層紀錄

### 1. Project exploration

在共同編輯文件所屬 repo 的 local explore branch 保存 revision provenance：

- allowlisted Markdown 文件；
- `.explore/<topic-slug>/VOICE.md`；
- 分開的 `explore(user|checkpoint|agent|voice): ...` commits。

需要建立 branch、判斷 authorship 或 checkpoint 時，讀
[references/exploration-workflow.md](references/exploration-workflow.md)。

### 2. Persistent learning

跨專案可重用的偏好放在 package lifecycle 之外的 per-user local data root。開始
代寫前依 [references/learning-records.md](references/learning-records.md) 解析、讀取
或建立 records。若 sandbox 不允許寫入，只要求該 exact data root 的 scoped
permission；不得改存到未宣告的全域位置。

## 啟動前

啟動前先確認：

- 共同編輯的 Markdown 路徑；多檔時建立明確 allowlist。
- 目前 Git branch、working tree、最近 commits 與可能的 ref 衝突。
- 使用者是否可能同時編輯同一檔案；不能確認就每次動筆前重新讀檔並縮小 patch。
- 目標文件與待 checkpoint 內容沒有 token、password、private key、未公開個資或
  其他不該進 Git object database／learning record 的內容。

首次建立 explore branch、commit 或寫入 persistent records 前，先向使用者說明
exact paths、會留下的 Git history／local data，並取得明確授權。未獲授權時退化成
不 checkpoint、不寫 persistent records 的共同編輯模式。

Local-only 不代表 secrets 可以安全 commit。若內容不適合留存，停止 checkpoint，
但仍可在不保存該 evidence 的前提下協助當次寫作。

## 每個 turn

1. Fresh-read branch、status、allowlisted diff、最近 explore commits、project
   `VOICE.md` 與相關 persistent learning records；摘要不能代替。
2. 若 agent 動筆前已有 target changes，先依 provenance 保存 user 或中性
   checkpoint；來源不明的變更不可標成 user evidence。
3. 套用和當前情境相符的 confirmed choices，並以最小、連貫的一段續寫。保留
   使用者的事實與觀點，不補造經歷或主張。
4. 寫檔前再讀目標段落；內容已變時吸收新版本，不用舊 snapshot 覆蓋。
5. 把 agent revision 與 voice inference 分開 checkpoint。出現無法解釋的新變更
   時，不還原、不冒認 authorship；改做中性 checkpoint 或停下釐清。
6. 只有本輪新增可引用 evidence 時才更新 project／persistent records。

Persistent record 寫入若沒有可用權限，project checkpoint loop 仍可繼續，但必須
明確回報 persistent update 未完成；不得聲稱已跨專案記住。

## 如何套用 voice

- 優先套用使用者明說或反覆證實的選擇，例如選材角度、中文／English 取捨、
  句子節奏、直白程度、幽默、結構與讀者假設。
- 依情境調整 register；私人筆記的口氣不能直接搬到求職信或公開文章。
- Working hypothesis 可以小幅試用，但要讓使用者容易否決；不得當成固定人格。
- 不推論敏感特質、健康、政治立場或未明說的個人經歷，也不把錯字、口述贅字
  或一次性的情緒措辭機械式模仿成特徵。
- Project `VOICE.md` 與 persistent profile 衝突時，以較新、情境較接近、
  provenance 較強的 evidence 為準；不要靜默覆寫舊規則。

## Handoff 與離開 exploration

每輪只需回報本次保存的 content checkpoints、目前採用的 1–3 個 voice choices、
未處理變更與下一個最小共編區塊；不要把 learning bookkeeping 倒進聊天。

使用者說完成時，列出 branch、base commit、目標文件、project voice-notes path 與
未確認 hypotheses，讓使用者另行決定保留 branch、帶走成品 commits 或刪除探索
資料。刪 branch 不會立即清除 Git object database 裡的內容。未經針對 exact branch
與內容範圍的明確確認，不得 push、merge、rebase、開 PR、刪 branch，或把
`.explore/**` 帶進正常 branch。
