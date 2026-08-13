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
- Scaffold-only pass (this commit): `frame.md` design system + font/token wiring in
  `index.html`. Scene authoring (all 9 scenes) is deferred to the next session per
  explicit request — don't build them out yet.
