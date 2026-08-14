---
workflow: general-video
flow: automation
storyboard: yes
message: "Three ordinary accidents — a family remedy, a kitchen spice, an uncovered petri dish — became the medicines billions of people use today."
destination: youtube
aspect: 1920x1080
audience: general YouTube documentary audience (Vox-style explainer viewers)
length: ~10:47 (VO-driven — see Notes)
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

- No external/generated visual media. All illustration is hand-authored inline SVG (paper-collage
  style, ink-only on cream, no stock photography, no real footage, no AI-generated
  images) — this is the final illustration approach for the project, not a placeholder.
  AI generation (HeyGen via `/media-use`, then Higgsfield via `/higgsfield-generate`) was
  attempted first but both require an interactive browser OAuth login this sandbox can't
  complete, and the user is separately low on Higgsfield credits — hand-authored SVG sidesteps
  both constraints entirely (no auth, no credits, deterministic, versioned as code).
- `audio/s1.wav` … `audio/s9.wav` — the full narration voiceover, one file per scene,
  generated locally via Kokoro-82M (`npx hyperframes tts`, voice `am_michael`) — no
  auth or credits needed, same rationale as the illustration. Scripts live in
  `audio/scripts/s1.txt`…`s9.txt`. Total ~30MB of WAV; not yet compressed to a smaller
  format (MP3/AAC would shrink this materially if repo size becomes a concern — ffmpeg
  is available in this environment to do that conversion).

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
- **Status: all 9 scenes built, voiceover recorded and synced** (this commit).
  Act 1 (0:00-2:51): willow bark, paprika/adrenal glands, mold spore. Act 2
  (2:51-6:40): Hoffmann 1897, Szent-Györgyi 1928-1932, Fleming 1928. Act 3
  (6:40-10:47): Bayer chemical process, Reichstein-Grüssner process, Peoria
  deep-tank fermentation. `#root data-duration="647"` (~10:47 — real VO length,
  superseding the earlier ~12min round-number estimate), 8 push-slide transitions,
  built on the GSAP scene-template pattern from `/hyperframes-animation` →
  `transitions/catalog.md` (plain `.scene` divs, not `class="clip"`).
- **Voiceover:** each scene has an `<audio id="sN-audio" src="audio/sN.wav" class="clip"
  data-start=… data-duration=… data-track-index="10">`, non-overlapping so they share
  one track. `data-start` = scene boundary + 0.3s lead-in; `data-duration` = the
  measured Kokoro output length (not rounded/guessed). Scene windows =
  lead-in + VO length + ~1.6s trailing hold, rounded up — this is what actually
  determined the new boundaries above, not the other way around.
- **Motion re-synced to narration** (superseding the earlier front-loaded version):
  each scene's secondary reveal beats now fire at the point in the VO where that
  fact is actually spoken, estimated by word-position proportion within the script
  (not a forced-alignment transcript — a future pass could tighten this with
  `npx hyperframes transcribe` on the WAVs for exact word timestamps). Examples:
  scene 2's paprika illustration AND its body-copy both land at ~79% into the VO,
  exactly when "paprika" is spoken; scene 4's date-tick stamps in at ~55% in, on
  "August 10th, 1897"; scenes 7 and 8's reaction-flow nodes reveal one at a time as
  the VO narrates each synthesis step, instead of arriving as one stagger burst.
  Camera-drift durations were extended to span each scene's now-longer real length.
- Yellow accent discipline: exactly one yellow element per frame throughout —
  Act 1 uses a `.yellow-highlight` word in body copy, Act 2 uses the `.date-tick`
  component (which is itself yellow, so titles stay plain there), Act 3 uses the
  final/product node in each reaction-flow diagram (S9 uses its `.date-tick`
  instead, so its tank illustration stays ink-only).
- Illustration is finished hand-authored ink-only SVG line art (paths in `--ink` on
  `--bg-canvas`, no third color) throughout — willow bark, adrenal gland, paprika
  pods (with stem caps + ridge hatching), petri dish/mold (with bacteria/spore
  stipple fields), chemistry flask (with bubbles + cork), four distinct guinea-pig
  silhouettes, fermentation tank (with rivets, weld seams, a pressure gauge, and
  support legs), plus the two coded reaction-flow diagrams. This is the final art
  direction — not pending replacement with generated/photographic assets.
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
