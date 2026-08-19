# Video editing system

This is not a code repo. It is a content system, and Claude is the editor. Raw
filmed footage goes in, a finished exported cut comes out. Everything runs
through skills in `.claude/skills/` driving scripts in `workflows/scripts/`.

Start here: **`.claude/skills/video-system/SKILL.md`** routes to the per-step
skills. **Lab Notes** at the bottom of this file holds the locks - rules learned
by getting them wrong. They are not preferences.

```bash
./check-setup.sh                                              # report only, never installs
workflows/scripts/rough_cut.sh footage.mov --title "A Title"  # the whole rough cut
workflows/scripts/verify_pipeline.sh                          # self test, every lock
```

## Pipeline

Linear. Every job runs these in order, and every stage is idempotent - re-running
after a config change redoes only what changed.

| # | step | what it does | skill | command |
|---|---|---|---|---|
| 1 | **Intake** | **Copy** the raw file into `raw/`, never move it. Probe once. | `video-intake` | `intake.sh <job> <file>` |
| 2 | **Rough cut** | WhisperX large-v3 transcribe + word align. Kill filler and dead air. Measure every boundary. Splice. Master once. Produces the cut **and** the finished script. | `video-rough-cut` | `rough_cut.sh <file>` |
| - | *default finish* | Replay the cut list against the raw footage inside Premiere or CapCut, so every cut is a trimmable edit point. | `video-to-editing-app` | `to_editing_app.sh <job>` |
| 3 | **Graphics** | Plan beat by beat first, then build. 9:16 short-form or 16:9 long. | `video-graphics` | `hf_build.sh <job>` then `hf_render.sh <job> <part>` |
| 4 | **Second pass** | The user reviews and calls adjustments. Iterate part by part. | `video-second-pass` | re-render only what changed |
| 5 | **Captions** | Short-form only, from the canonical transcript, never re-transcribed. | `video-captions` | `captions.sh <job> --render` |
| 6 | **Music** | Optional flat bed under the voice. | `video-music-bed` | `music_bed.sh <job> <track>` |
| 7 | **Export** | Promote the newest render, then reclaim regenerable cache. | `video-export` | `./finalize.sh <job>` then `./prune.sh <job>` |

After step 2 the default finish is inside an editing app, not a flat render.
Render flat only when a flat mp4 is the deliverable (`rough_cut.sh <job> --flat`).

## Folders

```
CLAUDE.md               this file
check-setup.sh          OS-aware dependency report. Reports, never installs.
finalize.sh             promote the newest render -> outputs/<job>.final.mp4 + ~/Downloads
prune.sh                reclaim regenerable cache only. Never raw/ or outputs/.
skills-lock.json        every skill's source, path, and sha256 of its SKILL.md bytes

projects/<job>/         one folder per video, named for the CONTENT
  raw/                  the footage. Copied in, immutable, never pruned.
  audio/                music beds and sourced audio
  assets/               stills, logos, anything hand-made
  broll/                cutaway footage
  outputs/              deliverables + <job>.transcript.json + <job>.script.md
  hf-graphics/          the graphics build: timeline.json, parts/, renders/
  transcript/           words.json (one WhisperX pass) + corrections.txt
  cut/                  cutlist.json (the edit), the splice, the interchange files
  cache/                regenerable scratch - the only thing prune.sh reclaims
  job.json              machine state
  PROJECT.md            the resume doc. Read this first on any job you did not just make.

workflows/              format detail sheets + utility scripts
  short-form-9x16.md    safe zones, anchors, reframing, pacing
  long-form-16x9.md     layout, part sizing, pacing
  corrections.txt       repo-wide transcript spelling fixes
  lib/common.sh         shared bash. Owns the pin, the master chain, the encoder branch.
  scripts/              every pipeline script
  vendor/gsap.min.js    vendored, so renders never depend on a CDN

presets/                locked look specs: one markdown + build.py per format
  short-form-punch/     9:16 - spec.md + build.py
  long-form-clean/      16:9 - spec.md + build.py

.claude/skills/         the HyperFrames pack (pinned, CLI-installed) + the video-* skills
```

## Machine

macOS or WSL2 Ubuntu. Needs ffmpeg/ffprobe, uv, node, Python + PIL. On Linux PIL
comes from apt (`python3-pil`), never bare pip. `./check-setup.sh` verifies every
dependency and says exactly what is missing, with the install line for the
machine it is on.

**The only platform branch in the media pipeline is the video encoder** -
`h264_videotoolbox` on macOS, `libx264` elsewhere - and it lives in one function,
`vs_video_encoder_args` in `workflows/lib/common.sh`. Every ffmpeg invocation,
every path, every filter is identical on both. Shell scripts run under stock
bash 3.2 (macOS) and bash 5.

Two things outside the pipeline are OS-aware because they cannot be anything
else: `check-setup.sh` prints the right install line for the machine it is on,
and `to_editing_app.sh` can only *launch* a GUI app on macOS - everywhere else it
prints the path, because a WSL2 shell cannot reliably start a Windows app and
guessing is worse than saying where the file is. If you find yourself writing a
third `uname` test, you are probably solving the wrong problem.

## Graphics engine

Graphics and captions render through **HyperFrames**, an npm package - not a repo
you clone.

```bash
npx hyperframes@0.7.68 skills     # installs the skill pack
npx hyperframes@0.7.68 doctor     # downloads the headless browser it renders with
workflows/scripts/hf_pin.sh install   # does both, then syncs and locks
```

The installed skills are copied into `.claude/skills/` and recorded in
`skills-lock.json` with the sha256 of each `SKILL.md`'s bytes. Update them
**through that CLI only** - never by hand editing. `hf_pin.sh verify` re-hashes
everything and fails on drift.

The version is pinned in every job's render path, spelled out on every
invocation. See Lab Notes and the `video-graphics-pin` skill.

---

# Lab Notes

Learned the hard way. One line each, with the reason, because a rule without its
reason gets "simplified" away by the next person - including future me.

**Transcribe once per video.** `transcript/words.json` is one WhisperX pass, keyed
to the sha256 of the raw bytes, reused forever. Nothing downstream re-transcribes.

**Derive the canonical transcript, never re-derive it.**
`outputs/<job>.transcript.json` comes from remapping kept words through the cut
list. Two ASR passes give two disagreeing truths that drift apart at every re-cut.

**Cut A/V in one lossless filtergraph.** One pass, one graph. Segment files plus a
concat demuxer is N encodes and N chances to drift.

**Polish the assembled track exactly once**: static +10 dB, then a -6 dBFS
limiter, then AAC 256k. Video is stream-copied so it is never re-encoded.

**Never dynamic loudnorm.** It pumps on speech, and once you hear it you cannot
stop hearing it.

**Never per-segment audio FX.** Every segment edge becomes a click. Process the
sum, once.

**Any re-encode after mastering must match or exceed 256k.** `finalize.sh` checks
and names the stage that dropped it.

**Snap every cut boundary to the video frame grid.** Otherwise per-segment video
and audio durations differ, concat pads the gap, and the timeline drifts a little
further at every joint.

**Joints are short equal-power crossfades over real continuing room tone**, never
fades to zero - that trades a click for an audible hole. Each segment's audio
window is widened by half a crossfade into the part of the take being thrown
away, so the fade is made of audio that actually exists there and the assembled
audio comes out exactly as long as the assembled video.

**Measure cut boundaries, do not trust transcript timestamps.** Forced alignment
reports a word's start 50-100 ms after its real acoustic attack. Scan an RMS
envelope of the raw and move each cut just outside the measured edge.

**Run an audio QA pass after every splice** - joint clicks, silence gaps, limiter
pressure. Print warnings, never silently pass. A click means the splice was
wrong; the fix belongs in the cut list, never in the rendered audio.

**Transcript spelling fixes live upstream** in one corrections file, applied as
the canonical transcript is written. Single-token whole-word swaps only, text
never timings. `words.json` stays untouched - it is evidence, not a draft.

**Nothing lives in `/tmp`.** macOS clears it, and a half-cleared frame cache
mid-render is a confusing failure. Builds live in the job folder; the HyperFrames
frames cache is pointed at `projects/<job>/cache/`.

**Long graphics render as short seamless parts from one shared timeline**, so a
tweak re-renders one part, not the whole video. Part boundaries only land on
seams - gaps where no beat is in flight - so a beat is never split out of phase.
Joining parts is a stream copy, so a freshly rendered part sits next to older
ones with no quality difference.

**Short-form safe zones**: no key visuals in the top 200 px or the bottom 300 px
of 1080x1920. Face, captions and graphics stay inside y 200-1620. Enforced by the
preset's layout, asserted at build time, and checked independently by HyperFrames
via `--caption-zone`.

**On the editing-app path, skip the flat render entirely.** Produce the cut list
and transcript in seconds and hand off to the app. Time to timeline is the
metric; transcription is the only slow step allowed. A flat mp4 is one clip with
every boundary burned in, and the first note you get back costs a full re-render.

**Job names are kebab-case titles about the content**, never the camera filename.
`C0042` tells you nothing in three weeks.

**Pin HyperFrames and spell the version out on every invocation.** `npx
hyperframes` floats to latest and past releases have broken the composition
contract mid-job: **0.7.42** started requiring `data-start`,
`data-composition-id`, `data-width` and `data-height` on the root comp or the
render capture dies; **0.7.67** shipped a change that was reverted in **0.7.68**.
Start at 0.7.68 and move the pin deliberately - one part re-rendered and reviewed
before anything else moves.

**Never hand-edit anything under `.claude/skills/`.** It comes from the CLI at a
pinned version and is hashed in `skills-lock.json`. Local edits are silently
destroyed by the next sync.

## Added while building this

**Vendor GSAP; never load it from a CDN at render time.** A blocked CDN does not
fail the render - the capture succeeds, every tween is missing, and the only
trace is a `sub_timeline_script_failure` warning buried in the log. Found this on
the first real render. `workflows/vendor/gsap.min.js`, refreshed by
`vendor_gsap.sh`.

**Each graphics part is its own HyperFrames project root.** Assets referenced
`../../shared/` fail lint as `invalid_parent_traversal_in_asset_path`: renders
rewrite the path but Studio preview and other live consumers resolve against the
project root and 404. Root-relative `shared/...` inside each part folder works
everywhere.

**`-ac 1` is not a 0.5/0.5 downmix.** swresample uses -3 dB coefficients for
stereo to mono, so two identical channels come back √2 hot and every level you
measure off it is 3 dB wrong. Cost an hour chasing a limiter that was working
correctly. Measure peaks per channel (`vslib.peak_dbfs`); downmix explicitly with
`pan=mono|c0=0.5*c0+0.5*c1` when you want an envelope.

**Only use fonts HyperFrames auto-resolves.** `Impact` and bare `Helvetica Neue`
fail `check` with `font_family_without_font_face`, and text falls back to
something generic in the render while looking right in preview. `Archivo Black`,
`Inter` and `Inter Tight` resolve.

**Clamp each caption card's hold to the next card's entry.** Overlapping clips on
the same track is `overlapping_clips_same_track` and a genuine render conflict -
two clips fighting for the same frames.

**A graphic's declared box must be computed from the type size it actually
chose.** A nominal height that ignores wrapping means the safe-zone assertion is
checking a lie, and a four-line headline sails past it into the caption zone.

**Give generated clip elements stable ids.** Without them `check` reports
`studio_missing_editable_id` and Studio has no edit target for its timeline.

**Fold a runt tail part back into its neighbour.** A 0.4 s part is all render
overhead and no benefit.

**`amix=duration=first` ends on the first input's last whole frame** and drops
~50 ms off the tail. The music bed uses `duration=longest` with the bed already
atrimmed to the voice length, which is exactly the voice length. Caught by the
QA pass's drift check, which is the entire reason that check exists.

**`prune.sh` measured directories only.** `[ -d ]` before `du` silently reported
0 B for every *file* it was about to delete, so the one big reclaim in a job -
the PCM splice - looked free. Size helpers take `-e`, not `-d`.

**A one-word caption card is a flash, not a caption**, and dropping captions to
nothing for 200 ms between cards reads as a glitch. Fold runt cards into their
neighbour and hold a card across any gap under 0.5 s.

**Don't put the accent on punctuation.** Highlighting "the last word" of a
truncated headline highlights the ellipsis - the one place an accent cannot mean
anything.

**Weights downloads fail deep inside huggingface_hub** and the traceback says
nothing actionable. `transcribe.py` catches proxy/DNS/403 failures and prints
what to do instead.
