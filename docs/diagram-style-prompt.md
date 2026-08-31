# Course diagram ImageGen style template

This is the reusable prompt base for every generated lesson illustration. Do not write a new art direction for each diagram. Keep the style block unchanged and append one short subject brief.

## Provenance

The template was recovered from the Codex session that produced the approved Unit 01 illustration direction (`01a05005-3ec4-78c3-80c4-fe637aaa496f`). It is also checked against the current repository assets and the active course-curatorial-design rules.

Approved reference assets:

- `public/images/lessons/01/request-response.png`
- `public/images/lessons/01/client-server.png`
- `public/images/lessons/01/http-methods.png`
- `public/images/lessons/01/status-codes.png`
- `public/images/lessons/01/browser-vision.png`

Use two or three subject-relevant references. They are visual-language references, not edit targets.

## Locked style block

Copy this block verbatim into every ImageGen request:

```text
Use case: scientific-educational.
Asset type: ELI5 lesson illustration for the 115 Backend course, landscape 16:9.
Input images: use the supplied approved course illustrations only as visual-language references. Preserve their Japanese museum-education drawing grammar: coherent medium-blue hand-inked contour, warm off-white paper, pale yellow / powder blue / soft coral flat fills, circular exhibition medallions where the causal structure benefits from them, slight organic print irregularity, concrete observational objects, large readable technical labels, calm negative space. Create new original artwork. Do not copy their subject, wording, branding, or exact composition.
Style/medium: hand-drawn educational editorial illustration, flat screen-print color, subtly imperfect but coherent line weight, specific physical object construction, technically clear, not generic tech iconography.
Palette: warm off-white paper background; indigo or medium-blue outlines; pale custard yellow and powder blue fields; coral only for a return path, error, denial, or contrast that the claim requires; no black-dominant field.
Composition: one observable claim, one dominant causal reading path, all objects fully visible with safe margins. Use only the number of objects or medallions required by the claim. Prefer horizontal causal movement for a sequence. Do not force every diagram into the same number of circles or repeat the same character and objects across the set.
Text: include only exact technical wire text and short evidence labels that point to something visible. Make all text large enough to read at mobile lesson width. No title, unit number, footer, slogan, decorative caption, metadata, or small explanatory paragraph. Do not remove labels such as Request Line, Status Line, port, method, or state when the claim requires them.
Constraints: Client and Server must be recognizable outlined physical objects when responsibility is part of the claim. The real wire text, state change, or causal movement must occupy the dominant visual area. Arrow source, destination, and direction must be unambiguous. Preserve protocol accuracy. No third-party publisher or product branding, logos, watermarks, or imitation of a living artist or a specific artwork.
Avoid: generic UI cards, dashboard layout, emoji, mascot, people used only as decoration, repeated student character, cloud clip art, dark background, gradients, glow, drop shadows, 3D render, isometric architecture, photorealism, tiny text, extra arrows, decorative symbols, copied composition.
```

## Subject brief schema

Append only this brief after the locked style block:

```text
Observable claim: [one sentence that the image must prove]
Required objects: [only the physical objects needed to locate responsibility]
Required causal flow: [source -> exact wire text or state -> destination]
Exact text (verbatim): [complete allowlist of text that may appear]
Object-specific constraints: [what must be visibly inside, outside, blocked, changed, or unchanged]
Subject-specific avoid list: [nearby concepts that must not leak into this diagram]
```

If the subject brief needs a paragraph to explain the diagram, the claim is not atomic enough. Split the lesson claim before generating.

## Candidate workflow

1. Write the observable claim before the prompt.
2. Select two or three approved references that best match the needed object density and flow.
3. Combine the locked style block with one subject brief.
4. Generate one candidate for one claim.
5. Check exact text, arrow direction, protocol accuracy, mobile readability, trademark absence, and visual consistency.
6. Present the candidate for explicit approval. Do not generate the remaining set, update the lesson asset, or revise the skill from an unapproved candidate.

## Acceptance checks

- A learner can state the intended claim after looking at the image without reading the surrounding paragraph.
- Every word and arrow points to visible evidence; there is no decorative copy.
- The image uses the approved palette, contour, print irregularity, object detail, and negative-space density.
- Required technical text is exact and readable.
- No path, object, metaphor, or label contradicts the real protocol.
- No publisher name, brand logo, watermark, title, unit number, or footer appears.
