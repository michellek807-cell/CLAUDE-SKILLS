---
version: alpha
name: Vox Documentary — Frame (video / frame layer)
description: >
  Frame-scale design system for "Three Accidents That Rewrote Medicine" — a Vox-style
  documentary explainer covering Aspirin, Vitamin C, and Penicillin. Warm paper-collage
  ground, matte-black ink, Vox-yellow as the sole populist accent, Playfair Display for
  every title/headline and Inter for dates, labels, and body chrome. Motion is snappy and
  editorial: GSAP power2.out slide-ins and clip-path mask reveals carry every entrance and
  scene seam — this system is authored for motion, unlike a static print spec.
unit: the frame — 1920×1080 primary (16:9)
principle: paper-collage texture is sacred · black + yellow is the only color language · motion is snappy, never soft

colors:
  bg-canvas: "#F4F1EA"
  ink: "#111111"
  accent-yellow: "#FFF000"
  text-secondary: "#4A4A47"
  line: "#111111"
  paper-shadow: "rgba(17,17,17,0.12)"

typography:
  # — reading ramp (Inter) — dates, labels, captions, body chrome
  body:        { fontFamily: "Inter", cqw: 1.1,  weight: 400, lineHeight: 1.5, color: "ink" }
  body-sm:     { fontFamily: "Inter", cqw: 0.9,  weight: 400, lineHeight: 1.5, color: "text-secondary" }
  date-label:  { fontFamily: "Inter", px: 20, weight: 600, tracking: "1px", upper: false, color: "ink" }
  label:       { fontFamily: "Inter", px: 14, weight: 600, tracking: "3px", upper: true, color: "ink" }
  micro:       { fontFamily: "Inter", px: 12, weight: 500, tracking: "2px", upper: true, color: "text-secondary" }
  # — display / hero ramp (Playfair Display, bold) — every title and headline
  h3:          { fontFamily: "Playfair Display", cqw: 2.0, weight: 700, lineHeight: 1.15 }
  h2:          { fontFamily: "Playfair Display", cqw: 3.2, weight: 700, lineHeight: 1.1 }
  h1:          { fontFamily: "Playfair Display", cqw: 5.5, weight: 800, lineHeight: 1.05 }
  display:     { fontFamily: "Playfair Display", cqw: 7.5, weight: 800, lineHeight: 1.0 }
  timeline-year: { fontFamily: "Playfair Display", cqw: 3.5, weight: 800, lineHeight: 1.0, color: "ink" }

spacing:
  pad-x: "6cqw"
  pad-y: "5cqw"
  gap-lg: "4cqw"
  gap-md: "2.5cqw"

components:
  paper-card:
    backgroundColor: "{colors.bg-canvas}"
    border: "none"
    rounded: "0"
    shadow: "0 8px 24px {colors.paper-shadow}"
    description: "Torn/cut-out collage piece — flat paper texture, soft drop shadow only, never a hard border."
  ink-rule:
    backgroundColor: "{colors.ink}"
    size: "100% × 3px"
    description: "The system's structural divider — a solid matte-black bar, never a thin hairline."
  yellow-highlight:
    backgroundColor: "{colors.accent-yellow}"
    description: "Populist accent — used as a text-highlight swipe, a tick-mark fill, or a small tag/stamp. Scarce: one per frame, never a full background."
  date-tick:
    backgroundColor: "{colors.ink}"
    typography: "{typography.timeline-year} on {colors.accent-yellow} tag"
    description: "Timeline year marker — black numeral on a small yellow tag, collage-stamped at a slight rotation."
  title-block:
    typography: "{typography.h1} or {typography.display} in ink"
    description: "Playfair Display bold headline, left-anchored, sentence case with one key word optionally boxed in yellow."
  label-chip:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.bg-canvas}"
    typography: "{typography.label}"
    rounded: "0"
    description: "Solid black chip with cream uppercase label text — used for act/scene tags."
  paper-grain:
    opacity: 0.04
    description: "Full-bleed SVG feTurbulence noise layer, shared across the whole composition (not per-scene, not a clip) — kills flat digital rendering on the cream ground. Implemented in index.html as a non-clip sibling of the .clip scenes, never a wrapper around them."
  cutout-photo:
    filter: "grayscale(30%) contrast(115%) brightness(95%) drop-shadow(8px 12px 16px rgba(0,0,0,0.25))"
    description: "Editorial treatment for real sourced photography standing in for a collage cutout — single filter declaration, soft directional shadow mimics cut-paper thickness. Never apply to invented vector art."
  historical-print:
    filter: "grayscale(100%) contrast(140%)"
    blendMode: "multiply"
    description: "Archival/period-photo treatment — desaturated, high-contrast, multiply-blended so it sits into the cream paper ground rather than floating as a flat rectangle."

motion:
  easing-primary: "power2.out"
  entrance: "GSAP slide-in — element travels 60-120px along one axis into its resting position, power2.out, 0.5-0.8s, no overshoot"
  reveal: "clip-path mask reveal — inset() or polygon() animated from a closed edge to full, power2.out, 0.6-1.0s; used for image/photo collage pieces and title-block entrances"
  scene-seam: "outgoing element exits on the same vector the next element enters on (vector continuity) — see /hyperframes-animation and /motion-doctrine before authoring scene transitions"
  restraint: "no idle ambient wobble; every motion beat performs (enters, reveals, or exits) rather than breathing"
---

# Vox Documentary — Frame (video / frame layer)

## Overview

This is a **paper-collage editorial system** built for a Vox-style history/explainer
documentary. The ground is a warm off-white paper texture, never pure white or pure
black. Every headline and title lives in **Playfair Display**, bold, set in ink —
serif carries authority and the "documentary" register. **Inter** carries everything
functional: dates, timeline labels, captions, body copy — always in a lighter,
utilitarian register that contrasts against the serif display type.

Color is deliberately restrained to two notes: **matte black** (`#111111`) as ink —
type, rules, chips, structural bars — and **Vox yellow** (`#FFF000`) as the *only*
populist accent, used sparingly as a highlight swipe, a date-tag fill, or a small
stamp/tag. Yellow never becomes a background or a large fill; its power comes from
scarcity.

Motion is **snappy and editorial**, not soft or ambient: entrances are GSAP
`power2.out` slides, and photo/collage pieces or title blocks reveal through animated
`clip-path` masks rather than simple fades. This system is explicitly authored for
motion — unlike a print-only spec, `motion:` tokens above are normative, not
decorative.

**Key characteristics at frame scale:**

- **Cream paper ground** (`#F4F1EA`) with a subtle collage/paper texture — never flat pure white.
- **Playfair Display bold** for every title/headline; **Inter** for dates, labels, captions, body.
- **Matte black + Vox yellow only** — no third color. Yellow is scarce (one accent per frame).
- **Paper-collage components** — torn-edge cards, cut-out shapes, soft drop shadows, slight rotation on stamped elements (dates, tags).
- **Snappy motion** — `power2.out` slide-ins, `clip-path` mask reveals; no idle ambient wobble.

## The Frame

- **Primary:** 1920×1080 (16:9). Display authored in **`cqw`** (`px ÷ 1920 × 100 = cqw`).
- **Safe area:** `pad-x` (6cqw) generous gutters; collage pieces (torn paper, photos) may bleed off an edge for texture.
- **The container law (load-bearing).** Every frame ground sets `container-type: size`; all frame-relative units are `cqw`/`cqh` against it — never `vw`.

## Colors

`{colors.bg-canvas}` is the ground on every frame — always cream, never pure white or
black. `{colors.ink}` is the one text/rule color: headlines, body, structural bars,
chips. `{colors.accent-yellow}` is the single populist accent — a highlight swipe
behind 2-4 words, a date-tag fill, a small stamp. `{colors.text-secondary}` is a muted
warm-gray used only for secondary captions/micro text, never for a headline.
`{colors.paper-shadow}` is the soft shadow under collage pieces — never a hard border.

**No third color exists.** When emphasis is needed beyond ink, reach for yellow —
never introduce a new hue.

## Typography

Two ramps. The **display ramp** (Playfair Display, weight 700-800) carries every
title, headline, and timeline year — always ink, sentence case, never uppercase. The
**reading ramp** (Inter, weight 400-600) carries dates, labels, captions, and body —
labels are uppercase and tracked; body and date-labels are not.

- **Legibility floor:** any load-bearing line ≥ 1.4cqw.
- **Fit-to-measure:** ≤3 words → `display`/`h1`; 4-6 → `h2`; 7+ → `h3`.
- **Playfair is always bold (700-800), ink, sentence case** — never thin, never uppercase.
- **Inter labels are uppercase, tracked 2-3px**; Inter body and date-labels are sentence case, untracked.

## Depth & Surface

- **Paper-collage layering** — cut-out shapes (bark, pods, portraits, icons) stack with soft drop shadows (`{colors.paper-shadow}`), suggesting physically layered paper rather than flat vector art.
- **Slight rotation** on stamped elements (date tags, labels) — 3-15°, never perfectly axis-aligned — reinforces the "collage" feel.
- **Ink rules** (`ink-rule`, 3px solid black bars) are the only hard structural line; there are no thin gray hairlines in this system.
- **Ceiling:** no gradients, no neon/glow, no glassmorphism. Shadows stay soft and single-source (never a hard drop-shadow duplicate).

## Shapes

- **Torn/cut paper edges** or clean rectangles — never fully rounded pill shapes.
- **0 border-radius** on structural chips/bars; collage cutouts may use irregular/organic SVG paths (bark, mold bloom, molecule glyphs) rather than geometric primitives.

## Components

- **paper-card** — cream collage cutout, soft shadow, no border.
- **ink-rule** — the one structural divider, solid 3px matte black.
- **yellow-highlight** — scarce populist accent: text-highlight swipe, tick fill, or small tag.
- **date-tick** — timeline year marker, black Playfair numeral on a rotated yellow tag.
- **title-block** — Playfair bold headline, left-anchored, one word optionally boxed in yellow.
- **label-chip** — solid black chip, cream uppercase Inter label, used for act/scene tags ("ACT 1", "1897").
- **paper-grain** — full-bleed noise texture, shared across the whole video, not per-scene.
- **cutout-photo** / **historical-print** — the two real-photography treatments; collage/vector art never uses these.

## Composition Rules

### Do

- Ground every frame in `{colors.bg-canvas}` — cream, textured, never flat white.
- Set every title/headline in **Playfair Display bold**, ink, sentence case.
- Set every date, label, and caption in **Inter** — labels uppercase/tracked, body/dates not.
- Use **Vox yellow once per frame**, at most — a highlight, a tag, a tick — never a large fill.
- Animate entrances with `power2.out` slides and reveal collage/title pieces with `clip-path` masks.
- Give stamped elements (date tags, labels) a slight rotation for the collage feel.

### Don't

- Don't introduce a third color — black and yellow only.
- Don't render a headline in Inter, or a label/date in Playfair.
- Don't let yellow become a background fill or dominate a frame.
- Don't use soft ambient fades/breathing for entrances — motion is snappy (`power2.out`) or reveals via `clip-path`, not opacity-only.
- Don't add drop shadows harder than `{colors.paper-shadow}`, gradients, or glow effects.

## Numerals & Claims (hard rule)

Never invent figures, dates, or counts at frame scale. Every year on a `date-tick`
(1897, 1899, 1928, 1932, 1933, 1944, …) must trace to the sourced script. Render an
unconfirmed figure as a placeholder (`— figure —`) until the script supplies it.

## Pre-Render Self-Audit

- **Palette** — cream ground, black ink, yellow accent only; no third color anywhere.
- **Type** — Playfair bold for every title; Inter for every date/label/body; no swapped roles.
- **Yellow scarcity** — at most one yellow accent per frame.
- **Motion** — every entrance is a `power2.out` slide or a `clip-path` reveal; no idle wobble.
- **Collage feel** — soft single-source shadows, slight rotation on stamps; no hard borders, no gradients.
- **Fabrication** — every date/year traces to the sourced script, else placeholder.

## Known Gaps

- **Fonts:** Playfair Display + Inter, resolved by the HyperFrames compiler from the `font-family` declarations in `index.html` (no Google Fonts `<link>`/`@import` — that trips lint and risks a render-time navigation timeout).
- **Paper texture:** implemented — a shared, non-clip `paper-grain` SVG noise layer at 0.04 opacity, full-bleed across the whole composition (see `index.html`). Do not duplicate it per-scene.
- **9:16 / 1:1 not yet documented** — this project is locked to 16:9 (YouTube long-form) per `BRIEF.md`; add aspect-ratio guidance here only if the destination changes.
