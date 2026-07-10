# 投資配置：39w 全球股容器 + 避險 mental model

> **這份是 Fable（2026-07-06，quota 見底前）留給下一位教學 AI（預設 Opus）的交接筆記。**
> 性質＝preflight 產物：決策 Fable 已先做完（附理由），Opus 的任務是帶 user 一關一關重走這些決策點，
> 每關「教一個概念＋拍板一個決策確認」。user 可以推翻任何一條 —— 這是他的錢。

## 背景（一句話版）
user 九月辭職做一年零收入 indie 實驗。現金 115w：50w 存糧不動，65w 閒錢投資。
既有 170w 主要在 0050。三重集中：薪水（啟碁/網通硬體）＋房子（台灣）＋0050（台灣科技）全壓同一注。
先前 session（2026-07-05 chat）已交付 65w 配置表，其中 **39w 給全球股** —— 本課程就是在解「這 39w 買哪個容器」。

## 教學進度（接關資訊）
- 類比：L1-L2 舊楓之谷；L3-1~3 寶可夢戰隊；**L3-4 起改用 k8s/Azure（user 主動要求，precision 議題用軟體類比更順；注意 user 只熟 on-prem k8s + Azure，不熟 AWS/multi-cloud）**。深度 A2 紮實打底；7 關地圖。
- 已完成：L1 四大 NPC、L2 三條路、L3 稅四關（3-1 註冊地決定課稅、3-2 美國兩道稅、3-3 愛爾蘭租稅協定、3-4 台灣 009826）、L4 配息 vs 累積、L5 存取路徑/保管（複委託=台灣跳板機 SPOF vs IBKR=個人 kubeconfig 直連）、L6 bitcoin 爆炸半徑（四紀律＋通路拍板）。MCQ 全過。教材：`invest-L6-bitcoin-blast-radius.md`。已修正 user 誤會：股息稅 ≠ 資本利得稅（30% 只咬股息）；custody 金融語意（已進 vocab REJECT 表）。
- 教材：L1-L2 為 HTML；**L3 起改 markdown**（token 效率，user 拍板），symlink 進 Obsidian vault `~/Documents/ObsidianVault/level-up-invest/`，用 `open "obsidian://..."` 開。檔案在 `~/lyfe-online/explainer/invest-L3-*.md`、`invest-L4-*.md`、`invest-L5-*.md`。
- 工作流（user 設計）：writer subagent（sonnet）寫 → **每關必 spawn 高標準 Opus fresh-eyes reviewer，可直接改檔** → CC 校對 → 聊天室出 MCQ（新情境，不可重複教材例子）。
- 教材品味：密度「一口一關極薄」（~70 行）；**L4 被嫌 boring，診斷=沒有決策沒有懸念；L5 用 DR 演練情境開場後 user 買單**——每關要有 stakes/戲。MCQ 不可洩題、bookkeeping 不進聊天。

## Fable 的決策（Opus 帶 user 逐關重走）

### D1：39w 容器 → ✅ **已拍板（2026-07-09/10）：VWRA，但透過 IBKR，推翻 Fable 的「富邦複委託」**
- VWRA = Vanguard FTSE All-World UCITS ETF（累積型，愛爾蘭**註冊**，LSE 掛牌——課稅看註冊地不是掛牌地，Opus reviewer 修正過 Fable 的用詞）。
- VWRA 本身：user 於 L3 結束時確認選 VWRA（稅務理由同 Fable：股息預扣 15%、無美國遺產稅、含稅總成本最低）。
- **通路改 IBKR**（L5 拍板），推翻理由有二，都是 Fable 沒掌握的事實：
  1. user 的原始動機是去台灣集中化＋明確問過「打起來富邦還讓我領錢嗎」——複委託存取路徑保留台灣單點故障，與初衷矛盾。
  2. 查證後 IBKR 開戶/App/客服都有繁體中文（Fable 假設的英文門檻不成立）；且英股費率 ~0.05% 低消 £1，比富邦議價後 0.15%~0.25% 低（雖然 39w 級距下費用差距一年不到千元，非決勝點）。
- 已教的 caveat：IBKR 保的是「資產不被台灣端卡住」，非「戰時人在台灣照常用錢」；帳戶要保持活動；繼承程序較麻煩（程序麻煩非課稅）。

### D2：配息 vs 累積 → ✅ 已拍板：**累積型**（L4 過，user 嫌這關 boring——因為 VWRA 出廠即累積型，沒有真決策）
- 已教清楚：境內累積型=直接免稅；境外累積型=遞延＋自選實現年度＋避開「海外財產交易損失不能抵海外股利所得」陷阱，不是免稅。

### D3：真避險 = 承認三重集中
- 決策確認目標：user 能自己說出「薪水＋房＋0050 是同一注」，並確認 39w 海外倉位就是避險本體，不是加菜。

### D4：bitcoin → ✅ 已拍板（2026-07-10，L6 過）：**四條紀律確認＋通路選 IBIT via IBKR**
- 四條紀律 user 已懂：現貨=有 resource limit 的 pod（虧損封頂）、1-2% 上限=canary 配額（65w 的 1-2%≈6,500~13,000）、心理歸零計、絕不槓桿/CFD=唯一會賠超過本金（privileged pod 拖垮 node）。
- 通路：user 自選 IBIT via IBKR，動機明確=「參與價格上漲」非「體系外資產」（user 原話 prefer 最省事那條）。查證過的前提：複委託虛擬資產 ETF 限專業投資人（財力 3,000 萬）user 不符；IBIT 美國註冊有遺產稅規則但金額遠低於 $60k 門檻。

### D5（已拍板，不用重教）：eToro $300 給 AI agent 玩 → 核可
- user 的範式：隔離帳戶＋金額有上限＝爆炸半徑受控；紅線只有一條 = 別把主帳戶/全部身家的鑰匙交出去；若小錢翻大額，盡快出金落袋。

### D6：進場節奏 → ✅ 已拍板（2026-07-10，L7 過）：**user 推翻分批，改「單筆＋operational canary」**
- user 自我盤點推翻 Fable 的「分 3 批」：不看盤、跌了只想加碼、要 set-and-forget（「錢放在市場裡大於放在戶頭」是他自己說的核心信念）——分批的心理保險前提對他不成立，取數學優勢（單筆 ~2/3 勝率）。
- 最終形式：先 1-5% 小單當 **smoke test**（驗證電匯→換匯→下單 pipeline 通不通），幾天內補足其餘 95-99%。間隔是驗證用的幾天，不是猜市場的幾個月。
- user 的長期監控偏好：不想佔用 mental RAM，考慮 cron/LaunchAgent 提醒、或「想度假時才看價」的贖回啟發式——與累積型邏輯一致。

## 課程狀態：✅ 七關通關（2026-07-10）。六大決策全數拍板，教材 L1-L7 齊，runbook 在 `invest-L7-launch-runbook.md`。

## Known unknowns（Opus 教學前先查證，別背 Fable 的數字）
- 富邦複委託是否能下 LSE 英股（VWRA）＋最低手續費/費率。
- 稅務數字全部要 web 查證當年度：15%/30% 預扣、美遺產稅 $60k 門檻、台灣海外所得課稅門檻、VWRA/VT 費用率。
- 009826 的正式名稱/追蹤指數（引用前再確認一次）。
- 65w 完整配置表精確數字在 2026-07-05 chat，本檔只保證「39w 全球股」這一項；user 若要重看整表，重新推導不要憑印象背。

## User 檔案重點（教學相關）
- 英文閱讀慢（約國中程度），縮寫沒展開會直接卡住。
- 遊戲化超有效；教材無聊＝失敗。開課前必讀 `learning/user-profile.md`。
- **不熟 message broker/Kafka/RabbitMQ/Celery，別拿來當類比**（有前科）。
- user 會抓 fact drift：任何具體數字先查再講。
