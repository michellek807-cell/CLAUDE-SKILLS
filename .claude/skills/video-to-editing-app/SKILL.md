---
name: video-to-editing-app
description: The default finish after the rough cut - drive Premiere Pro, CapCut, Resolve or Final Cut by replaying the cut list against the raw footage so every cut arrives as a trimmable edit point. Use when the user wants to finish in an app, says "open it in Premiere/CapCut", "give me the timeline", "I want to tweak the cuts", or when a flat render would throw away the edit points.
---

# The default finish: hand off to the editing app

After step 2 the default finish is **inside an editing app**, not a flat render.

```bash
workflows/scripts/to_editing_app.sh <job>            # auto-detect
workflows/scripts/to_editing_app.sh <job> premiere
workflows/scripts/to_editing_app.sh <job> capcut
workflows/scripts/to_editing_app.sh <job> none       # just write the files
```

`rough_cut.sh` runs this for you unless you pass `--flat`.

## Why not a flat render

A flattened mp4 is one clip with every boundary already burned into the pixels.
The first note you get back - "hold that beat two frames longer", "let the
laugh breathe" - sends you back to the config and costs a full re-render.

Replaying the cut list against the ORIGINAL file puts N trimmable clips on the
timeline instead. Every cut is still an edit point. Dragging one costs seconds.

**Time to timeline is the metric.** Transcription is the only slow step allowed
on this path; the cut list and the transcript are produced in seconds after it.
Skip the flat render entirely unless a flat mp4 is genuinely the deliverable.

## What gets written

| file | for |
|---|---|
| `cut/<job>.fcp7.xml` | Premiere Pro, DaVinci Resolve, Final Cut, Media Composer |
| `cut/<job>.edl` | CMX3600 - the universal fallback |
| `cut/<job>.capcut/` | a CapCut draft folder |
| `cut/<job>.cuts.md` | the razor list, for cutting by hand anywhere else |
| `outputs/<job>.srt` | the canonical transcript, cut-relative |

The XML carries one video clipitem and one linked audio clipitem per cut, all
pointing at `raw/`, with source in/out as frame numbers on the job's frame grid.

## Per app

**Premiere Pro / Resolve / Final Cut.** Import `cut/<job>.fcp7.xml`
(File > Import). It builds the sequence and relinks to `raw/`. On macOS the
script opens it for you. This is the path that does not rot: FCP7 XML has been
stable for over a decade.

**CapCut.** The script writes a draft folder and, on macOS, installs it into
`~/Movies/CapCut/User Data/Projects/com.lveditor.draft/<job>`. Restart CapCut
and pick the job from Drafts. CapCut's draft schema moves between releases - the
version this was written against is the `CAPCUT_SCHEMA` constant in
`workflows/scripts/edl_export.py`, and it is the first thing to check if CapCut
refuses the draft. If it does, fall back to `cut/<job>.cuts.md`: import the raw
file, then razor at the listed timecodes.

**WSL2 / Linux.** Nothing is launched - a WSL shell cannot reliably start a
Windows app, and guessing is worse than saying where the file is. The paths are
printed; reach them from Windows under `\\wsl$`.

## After the app

Whatever the app exports, promote it through `finalize.sh`, which copies rather
than re-encodes:

```bash
cp ~/exports/whatever.mp4 projects/<job>/outputs/
./finalize.sh <job>
```

If the app's export is below AAC 256k, `finalize.sh` says so. Raise the app's
audio bitrate rather than accepting it - the audio was mastered once and every
later encode has to match or exceed that.
