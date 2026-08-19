---
name: video-rough-cut
description: Pipeline step 2 - the rough cut. Use when the user says "rough cut this", "cut this down", "kill the ums", "tighten it", or hands over footage expecting an edit. Transcribes once with WhisperX large-v3, removes filler and dead air, measures every boundary against the audio, splices in one pass, masters the audio exactly once, and writes the finished script.
---

# Step 2 - Rough cut

```bash
workflows/scripts/rough_cut.sh /path/to/footage.mov --title "What It Is About"
```

One command, end to end: intake, transcribe, plan, measure, cut, canonical
transcript, handoff. Re-running it on an existing job resumes - every stage is
idempotent.

| flag | effect |
|---|---|
| `--title "..."` | content title; the folder is its kebab-case slug |
| `--format short\|long` | 9:16 (default) or 16:9 |
| `--aggressive` | also drop like / so / basically / actually / literally |
| `--keep-fillers` | dead air only, leave every word in |
| `--to-app` | stop at the cut list and hand off (the default) |
| `--flat` | also render the flat mastered mp4 |
| `--retranscribe` | force a re-transcribe. You almost never want this. |

## What it produces

- `transcript/words.json` - one WhisperX pass, raw, never hand-edited
- `cut/cutlist.json` - **the edit**. Every segment, its source in/out, its frame
  numbers, its audio handles, its crossfade lengths, and how far each boundary
  moved when measured.
- `cut/<job>.spliced.mkv` - the splice, PCM audio *(flat path only)*
- `cut/<job>.mastered.mp4` - mastered once, AAC 256k *(flat path only)*
- `outputs/<job>.transcript.json` - the canonical transcript
- `outputs/<job>.script.md` - the finished script
- `cut/<job>.fcp7.xml`, `.edl`, `.capcut/`, `.cuts.md` - the handoff

## The locks this step enforces

**Transcribe once.** `transcript/words.json` is keyed to the sha256 of the raw
bytes. Re-running is a no-op. Every later step reads it or the canonical
transcript derived from it. Nothing re-transcribes - not captions, not the
handoff. If you find yourself about to run a second ASR pass, stop: the answer
you want is already in `outputs/<job>.transcript.json`.

**Measure, do not trust.** Forced alignment reports a word's start 50-100 ms
after the real acoustic attack. `plan_cut.py` builds an RMS envelope of the raw
audio, finds each boundary's true edge, and moves the cut just outside it. Check
`stats` and each segment's `measured.in_delta` in `cutlist.json` - they should
be consistently negative at in-points. If they are near zero, the envelope
threshold is wrong for this recording.

**Snap to the frame grid.** In-points floor to a frame, out-points ceil, so no
word gets clipped and every segment is a whole number of frames. Per-segment
video and audio durations then agree and concat has nothing to pad. Skip this
and the timeline drifts a little further at every joint.

**Room-tone joints.** Each segment's audio window is widened by half a crossfade
at each joint, into the part of the take being thrown away - real continuing
room tone. The renderer equal-power crossfades those handles. Half the fade
comes from each side, so the assembled audio is exactly as long as the assembled
video. Never a fade to zero: that trades a click for an audible hole.

**Master exactly once.** The splice carries PCM. The master stage then runs one
time over the assembled track: static +10 dB, a -6 dBFS limiter, AAC 256k, video
stream-copied. Never dynamic loudnorm - it pumps on speech. Never per-segment
audio FX - every segment edge becomes a click.

**QA after every splice.** `audio_qa.py` runs automatically and reports joint
clicks, silent holes, limiter pressure, A/V drift and the encode bitrate. It
prints findings; it does not silently pass.

## Tuning

Copy defaults into `projects/<job>/cut/cut.config.json` (or repo-wide into
`workflows/cut.config.json`) and override only what you need:

| key | default | what it does |
|---|---|---|
| `max_gap` | 0.60 | silence longer than this between kept words is dead air |
| `head_pad` / `tail_pad` | 0.060 / 0.100 | room tone kept around a measured edge |
| `sentence_tail_pad` | 0.180 | a longer beat after `.` `?` `!` |
| `crossfade_ms` | 24 | joint length; raise it if joints tick |
| `floor_offset_db` | 8.0 | speech threshold above the measured noise floor |
| `min_segment` | 0.20 | segments shorter than this are noise |
| `drop_aggressive` | false | the like/so/basically list |

After a change, re-run `rough_cut.sh <job>`. It reuses the transcript and only
re-plans and re-renders.

## Spelling

Never edit `words.json`. Put single-token whole-word swaps in
`projects/<job>/transcript/corrections.txt` (or repo-wide in
`workflows/corrections.txt`):

```
hyperfrhames -> HyperFrames
```

They are applied when the canonical transcript is written, so the cut list, the
captions and the script all agree, and the raw machine output stays honest.

## If the QA pass complains

- **clicks at joints** - raise `crossfade_ms`, or move that boundary further
  into silence. Fix it in the cut list. Never patch the rendered audio.
- **silent holes** - a fade to zero crept in; room tone should carry through.
- **limiter working hard** - the take is hot; lower `VS_GAIN_DB`. Do not reach
  for a compressor.
- **drift** - a boundary is off the frame grid; re-run the planner.
