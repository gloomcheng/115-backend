# Contract — NGK course exhibit

Status: approved on 2026-08-30. Structural reference:
https://www.ngk.co.jp/gaishi-h/

This contract transfers an information-exhibition system. It does not copy NGK's
characters, historical objects, text, trademarks, illustrations, or page assets.

## Reader task

The first viewport must tell a student what the course teaches, show the current
Request/Response idea, and expose the Week 01 action. The next view explains the
current lesson, then presents the four course chapters and the complete 18-week route.

Course copy is fixed during layout work. All visible text comes from `src/data` or
`src/content`; `npm run copy:check` must pass before visual review.

## Composition

- Desktop shell: 1440 px maximum width, 48 px outer gutters, 12-column grid.
- Desktop first viewport: 72 px navigation plus one yellow exhibit field whose bottom
  lands at the viewport bottom at 1432 × 661. Use a 6/6 split for copy and the main
  illustration. The title remains two intentional lines and must not clip.
- Mobile first scene: one column inside the same yellow field. Copy and actions precede
  the illustration. Nothing may overlap text; the page must not overflow at 390 px.
- After the hero, use one focused current-lesson explanation, then an equal-height
  chapter exhibit grid. Each chapter card contains number, original illustration,
  title, summary, and week range.
- The 18-week schedule is a horizontal museum timeline made from circular stops,
  date ribbons, and directional chevrons. Mobile keeps horizontal scrolling instead
  of shrinking labels below readable size.
- Section rhythm comes from large color fields, scale changes, and the continuous
  ruled exhibition ground. Do not split every section with divider lines.

## Type and color

- Use sans-serif Chinese typography only. Display: Noto Sans TC, weight 900, tight
  tracking. Reading: Noto Sans TC, weight 400–600. Evidence: JetBrains Mono.
- Primary ink: `#075486`. Hero yellow: `#f4c84f`. Paper: `#fffaf0`. Supporting blue:
  `#b8d8e8`. Signal coral: `#ef795e`.
- Body text is at least 16 px. Metadata may be 12–14 px only when it is secondary and
  high-contrast. Never shrink explanations to make a composition fit.

## Illustration role

- Illustrations are information exhibits, not background decoration. Use medium-blue
  outlined physical objects, restrained flat fills, and large technical labels.
- A diagram contains only the actors and evidence needed for its claim. Decorative
  titles, unit numbers, slogans, captions, and repeated characters are excluded.
- Review generated images in Preview before adding them to the project. A rejected
  image is discarded; it is not patched into a new direction.

## Implementation

- Use Tailwind CSS utilities for all layout and component styling. Arbitrary values,
  CSS-variable utilities, and arbitrary descendant selectors are allowed.
- Do not add custom classes or selectors to `src/styles/global.css`. That file contains
  only Tailwind imports/plugins and theme variables.
- Components own reusable structure. Data/content files own words. Route files compose
  them without hard-coded course copy.

## Exclusions

- No Ming/Song serif type.
- No dark editorial poster, monochrome dashboard, bento dashboard, repeated generic
  cards, stacked drop shadows, glass effects, or sparse whitespace-led hero.
- No divider-heavy page that breaks one learning journey into unrelated strips.
- No reused rejected palette, grid, illustration, or person-centered chapter set.
- No imitation of NGK's logo, characters, historical narrative, or proprietary art.

## Acceptance checks

- Desktop 1432 × 661: header and complete hero fit; no horizontal overflow.
- Mobile 390 × 844: no overlap or horizontal page overflow; navigation and hero remain
  usable; timeline may scroll inside its own region.
- Lesson illustrations are 852 px wide inside a 980 px reading field on desktop, with
  readable source/status text and clear space above and below.
- `npm run copy:check` passes for all five routes.
- `npm run check` passes all editorial, image, type, build, accessibility, and font
  guards.
