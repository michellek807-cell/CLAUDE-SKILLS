# workflows/

Format detail sheets, the shared library, and every script the pipeline runs.

## Detail sheets

| file | |
|---|---|
| `short-form-9x16.md` | the 9:16 format: safe zones, anchors, reframing, pacing |
| `long-form-16x9.md` | the 16:9 format: layout, part sizing, pacing |
| `corrections.txt` | repo-wide transcript spelling fixes |
| `hyperframes-skills.txt` | the roster of skills the pinned HyperFrames release owns, written from the installer's own output |
| `cut.config.json` | *(optional, create it)* repo-wide rough-cut overrides |
| `vendor/gsap.min.js` | GSAP, vendored so renders never depend on a CDN |

## lib/

`common.sh` - sourced by every shell script. Bash 3.2 safe (macOS ships 3.2), so
no associative arrays, no `mapfile`, no `${var,,}`, no globstar.

It owns the pin (`VS_HF_VERSION`), the locked audio master chain
(`vs_master_filter`), the job path helpers, and **the only platform branch in the
system**: `vs_video_encoder_args`, which picks `h264_videotoolbox` on macOS and
`libx264` everywhere else. If you find yourself writing a second `uname` test,
you are probably solving the wrong problem.

## scripts/

Run in pipeline order.

| script | step | |
|---|---|---|
| `new-job.sh` | 1 | create a job folder from a content title |
| `intake.sh` | 1 | copy the raw file in, probe it once |
| `intake_probe.py` | 1 | write duration / fps / geometry into job.json |
| `rough_cut.sh` | 2 | **the whole rough cut, end to end** |
| `transcribe.py` | 2a | WhisperX large-v3 + word align, exactly once |
| `plan_cut.py` | 2b | filler + dead air, measured boundaries, frame grid |
| `build_filtergraph.py` | 2c | one lossless filtergraph for the whole cut |
| `render_cut.sh` | 2c | splice, then master the audio exactly once |
| `audio_qa.py` | 2c | clicks, holes, limiter pressure, drift, bitrate |
| `make_transcript.py` | 2d | the canonical transcript + the finished script |
| `edl_export.py` | 2e | FCP7 XML, EDL, CapCut draft, razor list, srt |
| `to_editing_app.sh` | 2e | **the default finish** - drive the app |
| `graphics_plan.py` | 3a | the beat sheet and the shared timeline |
| `hf_build_parts.py` | 3b | slice the timeline into re-renderable parts |
| `hf_build.sh` | 3 | plan + build |
| `hf_render.sh` | 3 | render parts through the pinned CLI |
| `hf_concat_parts.sh` | 3 | join parts, stream copy |
| `overlay_graphics.sh` | 3 | reframe + composite, audio stream-copied |
| `captions_build.py` | 5 | caption cards from the canonical transcript |
| `captions.sh` | 5 | build + render captions |
| `music_bed.sh` | 6 | flat bed, re-mastered once |
| `hf_pin.sh` | - | the ONLY way the skill pack changes |
| `hf_lock.py` | - | maintain skills-lock.json |
| `vendor_gsap.sh` | - | refresh the vendored GSAP |
| `project_doc.sh` / `.py` | - | regenerate PROJECT.md |
| `rename-job.sh` | - | give a job a better title |
| `name_job.py` | - | propose a title from the content |
| `parts_ids.py` | - | list part ids / missing renders |
| `verify_pipeline.sh` | - | **end-to-end self test on synthetic footage** |
| `make_test_clip.py` | - | the synthetic take, with known ground truth |
| `assert_pipeline.py` | - | 24 assertions, one per lock |
| `vslib.py` | - | shared Python: frame grid, envelopes, corrections, IO |

## Python

Every Python step carries PEP 723 inline dependency metadata and runs through
`uv run`, so nothing is ever installed into the system interpreter. `vslib.py` is
imported, not run - the importers put its directory on `sys.path` explicitly.

On Linux, PIL comes from apt (`python3-pil`), never bare pip. `check-setup.sh`
says so with the right command for the machine it is on.

## Testing a change

```bash
workflows/scripts/verify_pipeline.sh          # ~90 s, no model download
workflows/scripts/verify_pipeline.sh --keep   # leave the job behind to inspect
```

It synthesises a take with known word onsets, deliberately reports those onsets
50-100 ms late the way real forced alignment does, and then asserts that the
system measured its way back to the truth. Run it after touching anything in
`plan_cut.py`, `build_filtergraph.py`, `render_cut.sh` or `vslib.py`.
