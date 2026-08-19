---
name: video-captions
description: Pipeline step 5 - burned-in captions for short-form, rendered through HyperFrames from the canonical transcript. Use when the user asks for captions, subtitles, word-by-word text, or "add captions" to a 9:16 job. Never re-transcribes; word timings come from the single WhisperX pass remapped through the cut list.
---

# Step 5 - Captions

**Short-form only.** A 16:9 piece gets an `.srt` sidecar, not burned-in text.
`captions_build.py` refuses a long-form job unless you pass `--force-long`.

```bash
workflows/scripts/captions.sh <job>                    # build compositions + srt
workflows/scripts/captions.sh <job> --render           # build, then render
workflows/scripts/captions.sh <job> --render part-02   # re-render one part
```

## Built from the canonical transcript, never re-transcribed

**LOCK.** Word timings come from `outputs/<job>.transcript.json` - the single
WhisperX pass, remapped through the cut list. Running a second model over the
rendered file would produce a second, disagreeing truth, and the two would drift
apart at every re-cut.

If a caption says the wrong word, the fix is `transcript/corrections.txt` and a
re-run of `rough_cut.sh`. Never a second ASR pass, never editing the caption
HTML.

## What gets produced

- `hf-graphics/captions/parts/part-NN/` - one self-contained HyperFrames project
  per part, same parts discipline as the graphics
- `hf-graphics/captions/renders/part-NN.mov` - alpha MOV
- `hf-graphics/captions.mov` - the joined track (stream copy)
- `outputs/<job>.captions.srt` - word-grouped srt, from the same source

Caption parts are deliberately shorter than graphics parts (10 s target). A
caption part is what you re-render to fix one word, so it should be cheap - and
thirteen cards on one track is more timeline than anyone wants to read.

## Cards

Words are grouped into cards of up to `words_per_card` (4 by default), broken
early on a pause over 450 ms or a span over 2.6 s. Each word pops in on its own
timing inside the card. One word per card may be lifted into the accent colour -
the longest word, and only if it earns it. One highlight, never two.

Tune with `--per-card N`, or `CAPTION["words_per_card"]` in the preset.

## Safe zone

The caption stack sits at y 1240-1560 on 1080x1920: inside the 200-1620 band,
above the platform's own caption furniture, below the face. The box is asserted
at build time, and a violation fails the build. If captions need to move, change
`CAPTION["y"]` in `presets/short-form-punch/build.py` - and keep the whole box
inside the band.

## One caption at a time

Each card's hold is clamped to the next card's entry. Two caption clips
overlapping on the same track is a render conflict, and HyperFrames' lint calls
it `overlapping_clips_same_track`. If you see that, the clamp was bypassed.

## Compositing

```bash
workflows/scripts/hf_concat_parts.sh <job> --captions
workflows/scripts/overlay_graphics.sh <job>
```

`overlay_graphics.sh` layers graphics then captions over the reframed cut and
stream-copies the audio.
