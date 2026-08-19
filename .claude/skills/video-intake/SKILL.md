---
name: video-intake
description: Pipeline step 1 - bring raw filmed footage into a job folder. Use when the user hands over a clip, a card, a Downloads path, or says "new video", "start a job", "ingest this". Copies the file (never moves it), probes it once, and names the job after the content rather than the camera filename.
---

# Step 1 - Intake

```bash
workflows/scripts/new-job.sh "Why Your Rough Cut Sounds Cheap" --format short
workflows/scripts/intake.sh why-your-rough-cut-sounds-cheap ~/Downloads/C0042.MP4
```

`rough_cut.sh` does both for you; use these directly when you want the job to
exist before the transcription starts.

## COPY, never move

`intake.sh` copies. The card, the Downloads folder, the original stays exactly as
the camera left it. Every later step treats `projects/<job>/raw/` as immutable
and only reads from it.

If a file with the same name is already in `raw/` with different bytes, intake
refuses rather than overwriting. Rename the incoming file.

## Job names are titles about the content

`why-your-rough-cut-sounds-cheap`, not `c0042`, not `2026-08-19-final-v2`.
Kebab-case. In three weeks the folder name is the only thing you will have to go
on, and a camera filename tells you nothing.

`new-job.sh` warns when a name looks like a camera filename. If a job already
got a provisional name:

```bash
workflows/scripts/rename-job.sh untitled-20260819-101500 "A Real Title"
```

That renames the folder, rewrites `job.json`, and renames the files inside
`outputs/` and `cut/` that carry the job name.

## Format

`--format short` (9:16, delivers 1080x1920, the default) or `--format long`
(16:9, 1920x1080). This drives the graphics canvas, the safe zones, and whether
captions get built at all - captions are short-form only.

Intake warns if the source geometry disagrees with the format you claimed.

## What intake produces

- `raw/<file>` - the copy
- `job.json` - duration, exact fps as a rational, geometry, codecs, sha256 of
  the raw bytes. Everything downstream reads fps from here so the whole job
  agrees on one frame grid.
- `PROJECT.md` - the resume doc, regenerated at every stage

The sha256 is what lets the transcription step know it has already covered these
exact bytes and skip re-running. Do not edit it.
