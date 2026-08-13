---
workflow: general-video
flow: automation
storyboard: yes
message: "Three ordinary accidents — a family remedy, a kitchen spice, an uncovered petri dish — became the medicines billions of people use today."
destination: youtube
aspect: 1920x1080
audience: general YouTube documentary audience (Vox-style explainer viewers)
length: ~12min
angle: narrative — three parallel case studies (Aspirin, Vitamin C, Penicillin), interleaved by act rather than told back-to-back
---

## Intent

A Vox-style documentary explainer, "Three Accidents That Rewrote Medicine," tracing
Aspirin, Vitamin C, and Penicillin from their raw natural origin through their
discovery moment to their industrial-scale manufacturing. Authoritative, fast-paced,
clear — the Vox house voice. Structure cuts between all three stories within each of
three acts (Raw Natural Origin → Breakthrough Moment → Industrial Synthesis) rather
than telling one story fully before the next, so the parallel dates and mechanisms
stay comparable across medicines.

## Assets

- None supplied yet. All visuals are invented paper-collage illustration (no stock
  photography, no real footage) per the faceless-explainer-style approach carried
  into this general-video build.

## Customizations

- Full 9-scene narration + visual-asset-layout + motion blueprint already drafted in
  chat ("Vox Explainer Blueprint: Three Accidents That Rewrote Medicine") — reuse
  that scene breakdown and timestamps when authoring `STORYBOARD.md`, don't
  re-derive it.
- Design system is locked via `frame.md` (written this session): cream paper ground
  `#F4F1EA`, matte black `#111111` + Vox yellow `#FFF000` as the only two accent
  colors, Playfair Display bold for all titles/headlines, Inter for dates/labels/body,
  GSAP `power2.out` slide-ins and `clip-path` mask reveals as the house transition
  language.

## Notes

- Sourced facts only — every date/year (1897, 1899, 1928, 1932, 1933, 1944, …) traces
  back to the research already gathered in chat; do not invent or round a date.
- This project intentionally exceeds the ~3min cap of the specialized narrative
  routes (faceless-explainer), which is why it's routed to `general-video` instead.
- **Status: all 9 scenes built** (this commit), matching the drafted blueprint's
  act structure and pacing exactly — Act 1 (0:00-3:00, 60s/scene): willow bark,
  paprika/adrenal glands, mold spore. Act 2 (3:00-7:30, 90s/scene): Hoffmann 1897,
  Szent-Györgyi 1928-1932, Fleming 1928. Act 3 (7:30-12:00, 90s/scene): Bayer
  chemical process, Reichstein-Grüssner process, Peoria deep-tank fermentation.
  `#root data-duration="720"` (12min), 8 push-slide transitions connecting all
  scenes, built on the GSAP scene-template pattern from `/hyperframes-animation` →
  `transitions/catalog.md` (plain `.scene` divs, not `class="clip"`).
- Yellow accent discipline: exactly one yellow element per frame throughout —
  Act 1 uses a `.yellow-highlight` word in body copy, Act 2 uses the `.date-tick`
  component (which is itself yellow, so titles stay plain there), Act 3 uses the
  final/product node in each reaction-flow diagram (S9 uses its `.date-tick`
  instead, so its tank illustration stays ink-only).
- Illustration is placeholder ink-only line art (SVG paths in `--ink` on
  `--bg-canvas`, no third color) throughout — willow bark, paprika, adrenal gland,
  petri dish/mold, flask, guinea-pig row, two reaction-flow diagrams, fermentation
  tank. Real illustration assets are not yet sourced (`/media-use`, when picked up).
- Motion currently front-loads each scene's beats in its first ~4-5s and holds
  static for the remainder. `/hyperframes-core` → `frame-worker-core.md` recommends
  sequencing reveals across the full shot in sync with voiceover instead — worth
  a pass once narration exists to drive that timing; not attempted here since
  there's no VO track yet.
- `npm run check`: lint is clean (0 errors — one info-level Studio-selectability
  note on the decorative overlay, expected/intentional). Motion: 0 errors.
  Contrast: 20/20 checks pass WCAG AA. One outstanding **warning**:
  `composition_file_too_large` (index.html is ~600 lines) — the tool recommends
  splitting scenes into sub-compositions under `compositions/` via
  `data-composition-src`. Deliberately not done in this pass: sub-compositions
  can't be reached by the main timeline's selectors, so each scene's internal
  choreography (entrance beats, camera drift) would need its own local timeline,
  a real architectural change rather than a quick split — flagged as a
  recommended follow-up, not attempted opportunistically alongside the 9-scene
  build.
- Runtime/layout checks fail in this sandbox only, because outbound access to
  `cdn.jsdelivr.net` (GSAP's CDN) is blocked by this environment's network
  policy (confirmed via repeated direct `curl` checks) — not a defect in the
  composition; re-check wherever that CDN is reachable.
