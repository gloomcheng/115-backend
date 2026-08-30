# Course Constitution (ELI5) — 網頁程式設計 115

> 依據 `DreambigOu/ELI5 SKILL.md`，TA 明確定義於此，後續所有教材、投影片、互動島皆依此校準。

**TA：College Student · 20 歲 · 零後端基礎**

- 會一點 Python，會貼上 terminal 指令
- 沒分清 `GET` vs `POST`，沒見過 `200 / 404 / 401` 是哪一段回的
- 正在被 AI 直接給答案，貼上能跑但說不清為何

**寫作校準（De-AI，依 `Nanako0129/sepia` 與 O'Reilly Editorial Standard）：**

寫得像人寫的。下筆前先讀本 repo 已定稿的文案抓腔調（`src/pages/index.astro` 首頁、`src/content/docs/readme.md`）——短句、直述、一個結論就一句，不繞。

- 開場貼著具體情況（教室、第一次 `curl`、一條錯誤訊息），不先泛談「這是什麼」。
- 該給判斷就給判斷，講清楚理由；怕錯的地方才加保留。
- 不要「先說明 → 進度回顧 → 總整理」三明治；內容講完就停。
- 數字要帶條件；不要亂編數字跟案例，沒有實際資料就問或留 TODO。
- 刪比加重要。可替換就替換，可刪就刪，少插入。
- 專有名稱、網址、版本號要真實，不要為了「像人寫的」編具體細節。
- 語言分工：文稿敘述用中文；程式碼、變數命名、註解一律英文。

語氣：清楚、直接、尊重。不哄、不酸。長度匹配對象：給一張圖與一個 `curl` 就夠。

---

## O'Reilly Editorial Working Principles (技術編輯工作守則)

教材、講義與文件撰寫時，一律遵循以下 O'Reilly 經典技術圖書編輯準則：

1. **心智模型優先（Mental Model First）**
   - 任何技術概念必須先釐清「角色與責任邊界」（Who asks, what verb, who answers, who is responsible）。
   - 避免直接丟名詞；先建立一問一答的因果關係，再帶出術語。

2. **撥開黑盒，看見傳輸（Show the Wire, Strip the Magic）**
   - 後端沒有魔法。不使用過度擬人化或失真的比喻，直接展示真實純文字封包（Raw HTTP Text / Headers / Payload）。
   - 讓初學者理解：所有的框架、瀏覽器、CLI，底層都在組裝與解析這幾行文字。

3. **可驗證性大於純理論（Observable Proof over Abstract Theory）**
   - 每一段觀念都必須附帶一條讀者能在 Terminal 親手打出並看見輸出的指令（如 `curl -v`、`httpie`、Python 最小實作）。
   - 讓讀者親眼看到狀態碼（`200`, `404`, `500`）是從哪一行 Response 回來的。

4. **精準術語，零多餘修飾（Precision Terminology, Zero Fluff）**
   - 專有名詞標準嚴謹（Request Line、Header、Status Code、Idempotency、Payload）。
   - 嚴禁空洞形容詞（「非常強大」、「極其重要」）；直接用事實和技術限制說明原因。

5. **視角穿透（From Wire to Browser Vision）**
   - 講 HTTP 不能停在抽象網路層，必須穿透到瀏覽器視角：
   - 點擊按鈕或網址 $\to$ 瀏覽器發出 Request $\to$ 後端計算 $\to$ 吐回 Response $\to$ 瀏覽器把 Response Body 繪製成畫面。

---

## Development

When starting the dev server, use background mode:

```
astro dev --background
```

Manage the background server with `astro dev stop`, `astro dev status`, and `astro dev logs`.

## Course curation and learning visuals

Before changing the course site’s visual language or producing lesson diagrams, use
`.agents/skills/course-curatorial-design/SKILL.md`.

Before a new layout direction is implemented, select three examples from
`.agents/skills/course-curatorial-design/references/japanese-web-awards.md`, capture
their rendered pages, and present a reference board for user approval. Never choose a
direction from a regional-aesthetic adjective alone.

The website is a curated learning journey, not a dashboard. Start with the learner’s
question and the sequence of evidence; styling comes after that structure is settled.
For ELI5 diagrams, state one observable claim first and draw only the objects, wire
text, arrows, and short labels needed to prove it. Do not batch-generate or replace
diagram assets until the user accepts one candidate direction.

## Content and layout boundary

Layout work must not edit course copy. Keep visible course text and course data in
content/data modules; keep layout components responsible only for structure,
responsive behavior, and semantic presentation; keep route pages responsible only for
composition. Before a visual refactor, capture a copy-integrity baseline. A layout
change that changes visible text is a failure unless the user separately requested a
copy edit.

## Documentation

Full documentation: https://docs.astro.build

Consult these guides before working on related tasks:

- [Adding pages, dynamic routes, or middleware](https://docs.astro.build/en/guides/routing/)
- [Working with Astro components](https://docs.astro.build/en/basics/astro-components/)
- [Using React, Vue, Svelte, or other framework components](https://docs.astro.build/en/guides/framework-components/)
- [Adding or managing content](https://docs.astro.build/en/guides/content-collections/)
- [Adding styles or using Tailwind](https://docs.astro.build/en/guides/styling/)
- [Supporting multiple languages](https://docs.astro.build/en/guides/internationalization/)
