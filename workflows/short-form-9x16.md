# Short-form, 9:16

Delivery frame **1080 x 1920**. The default format for a new job.

## Safe zones - the hard one

```
y    0 ┌─────────────────────────┐
       │   KEEP OUT  (200 px)    │  handle, sound credit, platform chrome
y  200 ├─────────────────────────┤
       │                         │
       │      the only band      │  face, graphics, captions - all of it
       │      that is yours      │
       │                         │
y 1620 ├─────────────────────────┤
       │   KEEP OUT  (300 px)    │  caption stack, CTA, progress bar
y 1920 └─────────────────────────┘
```

Nothing that carries meaning goes above y=200 or below y=1620. Not the subject's
eyes, not a lower third, not a caption. This is enforced in three places:

1. `presets/short-form-punch/build.py` lays every element out inside a `.safe`
   box, so drift is structurally hard rather than merely discouraged
2. `hf_build_parts.py` and `captions_build.py` assert each returned box against
   the band and **fail the build** for short-form
3. `hf_render.sh` passes the same band to HyperFrames as
   `--caption-zone ...;severity=error`, so the renderer checks it independently

## Layout anchors used by the preset

| anchor | y | used by |
|---|---|---|
| upper | 380 | rare; only when the subject is low in frame |
| center | 820 | `title`, `endcard` |
| lower | 1180 | `kicker` |
| low | 1360 | `lower-third` |
| captions | 1240-1560 | the caption stack |

A title at 820 and captions at 1240 do not collide as long as the headline fits
in three lines - which is why `_fit()` steps the type down (104 -> 78 -> 62 px)
and reports the true box height rather than a nominal one.

## Reframing

Sources are usually 16:9. `overlay_graphics.sh` scales to cover and centre-crops:

```
scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920
```

Centre is a default, not a decision. When the subject is off to one side:

```bash
VS_CROP_X='(iw-ow)/3' workflows/scripts/overlay_graphics.sh <job>
```

## Captions

Short-form gets burned-in captions; long-form gets an `.srt` sidecar. Cards of up
to 4 words, broken on a pause over 450 ms or a span over 2.6 s, one word per card
lifted into the accent colour. See the `video-captions` skill.

## Pacing

`max_gap` 0.60 s is already tight. Going below about 0.45 s starts clipping the
breath people need to follow a sentence, and it reads as anxious rather than
punchy. If it still feels slow, the problem is usually the writing, not the gaps.

## Numbers

| | |
|---|---|
| canvas | 1080 x 1920 |
| safe band | y 200 - 1620 |
| fps | inherited from the source, exactly (`r_frame_rate`) |
| video | h264_videotoolbox on macOS, libx264 elsewhere |
| audio | AAC 256k, 48 kHz, stereo |
| graphics part target | 15 s |
| caption part target | 10 s |
| preset | `short-form-punch` |
