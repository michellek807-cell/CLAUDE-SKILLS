---
name: video-system
description: Entry point for this repo's video editing system - raw footage in, a finished cut out. Use whenever the user drops a clip and says "rough cut this", asks to edit/cut/caption/export a video, mentions a job in projects/, or asks about the pipeline, presets, HyperFrames graphics, or the locks. Routes to the per-step skills and knows the one command that runs the whole thing.
---

# Video system

This repo is not a code repo. It is a content system, and you are the editor.
Raw filmed footage goes into `projects/<job>/raw/`, a finished cut comes out of
`projects/<job>/outputs/`. Everything runs through the scripts in
`workflows/scripts/`, which the per-step skills drive.

Read `CLAUDE.md` at the root before doing anything non-obvious. Its **Lab Notes**
section holds the locks: rules that were learned by getting them wrong, one line
each. They are not style preferences. Breaking one produces audio that clicks,
timelines that drift, or a re-render that eats an afternoon.

## The one command

The finish line for this system is: the user drops a clip in and says
"rough cut this", and it runs end to end untouched.

```bash
workflows/scripts/rough_cut.sh /path/to/footage.mov --title "What It Is About"
```

That does intake, transcription, cut planning, boundary measurement, the
canonical transcript, and the editing-app handoff. If no `--title` is given it
parks the job under a provisional name, transcribes, then names the job from the
content - never from the camera filename.

Run `./check-setup.sh` first if anything looks like a missing dependency. It
reports, it never installs.

## Pipeline

| # | step | skill | command |
|---|---|---|---|
| 1 | Intake | `video-intake` | `workflows/scripts/intake.sh <job> <file>` |
| 2 | Rough cut | `video-rough-cut` | `workflows/scripts/rough_cut.sh <file\|job>` |
| - | *default finish* | `video-to-editing-app` | `workflows/scripts/to_editing_app.sh <job>` |
| 3 | Graphics | `video-graphics` | `workflows/scripts/hf_build.sh <job>` then `hf_render.sh <job> <part>` |
| 4 | Second pass | `video-second-pass` | iterate part by part, re-render only what changed |
| 5 | Captions | `video-captions` | `workflows/scripts/captions.sh <job> --render` |
| 6 | Music | `video-music-bed` | `workflows/scripts/music_bed.sh <job> <track>` |
| 7 | Export | `video-export` | `./finalize.sh <job>` then `./prune.sh <job>` |

Steps run in order. Every one of them is idempotent, so re-running after a config
tweak redoes only what changed.

## Two finishes, and the default is the timeline

After step 2 the default finish is **inside an editing app** - Premiere or
CapCut. The cut list is replayed against the raw footage so every cut arrives as
a trimmable edit point, not one flattened clip. Time to timeline is the metric;
transcription is the only slow step allowed. See `video-to-editing-app`.

Render a flat mp4 only when a flat mp4 is the deliverable:

```bash
workflows/scripts/rough_cut.sh <job> --flat
```

## Where things live

```
projects/<job>/
  raw/          the footage, copied in, never moved, never written to
  audio/        music beds and sourced audio
  assets/       stills, logos, anything hand-made
  broll/        cutaway footage
  outputs/      deliverables + the canonical transcript + the script
  hf-graphics/  the graphics build, its parts, and their renders
  transcript/   words.json (one WhisperX pass) + corrections.txt
  cut/          cutlist.json, the splice, the interchange files
  cache/        regenerable scratch; the only thing prune.sh reclaims
  job.json      machine state
  PROJECT.md    the resume doc - read this first on any job you did not just make
workflows/      format sheets, shared library, every pipeline script
presets/        locked look specs: one markdown + build.py per format
```

## Rules that are not negotiable

Full list with reasons in `CLAUDE.md` > Lab Notes. The ones that bite hardest:

- **Transcribe once.** `transcript/words.json` is written by one WhisperX pass
  and reused forever. `outputs/<job>.transcript.json` is derived from it by
  remapping kept words through the cut list. Nothing downstream re-transcribes -
  not captions, not the handoff, not the graphics.
- **Master the audio exactly once.** Static +10 dB, then a -6 dBFS limiter, then
  AAC 256k, on the assembled track. Never dynamic loudnorm, never per-segment FX.
  Any re-encode after that must match or exceed 256k.
- **Measure, do not trust.** Transcript word starts run 50-100 ms late. Every cut
  boundary is moved to an edge measured on an RMS envelope of the raw.
- **Nothing lives in `/tmp`.** macOS clears it. Builds live in the job folder.
- **Job names are content titles**, kebab-case. Never `C0042`, never a date.
- **Never hand-edit anything under `.claude/skills/`.** Those come from the
  HyperFrames CLI at a pinned version and are recorded in `skills-lock.json`.
  See `video-graphics-pin`.

## When something is wrong

- Audio clicks or holes -> `workflows/scripts/audio_qa.py` already told you;
  fix it in the cut list, never in the rendered audio.
- Timeline drifts -> a boundary is off the frame grid. Re-run `plan_cut.py`.
- Graphics render blank or the capture dies -> the HyperFrames pin moved, or a
  root composition is missing `data-start`. See `video-graphics-pin`.
- Anything at all -> `workflows/scripts/verify_pipeline.sh` runs the whole path
  on synthetic footage with known ground truth and asserts every lock. It needs
  no model download. If that passes and your job does not, the problem is the
  footage or the config, not the system.
