---
name: video-second-pass
description: Pipeline step 4 - the review loop. Use when the user gives notes on a cut or on graphics ("that beat is too long", "move the title", "the joint at 0:42 ticks", "re-render just that part"), or asks to iterate on a job. Turns notes into the smallest change that fixes them, part by part, without re-rendering the whole video.
---

# Step 4 - Second pass

This is the step where the user watches it and calls adjustments, and you make
them. The discipline is: **change the smallest thing, re-render the smallest
thing, show it back.**

Read `projects/<job>/PROJECT.md` first. It says what stage the job is at, what
the numbers were, and what the last run did.

## Where a note actually belongs

| the note | where it goes | what to re-run |
|---|---|---|
| "cut this bit / keep that bit" | `cut/cutlist.json` via `cut/cut.config.json` | `rough_cut.sh <job>` |
| "it's still got ums" | `drop_aggressive: true`, or add tokens to `fillers` | `rough_cut.sh <job>` |
| "too choppy / too tight" | raise `max_gap`, raise `sentence_tail_pad` | `rough_cut.sh <job>` |
| "that joint ticks" | raise `crossfade_ms`; check `audio_qa` output | `rough_cut.sh <job>` |
| "too quiet / too squashed" | `VS_GAIN_DB` | `render_cut.sh <job>` |
| "wrong word on screen" | `hf-graphics/timeline.json` | `hf_build.sh` + `hf_render.sh <job> part-NN` |
| "move / restyle the graphic" | `presets/<name>/build.py` | `hf_build.sh` + the affected parts |
| "misspelled name" | `transcript/corrections.txt` | `rough_cut.sh <job>` (reuses the transcript) |
| "captions are late" | caption timing comes from the canonical transcript; fix the cut, not the captions | |

Notice what is missing: nothing is ever fixed by editing the rendered file, and
nothing is ever fixed by re-transcribing.

## Re-render only what changed

```bash
workflows/scripts/hf_render.sh <job> part-03      # one part
workflows/scripts/captions.sh <job> --render part-02
workflows/scripts/hf_concat_parts.sh <job>        # rejoin, stream copy
workflows/scripts/overlay_graphics.sh <job>       # re-composite
```

Parts exist for exactly this. `hf_build.sh` re-derives every part from
`timeline.json`, but only the parts whose content changed need re-rendering -
diff them or re-render the one the note is about.

Joining is a stream copy, so a freshly rendered part sits next to older parts
with no quality difference and no re-encode.

## Re-running the cut is cheap

`rough_cut.sh <job>` on an existing job reuses `transcript/words.json` - the
expensive step never repeats. It re-plans, re-measures, re-splices, re-masters
and re-derives the canonical transcript. On a ten-minute take that is under a
minute.

## Record what you learned

Two places, and both matter:

- `projects/<job>/PROJECT.md` below the NOTES marker - what got rejected and
  why, for the next person opening this job cold. Everything below that marker
  is preserved across regeneration.
- `CLAUDE.md` > **Lab Notes** - if the note revealed something non-obvious that
  will bite again on the next video, add a line. That section is the reason this
  system stopped repeating its mistakes.

## Sanity check

If a change makes things worse in a way you cannot explain:

```bash
workflows/scripts/verify_pipeline.sh
```

Runs the whole path on synthetic footage with known ground truth and asserts
every lock. Needs no model download. If it passes and the job still misbehaves,
the problem is the footage or the config, not the system.
