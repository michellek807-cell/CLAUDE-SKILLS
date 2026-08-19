# long-form-clean

The locked look for 16:9 long-form. Quieter than short-form on purpose: a 16:9
piece is watched, not scrolled past, so graphics support the talking rather than
compete with it.

Implemented by `build.py` next to this file.

## Canvas

1920 x 1080. Title-safe margin 60 px vertical, 96 px horizontal. No platform
chrome to dodge.

## Tokens

| token | value | used for |
|---|---|---|
| `ink` | `#f4f4f5` | type |
| `ink_dim` | `rgba(244,244,245,0.66)` | roles, sublines |
| `accent` | `#7cc4ff` | the lower-third rule, one highlighted word |
| `card` | `rgba(14,16,20,0.86)` | bar and pill fill |
| `edge` | `rgba(255,255,255,0.10)` | pill border |
| display | `"Inter Tight", "Inter", system-ui` | names, titles |
| body | `"Inter", system-ui` | roles, sublines |

## Beat kinds

| kind | layout | type |
|---|---|---|
| `title` / `endcard` | centred, y 300, over a soft scrim | 96 px, 800 weight |
| `lower-third` | bottom left, 8 px accent bar on the left edge | 46 px name, 28 px role |
| `kicker` | top right pill | 30 px |

The lower third is the workhorse: name in `text`, role in `sub`.

## Motion

Lower thirds slide in from the left (`x: -56`), everything else rises
(`y: +40`); 460 ms `power3.out` in, 340 ms `power2.in` out. Direction carries
meaning here - a lower third that drops in from above reads as a notification.

## Parts

Part target 25 s. See `workflows/long-form-16x9.md`.

## Captions

None burned in. Long-form gets `outputs/<job>.srt` from the canonical transcript.

## Changing the look

Edit `build.py`, rebuild, re-render only the affected parts. Never edit generated
HTML.
