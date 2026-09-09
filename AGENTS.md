# Course Constitution (ELI5) — 網頁程式設計 115

> Target Audience defined per `DreambigOu/ELI5 SKILL.md`. All teaching materials, slides, and interactive components calibrate against this baseline.

**Target Audience: College Student · Age 20 · Zero Backend Foundation**

- Basic familiarity with Python and terminal commands.
- Unclear on `GET` vs `POST`, unfamiliar with which layer returns `200 / 404 / 401`.
- Currently receiving direct answers from AI; pastes code that runs without understanding causality.

**Writing Calibration (De-AI, per `Nanako0129/sepia` & O'Reilly Editorial Standard):**

Write in an authentic human voice. Before drafting, read finalized copy in this repo for tone (`src/pages/index.astro`, `src/content/docs/readme.md`) — concise sentences, direct assertions, one conclusion per sentence without circular phrasing.

- Open with concrete situations (classroom context, first `curl`, specific error message) rather than abstract definitions.
- Provide firm technical judgments with clear rationale; reserve hedging only for genuine uncertainties.
- Avoid the "Introduction → Progress Recap → Summary" sandwich structure; conclude immediately once the technical content is delivered.
- Condition all numbers on specific constraints; never invent numbers or case studies without evidence (ask or leave a TODO).
- Prefer deletion and replacement over additive insertion.
- Technical terms, URLs, and version numbers must be authentic; never fabricate specifics for simulated realism.
- **Language Division**: Instructional narrative in Traditional Chinese; source code, variable naming, comments, and identifiers strictly in English (`語言分工：文稿敘述用中文；程式碼、變數命名、註解一律英文`).

**Tone**: Clear, direct, respectful. No condescension, no sarcasm. Tailor detail to the audience: a single diagram and a single `curl` command are sufficient.

---

## O'Reilly Editorial Working Principles (技術編輯工作守則)

Follow these editorial principles when authoring textbooks, handouts, and documentation:

1. **Mental Model First (心智模型優先)**
   - Clarify role and responsibility boundaries before introducing mechanics (Who asks, what verb, who answers, who is responsible).
   - Avoid dumping isolated terminology; establish cause-and-effect dialogues first, then introduce terms.

2. **Show the Wire, Strip the Magic (撥開黑盒，看見傳輸)**
   - Backend systems have no magic. Avoid distorted metaphors; inspect real raw HTTP text packets (Headers, Methods, Payload).
   - Help beginners see that frameworks, browsers, and CLIs all assemble and parse plain text underneath.

3. **Observable Proof over Abstract Theory (可驗證性大於純理論)**
   - Accompany every concept with an executable terminal command readers can run to observe output (`curl -v`, `httpie`, minimal Python script).
   - Show readers which response line returned the status code (`200`, `404`, `500`).

4. **Precision Terminology, Zero Fluff (精準術語，零多餘修飾)**
   - Use rigorous technical terms (Request Line, Header, Status Code, Idempotency, Payload).
   - Prohibit empty marketing adjectives ("very powerful", "extremely important"); explain facts and technical constraints directly.

5. **From Wire to Browser Vision (視角穿透)**
   - Connect the network layer to the browser experience:
   - Click button/URL → Browser issues Request → Backend computes → Returns Response → Browser renders Response Body.

---

## Development

Start the development server in background mode:

```bash
astro dev --background
```

Manage the background server with `astro dev stop`, `astro dev status`, and `astro dev logs`.

---

## Course Curation and Learning Visuals

Before changing the course site's visual language or producing lesson diagrams, consult `.agents/skills/course-curatorial-design/SKILL.md`.

Before a new layout direction is implemented, select three examples from `.agents/skills/course-curatorial-design/references/japanese-web-awards.md`, capture their rendered pages, and present a reference board for user approval. Never choose a direction from a regional-aesthetic adjective alone.

The website is a curated learning journey, not a dashboard. Start with the learner's question and the sequence of evidence; styling comes after that structure is settled. For ELI5 diagrams, state one observable claim first and draw only the objects, wire text, arrows, and short labels needed to prove it. Do not batch-generate or replace diagram assets until the user accepts one candidate direction.

---

## Content and Layout Boundary

Layout work must not edit course copy. Keep visible course text and course data in content/data modules; keep layout components responsible only for structure, responsive behavior, and semantic presentation; keep route pages responsible only for composition. Before a visual refactor, capture a copy-integrity baseline. A layout change that changes visible text is a failure unless the user separately requested a copy edit.

---

## Documentation

Full documentation: https://docs.astro.build

Consult these guides before working on related tasks:
- [Adding pages, dynamic routes, or middleware](https://docs.astro.build/en/guides/routing/)
- [Working with Astro components](https://docs.astro.build/en/basics/astro-components/)
- [Using React, Vue, Svelte, or other framework components](https://docs.astro.build/en/guides/framework-components/)
- [Adding or managing content](https://docs.astro.build/en/guides/content-collections/)
- [Adding styles or using Tailwind](https://docs.astro.build/en/guides/styling/)
- [Supporting multiple languages](https://docs.astro.build/en/guides/internationalization/)

---

## RTK Policy

Follow `~/.agents/RTK.md` and the current tool's global instructions for automatic versus manual RTK routing. Preserve exact output when required.
