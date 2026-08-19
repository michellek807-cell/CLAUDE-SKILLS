---
name: video-export
description: Pipeline step 7 - promote the finished render and reclaim disk. Use when the user says "export", "finalize", "ship it", "give me the file", "clean up", or asks where the final video is. Copies the newest render to outputs/<job>.final.mp4 and ~/Downloads, then prunes only regenerable cache.
---

# Step 7 - Export

```bash
./finalize.sh <job>              # promote the newest render
./finalize.sh <job> some.mp4     # promote a specific file
./finalize.sh <job> --no-copy    # skip the ~/Downloads copy
./finalize.sh --list             # every job and its final
./prune.sh <job>                 # reclaim regenerable cache
```

## finalize.sh

Picks the most recently written deliverable in the job (`cut/<job>.graded.mp4`,
then `cut/<job>.mastered.mp4`, then anything in `outputs/`), copies it to
`outputs/<job>.final.mp4`, and drops a copy at `~/Downloads/<job>.mp4` so it is
where you actually look for it. Set `VS_DOWNLOADS` to point elsewhere.

**Promotion is a copy, never a re-encode.** The audio was mastered exactly once
at AAC 256k; re-encoding at the finish line would silently take a second
generation off it for no benefit. If the file is not already an mp4, finalize
refuses and tells you to render it as one upstream. If its audio is under
250 kbps it warns and names the problem - find the stage that re-encoded it.

## prune.sh

```bash
./prune.sh <job>              # cache + the pre-master PCM splice
./prune.sh <job> --dry-run    # say what it would delete
./prune.sh <job> --deep       # also drop the graphics part renders
./prune.sh --all              # every job that reached 'final'
```

Deletes only what regenerates from `cutlist.json`, `timeline.json` and the raw
file: frame caches, filtergraph scratch, the PCM splice, and with `--deep` the
part renders.

It will **never** touch, at any flag:

| | |
|---|---|
| `raw/` | the footage. Deleting it is unrecoverable. |
| `outputs/` | the deliverables and the canonical transcript |
| `transcript/` | one WhisperX pass you are not paying for twice |
| `audio/` `assets/` `broll/` | things you sourced by hand |
| `cut/*.json` | `cutlist.json` **is** the edit |

That list is hard-coded, not configurable, and the script refuses to run at all
on a folder that does not have every protected directory - if the shape is
unfamiliar, it is not a job folder and prune stops.

## Handing over

`PROJECT.md` is regenerated at every stage: the source, the cut stats, the
outputs, the pipeline state, and the folder sizes with what is and is not
prunable. It is the thing to open first on a job you did not just make.
