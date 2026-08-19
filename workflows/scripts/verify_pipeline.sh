#!/usr/bin/env bash
# verify_pipeline.sh - end-to-end self test on synthetic footage.
#
#   verify_pipeline.sh [--keep]
#
# Builds a take with known ground truth (word onsets, deliberate filler, two
# stretches of dead air, continuous room tone), runs the whole rough-cut path
# on it, and asserts every lock actually holds:
#
#   * boundaries measured off the envelope, not taken from the transcript
#   * every boundary on the frame grid, A/V lengths agreeing
#   * filler and dead air gone
#   * joints crossfaded through room tone, no clicks, no holes
#   * audio mastered exactly once, AAC >= 256k
#   * the canonical transcript derived, never re-transcribed
#
# Needs no model download - the transcript is a fixture, so this runs anywhere
# ffmpeg and uv do.

set -eu
. "$(cd "$(dirname "$0")/../lib" && pwd -P)/common.sh"
vs_require ffmpeg ffprobe uv

KEEP=0
[ "${1:-}" = "--keep" ] && KEEP=1

JOB="pipeline-self-test"
DIR="$VS_ROOT/projects/$JOB"
BUILD="$VS_ROOT/projects/.selftest"        # never /tmp - macOS clears it
rm -rf "$DIR" "$BUILD"
mkdir -p "$BUILD"

vs_step "self test: building a synthetic take"
DUR=$(vs_py "$VS_SCRIPTS/make_test_clip.py" \
        --out-wav "$BUILD/take.wav" --out-words "$BUILD/words.json")
vs_ok "${DUR}s of synthetic speech, room tone throughout"

ffmpeg -hide_banner -loglevel error -y \
  -f lavfi -i "testsrc2=size=540x960:rate=30" \
  -i "$BUILD/take.wav" \
  -t "$DUR" -c:v libx264 -preset ultrafast -crf 28 -pix_fmt yuv420p \
  -c:a pcm_s16le "$BUILD/self-test-take.mov"
vs_ok "self-test-take.mov  540x960 @ 30 fps"

vs_step "intake"
"$VS_SCRIPTS/new-job.sh" "Pipeline Self Test" --format short >/dev/null
"$VS_SCRIPTS/intake.sh" "$JOB" "$BUILD/self-test-take.mov"

# Stand in for step 2a. Real jobs run whisperx here exactly once.
uv run --quiet - "$BUILD/words.json" "$DIR" <<'PYEOF'
import json, sys, os
src, job_dir = sys.argv[1], sys.argv[2]
doc = json.load(open(src))
job = json.load(open(os.path.join(job_dir, "job.json")))
doc["source"] = {"file": job["raw"]["file"], "sha256": job["raw"]["sha256"],
                 "duration": job["raw"]["duration"]}
out = os.path.join(job_dir, "transcript", "words.json")
json.dump(doc, open(out, "w"), indent=2); open(out, "a").write("\n")
PYEOF
vs_ok "transcript/words.json installed as a fixture (starts 50-100 ms late, on purpose)"

vs_py "$VS_SCRIPTS/plan_cut.py" --job-dir "$DIR" --root "$VS_ROOT"
"$VS_SCRIPTS/render_cut.sh" "$JOB"
vs_py "$VS_SCRIPTS/make_transcript.py" --job-dir "$DIR" --root "$VS_ROOT"
vs_py "$VS_SCRIPTS/edl_export.py" --job-dir "$DIR"

vs_step "assertions"
vs_py "$VS_SCRIPTS/assert_pipeline.py" --job-dir "$DIR" --truth "$BUILD/words.json"
RC=$?

"$VS_SCRIPTS/project_doc.sh" "$JOB" >/dev/null

if [ "$KEEP" = 1 ]; then
  vs_info ""
  vs_dim "kept: projects/$JOB  (build: projects/.selftest)"
else
  rm -rf "$DIR" "$BUILD"
  vs_dim "cleaned up; pass --keep to inspect the job"
fi
exit $RC
