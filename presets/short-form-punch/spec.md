# short-form-punch

The locked look for 9:16 short-form. Loud display type, one accent per beat,
everything inside the safe band.

Implemented by `build.py` next to this file. This document is the spec; the
module is the truth. If they disagree, the module wins and this file is stale -
fix it.

## Canvas

1080 x 1920. Safe band **y 200 - 1620** (top keep-out 200, bottom keep-out 300).

## Tokens

| token | value | used for |
|---|---|---|
| `ink` | `#ffffff` | body and display type |
| `ink_dim` | `rgba(255,255,255,0.72)` | sublines |
| `accent` | `#f5c451` | the one highlighted word, rules, labels |
| `warn` | `#e2564b` | reserved; nothing uses it yet |
| `card` | `rgba(12,10,14,0.82)` | callout panel |
| `edge` | `rgba(255,255,255,0.14)` | panel border |
| display | `"Archivo Black", "Inter", system-ui` | headlines, kickers, captions |
| body | `"Inter", system-ui` | sublines, panel body |

Both families are in HyperFrames' auto-resolved font list. Adding a family that
is not gets you `font_family_without_font_face` from `check`, and text that
silently falls back to something generic in the render.

## Beat kinds

| kind | anchor | type | notes |
|---|---|---|---|
| `title` | center, y 820 | 104 / 78 / 62 px | steps down to fit three lines |
| `endcard` | center, y 820 | as title | |
| `kicker` | lower, y 1180 | 72 / 62 / 52 px | centred, one line ideally |
| `callout` | lower, y 1180 | 50 px in a panel | has a small accent label |
| `lower-third` | low, y 1360 | as callout | |

**One highlight per beat.** `_emphasise()` lifts the last word into the accent
colour. Two highlights in one graphic and neither reads as one.

## Type fitting is not cosmetic

`_fit()` steps the size down until the headline fits three lines, and `beat()`
reports a box height computed from the size it actually chose. The safe-zone
assertion checks that box - so a nominal height that ignores wrapping would be
checking a lie, and a four-line headline would sail past the assertion and land
in the caption zone.

## Captions

`CAPTION` block: stack at **y 1240**, 320 px tall, up to 4 words per card, 86 px.
Each word pops in on its own timing (`back.out(2.2)`, 140 ms).

The caption text span is `.cap-line`, not `.card` - the `callout` kind already
owns `.card`, and a caption inheriting its padded dark panel is a collision you
only see in a rendered frame.

## Motion

In: `fromTo` y +46 -> 0, `autoAlpha` 0 -> 1, scale 0.965 -> 1, 420 ms
`power3.out`.
Out: y -26, `autoAlpha` 0, 300 ms `power2.in`, starting 300 ms before the beat
ends.

Initial states live in the `fromTo`, never in CSS. Pairing a CSS `transform` with
a GSAP tween on the same property is rejected by lint as
`gsap_css_transform_conflict`, and for good reason - the two fight.

## Changing the look

Edit `build.py`, then `workflows/scripts/hf_build.sh <job>` and re-render the
affected parts. Never edit generated HTML under `hf-graphics/parts/` - it is
overwritten on every build and says so at the top of the file.
