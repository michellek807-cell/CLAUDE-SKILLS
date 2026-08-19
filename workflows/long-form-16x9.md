# Long-form, 16:9

Delivery frame **1920 x 1080**. `--format long`.

## Safe zones

No platform chrome eats the edges, so the keep-out is a conventional title-safe
margin: 60 px top and bottom, 96 px left and right. That is a nicety, not the
hard rule short-form has - but a lower third that runs to the frame edge still
looks like a mistake on a TV.

## Layout

| anchor | position | used by |
|---|---|---|
| `.lower3` | left, 72 px up from the bottom | `lower-third` |
| `.centered` | full width, y 300 | `title`, `endcard` |
| `.corner` | top right | `kicker` (pill) |

The `long-form-clean` preset is deliberately quieter than the short-form one. A
16:9 piece is watched rather than scrolled past, so the graphics support the
talking instead of shouting over it.

## Parts

Part target is **25 s**, longer than short-form's 15 s: fewer seams to manage,
still small enough that one note is one re-render. Part boundaries only land on
seams - gaps where no beat is in flight - so a beat is never split out of phase.

For a 20-minute piece that is roughly 48 parts. Re-rendering one of them after a
note costs well under a minute; re-rendering the video costs an afternoon. That
difference is the entire reason parts exist.

## Captions

Long-form does **not** get burned-in captions. It gets `outputs/<job>.srt`,
derived from the canonical transcript, which is what a platform's own caption
track wants anyway. `captions_build.py` refuses a long-form job unless you pass
`--force-long`.

## Pacing

`max_gap` can be more generous than short-form - 0.8-1.0 s reads as considered
rather than slow, and long-form viewers have already committed. Raise
`sentence_tail_pad` too; the beat after a full stop is what makes a long piece
feel edited rather than compressed.

```json
{ "max_gap": 0.90, "sentence_tail_pad": 0.260 }
```

in `projects/<job>/cut/cut.config.json`.

## Numbers

| | |
|---|---|
| canvas | 1920 x 1080 |
| title-safe | 60 px vertical, 96 px horizontal |
| fps | inherited from the source, exactly |
| video | h264_videotoolbox on macOS, libx264 elsewhere |
| audio | AAC 256k, 48 kHz, stereo |
| graphics part target | 25 s |
| captions | srt sidecar only |
| preset | `long-form-clean` |
