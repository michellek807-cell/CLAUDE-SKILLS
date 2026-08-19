---
name: video-music-bed
description: Pipeline step 6, optional - put a flat music bed under the voice. Use when the user asks for music, a bed, a backing track, or says "add music" to a job. Mixes at one static level into the pre-master audio and re-runs the single master chain; no ducking, no automation.
---

# Step 6 - Music bed (optional)

```bash
workflows/scripts/music_bed.sh <job> ~/Music/bed.wav
workflows/scripts/music_bed.sh <job> ~/Music/bed.wav --level -18
workflows/scripts/music_bed.sh <job> --none        # remove it, re-master voice only
```

Default level is -22 dB under the voice (`VS_MUSIC_DB`).

## Flat means flat

One static level for the whole piece. No sidechain ducking, no volume
automation, no compressor riding the voice.

Dynamic gain on a music bed is the same failure as dynamic loudnorm on a voice
track: it breathes, and once you hear it you cannot stop hearing it. If the bed
is fighting the voice, **the bed is too loud** - turn it down. Do not automate it.

The only fades are one at each end of the film, so it does not start or stop
with a thud. Never at a joint: the voice track's own room tone carries there.

## Why it mixes into the pre-master

The mix happens on `cut/<job>.spliced.mkv` - the PCM splice - and then the one
master chain runs over the sum: +10 dB, -6 dBFS limiter, AAC 256k. That keeps
the lock intact: the assembled track is polished exactly once.

Mixing into the already-mastered AAC would be a second lossy generation on top
of a track that was already limited, and the limiter would then be fighting
material it had already shaped.

The script runs `audio_qa.py` afterwards. Watch the limiter pressure line: a bed
that pushes it over about 2 % of samples is too loud, whatever it sounds like on
laptop speakers.

## Housekeeping

The track is copied into `projects/<job>/audio/`, which `prune.sh` never touches.
`job.json` records the file and the level so the mix is reproducible.
