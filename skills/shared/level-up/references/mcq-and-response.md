# MCQ, Shotcall, and Adaptive Response

Ask exactly one substantive question at a time. The chat question is the sole
authority for progression.

## Choose the Question Type

- **quiz:** tests understanding and has one correct answer. Use by default for
  pure teaching.
- **shotcall:** settles a real design decision. Use by default for preflight and
  debrief decision points; the learner's pick is the decision, not a guess at a
  hidden correct answer.

The learner may request either type by name mid-session.

## Shared Format

- Use bold for the question, not heading syntax.
- Put each option on its own line without blank lines between options.
- Match difficulty to the current level and selected depth.

```markdown
**問題: <question>**

A) <option A>
B) <option B>
C) <option C>
D) <option D>

---
```

## Quiz Anti-Tells

Make the learner reason instead of reading the shape of the answer:

- Vary the correct position genuinely across A/B/C/D. Check the previous 2–3
  levels, spread positions roughly evenly across the session, and choose a
  different slot when a pattern is forming.
- Keep position history only in session working memory; never persist it.
- Keep all options roughly equal in length. Put the full justification after the
  answer, not in the correct option.
- Make three options plausible through real misconceptions, half-truths, wrong
  layers, or true-but-irrelevant claims.
- At depth 1, softer distractors are acceptable. At depth 2–3, use near-misses
  rather than strawmen.
- Exactly one option may be deliberately absurd for fun; it must not become
  accidentally correct.

## Shotcall Contract

- Offer at least three serious, defensible options with real tradeoffs. A joke
  option may remain but does not count as one of the serious choices.
- Mark the agent's recommendation with ★ and one concise reason. Recommendation
  position may be explicit, but option lengths should remain comparable.
- Teach the relevant concept and hidden cost before asking; a bare poll is not a
  preflight.
- Treat the learner's choice as authoritative. There is no wrong-answer flow.
- Accept a better out-of-list option or principle and record its substance as
  the decision.
- Record the decision content, never the option letter.
- Ask one shotcall per turn.

## Respond to a Quiz

### Correct

Confirm briefly, explain why it works, then advance and preview the next level.

### 答錯

語氣一樣鼓勵，留在同一關。換一個真的不一樣的角度重講：職場鬼故事模式就換一個事故（Ben 弄壞別的東西），類比模式就換一個場景。不要把同一段解釋換幾個字就重貼。然後出一題新的檢查題；只有會影響後面怎麼教的時候才記缺口。

重試通過後，在給學習者看的進度表把這關標「逆轉」，收尾慶祝會特別標這幾關。

Use this miss ladder:

- 2 misses: use a simpler analogy or narrower example.
- 3 misses: isolate the missing prerequisite.
- 4+ misses: ask whether to split smaller, pause, or switch to a simpler concept.

## Respond to a Shotcall

Confirm the chosen tradeoff, explain its main consequence, and silently record
the decision. In debrief, preserving the implemented choice means it can proceed;
overriding it creates follow-up correction work. Do not label either choice
correct or wrong.

## 定位小測驗

學習者說某關太難，或開課時摸不清學習者的起點，就先用定位小測驗找出哪裡已經會、哪裡要補。目的是定位，不是考倒人；開頭講一句「先問三題，看你現在站在哪」，讓學習者知道答錯也沒關係。

- 通常三題，一次只出一題，學習者答完才出下一題。三題各打一個這門課接下來最需要的先備知識，不要三題都在考同一件事。
- 學習者回「不會」或「用猜的」都是有效答案，照樣記成缺口；說用猜的，就算猜對也記成缺口。不追問，直接出下一題。
- 答錯不走上面「答錯」的重講流程：記下缺口，教到那關再補。
- 學習者作答時順手補的推理（例如「這要看設定」）比選了哪個選項更看得出程度。回應時點出那句推理好在哪，肯定它。
- 三題答完，用一兩句話總結哪些已經會、哪些要補，接著說課程怎麼照結果調整：哪關前面插一關補、哪關講快一點。進度表跟著改。

答對不等於可以跳關。答對只代表學習者大致懂那個概念，不代表知道自己那邊的現況，也不代表知道怎麼參與這個決定。想跳過某關，先問學習者「這關要跳過嗎？」，學習者說還想聽就照教。曾經有學習者三題全對，agent 就自己跳過「網路規則貼在誰身上」；其實學習者還不知道自己那邊現在怎麼設，也不知道怎麼參與決定。
