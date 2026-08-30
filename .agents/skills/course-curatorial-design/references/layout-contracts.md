# Course layout contracts

These are concrete layout instructions. They preserve the existing course copy.
Choose the contract by route and reader task; do not apply a visual treatment merely
because it is associated with a country, period, or design movement.

## Contract A — course route map

Use for `/`.

- Purpose: let a student find the current lesson, understand the semester’s four
  chapter groups, and jump to a week without reading the whole page.
- Desktop: a 12-column grid inside a 1440 px maximum frame with 48 px outer margin.
  The first view uses 8 columns for the existing title and description, 4 columns for
  the existing current-lesson information. The four chapter groups follow as one
  vertical route, not four equal cards.
- Mobile: one column. Keep course title, current-lesson action, then the route map.
  Do not hide dates or week numbers.
- Hierarchy: title first, current lesson second, week list third. Use the existing
  accent only for the current lesson and its action.
- Surface: base page surface first. Separate route groups with rules and changed
  spacing. A filled panel is permitted only around the current lesson.
- Exclusions: no altered copy; no marketing hero illustration; no badge cloud; no
  dashboard metrics; no repeated card shadows; no same-sized chapter tiles.

## Contract B — technical reader

Use for `/lessons/*` and `/book`.

- Purpose: let a beginner read one technical claim, inspect its evidence, run a
  command, then continue to the next claim.
- Desktop: reading column 8/12 wide, with an optional 3/12 marginal navigation area.
  The header aligns to the reading column. Each H2 begins a new evidence interval.
- Code and diagrams: code uses the full reading measure. A diagram sits directly
  after the claim it proves; its caption explains only the diagram’s observable claim.
- Mobile: single reading column, 16 px side gutters, no horizontal code clipping.
- Hierarchy: heading → claim → raw evidence → runnable command → consequence.
- Exclusions: no decorative cover title inside the lesson body; no parallel cards that
  repeat the same explanation; no diagram metadata such as issue numbers or slogans.

## Contract C — reference index

Use for `/glossary` and `/preparation`.

- Purpose: enable lookup, orientation, and return to study without turning reference
  material into a landing page.
- Desktop: term/section label occupies 4/12; definition or steps occupy 8/12. Use a
  continuous ruled list rather than a grid of independent cards.
- Mobile: label precedes content, with one rule between records.
- Hierarchy: term or section name, then the one definition or action the learner needs.
- Exclusions: no decorative numbering; no status chips; no hover-only essential data;
  no background surface behind every entry.
