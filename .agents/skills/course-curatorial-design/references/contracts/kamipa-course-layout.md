# Contract — Kamipa information landscape

Status: approved reference direction. Source: https://www.kamipa.co.jp/

## Transferable structure

- A calm corporate shell that makes navigation available before the main story.
- One large primary field, followed by content domains whose density changes with the
  information task; not a repeated card grid.
- Full-width media or evidence fields establish topic context; smaller factual regions
  follow afterward.
- Section transitions come from background changes, scale changes, and content rhythm;
  not from frequent divider lines.
- Long information lists remain readable because headings, summaries, and links have
  distinct roles rather than identical component shells.

## Course translation

- The primary field is raw HTTP evidence, not a decorative video or photo.
- The first visible interaction is the existing Week 01 lesson action; it must remain
  explicit and readable.
- Course chapters become four distinct information landscapes: protocol, persistence,
  security, runtime. Each can change density or background, but keeps the same
  navigation and type roles.
- The complete schedule is a factual index near the end, not a duplicate hero grid.
- Client, Server, and Browser may appear only as outlined explanatory objects attached
  to a real Request/Response stage.

## Visual constraints

- Use a restrained neutral field, one dark ink, one muted supporting color, and a
  single localized signal color. Do not copy Kamipa's logo, video treatment, brand
  blue, paper imagery, or corporate typography.
- Avoid drop shadows, card stacks, poster-like metadata, fake texture, oversized
  generic headlines, and divider-based sectioning.
- Keep mobile as a progressive single column: topic field → action → evidence → index.

## Acceptance criteria

- Desktop: first viewport has navigation, one raw HTTP evidence field, and the
  existing Week 01 action without a card shell.
- Mobile: text does not sit under graphic objects; labels and actions remain at least
  14 px; no horizontal clipping.
- Existing rendered copy passes `npm run copy:check`.
