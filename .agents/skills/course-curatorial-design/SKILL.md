---
name: course-curatorial-design
description: Redesign or extend the 115-backend course as a curated learning journey, including its site layout and ELI5 technical diagrams. Use for visual-system, information-architecture, or lesson-illustration work; do not use for ordinary copy-only edits.
---

# Course curatorial design

## Scope

This is a workflow and governance skill. It does **not** select a culture, visual
aesthetic, font, palette, or layout by itself. A request to change design must choose
or create one concrete layout contract first.

When the request is to change design or layout, preserve all existing course copy,
labels, titles, and calls to action. Copy changes require separate user instruction.

## Content/layout separation

- Put user-visible copy and course data in content or data modules. Do not bury it in
  layout classes or modify it while changing CSS/markup.
- Layout components own semantic structure, grid, spacing, responsive behavior, and
  component placement. They consume copy as data.
- Route pages compose content and layout. They do not duplicate either.
- Before a layout refactor, record the rendered text baseline. Verify the same text
  afterward; any difference is a copy change that requires separate approval.

The course is a sequence of things a beginner can observe and verify:

`learner question → observable evidence → one verified conclusion`

## Before implementation

1. Inspect the existing page and identify the learning task it must support.
2. Read [the layout contract template](references/layout-contract-template.md).
   Read [the available route contracts](references/layout-contracts.md) when the
   requested route matches one of them.
   Read [the Japanese web award reference library](references/japanese-web-awards.md)
   before proposing a new direction.
3. Select three concrete references from the library, capture their current rendered
   pages, and present a reference board for approval. Never infer a layout from a
   phrase such as “Japanese”, “wabi-sabi”, “premium”, or “editorial”.
4. Record the contract’s target route, fixed copy, viewport rules, visual hierarchy,
   component rules, and exclusions before editing.

## Rejection discipline

Treat a rejection of the governing relationship as evidence that the direction is
wrong, not as a request for a more polished variant.

- When the user rejects the layout’s premise, discard the candidate and restore the
  last accepted baseline before exploring a new contract.
- Do not retain a rejected grid, component hierarchy, font treatment, color role, or
  visual motif merely because implementation work has already been spent on it.
- Record the rejected premise and its reason in the next contract’s exclusions. Do not
  convert a rejected direction into a reusable token, skill rule, or harness check.
- Return to discovery: inspect source material, write the reader task, present distinct
  contract options, and wait for a selected direction before implementation.

## Layout contracts

A valid contract describes a specific, testable design operation: grid, type roles,
space, surface, image role, navigation position, mobile transformation, and prohibited
patterns. It does not say only “use Japanese aesthetics” or “make it minimalist”.

When a contract is accepted, put it in `references/` and link it from this skill. Do
not turn a rejected direction into a reusable instruction.

The currently approved course direction is
[NGK course exhibit](references/contracts/ngk-course-exhibit.md). The earlier
[Kamipa information landscape](references/contracts/kamipa-course-layout.md) remains
research history, not an implementation baseline.

## Implementation boundary

- Build layout styling with Tailwind CSS utilities, including arbitrary utilities and
  arbitrary descendant selectors when needed. Do not add project-specific CSS classes
  or selectors to `global.css`.
- `global.css` is limited to Tailwind imports, plugins, and theme variables. Reusable
  structure belongs in Astro components; page-specific composition stays in route or
  layout markup.
- Do not add visible words, arrows, badges, or numbering inside layout templates.
  Read visible copy from `src/data` or `src/content`; use SVG/CSS for purely visual
  marks so copy-integrity stays meaningful.
- Do not use Unicode emoji in course copy, diagrams, or UI. Semantic interface icons
  must come from the installed Lucide icon set so stroke, sizing, and accessibility
  remain consistent. Technical diagrams and operating-system window controls may use
  purpose-built SVG geometry when they are part of the evidence rather than an icon.

## ELI5 technical diagrams

Before any ImageGen call, read the canonical
[course diagram style template](../../../docs/diagram-style-prompt.md). Keep its locked
style block unchanged and append only the per-claim subject brief. Do not recreate the
art direction from memory or persist a separate full style prompt for every diagram.

1. Write the single claim first. Example: `The 404 is on the first line of the
   Server response.`
2. Draw the smallest real evidence that proves it. Prefer native SVG or interactive
   HTML so wire text, arrows, and accessibility text remain deterministic.
3. Use recognizable outlined Client and Server objects only to locate responsibility.
   The dominant visual area belongs to the real HTTP text and its causal movement.
4. Keep explanatory labels that point to visible evidence, such as `Status Line` or
   `Body`. Remove only metadata, decorative titles, unit numbers, slogans, and footer
   copy that the diagram does not need.
5. Add a terminal command near the diagram in the lesson so the learner can verify
   its claim. Do not use a visual metaphor that contradicts the protocol.

## ELI5 diagrams

- Before drawing, write the one-sentence claim and remove every subject that is not
  required to prove it. A Request/Response diagram does not need a student, browser,
  or server rack; a Client/Server responsibility diagram does need recognizable
  outlined Client and Server objects.
- Use the approved exhibit illustration grammar: medium-blue hand-inked contours,
  warm off-white ground, pale yellow and powder-blue fields, coral only for contrast
  or return/error paths, concrete physical objects, and large readable technical text.
- Prefer circular exhibit medallions and horizontal causal movement when a sequence is
  being taught. Do not force every topic into the same number of circles or repeat one
  character/object across the set.
- Produce one candidate diagram for one claim. Open the PNG directly in macOS Preview.
- Do not extend a candidate into a set, overwrite existing lesson assets, or update
  this skill from a rejected candidate. Wait for an explicit user acceptance.
- After one image direction is accepted, keep its line weight, palette, object detail,
  text scale, and background treatment consistent across the remaining set. Keep each
  diagram's subject and composition specific to its own claim.
- After a whole-site change, inspect the running page at desktop and narrow widths,
  then run `node scripts/curatorial-harness.mjs`, Astro check, and a static build.

## Verification

Run `scripts/curatorial-harness.mjs` whenever changing site structure. The harness
may verify presence of a selected contract and shared layout primitives, but must never
freeze or rewrite course copy. Inspect the running site at desktop and mobile widths;
the harness is not a visual verdict.
