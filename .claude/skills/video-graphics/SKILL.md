---
name: video-graphics
description: Pipeline step 3 - plan and build graphics through HyperFrames. Use when the user asks for titles, lower thirds, callouts, kickers, on-screen text, or "add graphics" to a job. Plans beat by beat first, then builds the composition as short re-renderable parts from one shared timeline, with short-form safe zones enforced.
---

# Step 3 - Graphics

Graphics and captions render through **HyperFrames**, an npm package pinned to a
specific version. Never `npx hyperframes` without a version; never clone it; never
hand-edit anything under `.claude/skills/`. See `video-graphics-pin`.

## Plan first, build second

```bash
workflows/scripts/hf_build.sh <job>              # plan (if absent) + build parts
workflows/scripts/hf_build.sh <job> --replan     # regenerate the plan, losing edits
workflows/scripts/hf_build.sh <job> --preset long-form-clean
```

The plan is `hf-graphics/PLAN.md` - a beat sheet you can argue with in thirty
seconds - backed by `hf-graphics/timeline.json`, which holds every beat in
absolute cut-relative time. Read the plan, edit `timeline.json` (flip `enabled`,
rewrite `text`, change `kind`, delete beats), then build. Your edits survive a
rebuild unless you pass `--replan`.

Getting that order wrong is how you end up re-rendering a whole video to move
one word.

Beats are proposed from the canonical transcript - never re-transcribed. Kinds:
`title`, `kicker`, `callout`, `lower-third`, `endcard`.

## Parts, not one long render

**LOCK: long graphics render as short seamless parts from one shared timeline.**

`timeline.json` is the single source of truth. The builder slices it at *seams* -
gaps where no beat is in flight - into `hf-graphics/parts/part-NN/`, each a
self-contained HyperFrames project with its own root, its own `shared/` assets
and root-relative paths.

```bash
workflows/scripts/hf_render.sh <job>            # every part
workflows/scripts/hf_render.sh <job> part-03    # just the one that changed
workflows/scripts/hf_render.sh <job> --check    # lint only, render nothing
workflows/scripts/hf_concat_parts.sh <job>      # join them, stream copy
workflows/scripts/overlay_graphics.sh <job>     # composite onto the cut
```

Re-rendering part 3 after a note costs one part. The joins stay frame-exact
because nothing was re-timed, only re-sliced, and joining is a stream copy - no
re-encode, no quality drift between parts.

Parts render to MOV with an alpha channel so they composite over the footage
rather than replacing it. `overlay_graphics.sh` reframes the cut to the delivery
canvas and overlays; the audio is **stream-copied**, never re-encoded.

## Safe zones - not advisory

**LOCK: on 1080x1920 nothing that matters goes in the top 200 px or the bottom
300 px.** Face, captions and graphics all stay inside y 200-1620. That band is
where the platform's handle, follow button, caption stack and progress bar sit.

Enforced three ways: the preset lays every element out inside a `.safe` box; the
builder asserts each returned box against the band and *fails the build* for
short-form; and `hf_render.sh` hands HyperFrames the same keep-out band as a
`--caption-zone` error so the renderer checks it independently.

If a beat violates the band, fix the preset or the beat. Do not relax the band.

## Presets

`presets/<name>/build.py` plus `presets/<name>/spec.md`. The build module owns
everything visual - tokens, CSS, per-kind markup and animation - and the builder
only slices time.

- `short-form-punch` - 9:16, 1080x1920, big display type, one accent highlight
- `long-form-clean` - 16:9, 1920x1080, quieter; lower thirds and pills

To change the look, change the preset and rebuild. Never edit the generated HTML
under `parts/` - it is overwritten on every build and says so at the top.

## Composition contract

The builder emits it; you should recognise it when reading a part:

- root `<div>` with `data-composition-id`, `data-start="0"`, `data-width`,
  `data-height`, `data-duration`
- one `gsap.timeline({paused: true})` registered at `window.__timelines["<id>"]`,
  built synchronously
- each beat is a `<section class="clip">` with `data-start`, `data-duration`,
  `data-track-index` and a stable `id`
- GSAP is loaded from `shared/gsap.min.js`, **vendored**, not from a CDN

That last one matters: a composition that fetches GSAP over the network renders
silently wrong the day the network says no. The capture still succeeds, every
tween is simply missing, and the only trace is a `sub_timeline_script_failure`
warning buried in the log. Refresh the vendored copy with
`workflows/scripts/vendor_gsap.sh`.

Initial states go in `gsap.fromTo(...)`, never a CSS `transform` on the same
property - lint rejects that pairing.

## Checking

`hf_render.sh <job> --check` runs HyperFrames' lint, runtime, layout, motion and
contrast passes on each part. Aim for zero findings before rendering; a render is
minutes, a check is seconds.
