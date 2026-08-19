#!/usr/bin/env bash
# hf_render.sh - render graphics parts through the PINNED HyperFrames CLI.
#
#   hf_render.sh <job>              every part
#   hf_render.sh <job> part-03      one part - the whole reason parts exist
#   hf_render.sh <job> --check      lint only, render nothing
#
# The version is pinned in workflows/lib/common.sh and passed on every single
# invocation. `npx hyperframes` without a version floats to latest, and past
# releases have broken the composition contract mid-job:
#   0.7.42  started requiring data-start / data-composition-id / data-width /
#           data-height on the root comp, or the render capture dies
#   0.7.67  shipped a change that was reverted in 0.7.68
# Move the pin with hf_pin.sh bump, one part re-rendered and reviewed.
#
# Frames cache goes in the job folder, never /tmp - macOS clears /tmp and a
# half-cleared cache mid-render is a confusing failure.

set -eu
. "$(cd "$(dirname "$0")/../lib" && pwd -P)/common.sh"
vs_require npx

JOB="${1:-}"; WHICH="${2:-}"
DIR=$(vs_require_job "$JOB")
GDIR="$DIR/hf-graphics"
MANIFEST="$GDIR/parts.json"
[ -f "$MANIFEST" ] || vs_die "no hf-graphics/parts.json - run hf_build.sh $JOB first"

CACHE="$DIR/cache/hf-frames"
RENDERS="$GDIR/renders"
mkdir -p "$CACHE" "$RENDERS"
CACHE=$(cd "$CACHE" && pwd -P)
RENDERS=$(cd "$RENDERS" && pwd -P)

FPS=$(vs_json "$MANIFEST" fps 30)
QUALITY="${VS_HF_QUALITY:-high}"

CHECK_ONLY=0
[ "$WHICH" = "--check" ] && { CHECK_ONLY=1; WHICH=""; }

PARTS=$(vs_py "$VS_SCRIPTS/parts_ids.py" --job-dir "$DIR" --kind graphics)
[ -n "$PARTS" ] || vs_die "parts.json lists no parts"

if [ -n "$WHICH" ]; then
  printf '%s\n' "$PARTS" | grep -qx "$WHICH" || vs_die "no such part: $WHICH (have: $(echo $PARTS))"
  PARTS="$WHICH"
fi

vs_step "hyperframes $VS_HF_VERSION  quality=$QUALITY  fps=$FPS"

# Short-form: hand the checker the same keep-out band the preset lays out to,
# so HyperFrames enforces it independently of our own assertion.
ZONE=""
FMT=$(vs_json "$DIR/job.json" format short)
if [ "$FMT" = short ]; then
  H=$(vs_json "$MANIFEST" canvas.h 1920)
  BOT=$(vs_json "$MANIFEST" canvas.safe_bottom 300)
  Y0=$(uv run --quiet - "$H" "$BOT" <<'PYEOF'
import sys
print("%.4f" % (1.0 - float(sys.argv[2]) / float(sys.argv[1])))
PYEOF
)
  ZONE="--caption-zone x0=0;y0=$Y0;x1=1;y1=1;severity=error"
fi

for P in $PARTS; do
  PDIR="$GDIR/parts/$P"
  [ -f "$PDIR/index.html" ] || vs_die "missing parts/$P/index.html - rebuild with hf_build.sh $JOB"

  vs_dim "$P: check"
  # Each part is its own project root, so check and render resolve identical
  # URLs and root-relative asset paths stay valid in both.
  # shellcheck disable=SC2086
  ( cd "$PDIR" && vs_hf check . $ZONE ) || \
    vs_warn "$P has lint findings above - fix the preset or the beat, never the generated html"

  [ "$CHECK_ONLY" = 1 ] && continue

  vs_step "render $P"
  # MOV keeps the alpha channel, so graphics composite over the cut instead of
  # replacing it.
  ( cd "$PDIR" && vs_hf render . \
      --output "$RENDERS/$P.mov" \
      --format mov \
      --fps "$FPS" \
      --quality "$QUALITY" \
      --frames-cache-dir "$CACHE" \
      --quiet ) || vs_die "$P failed to render"
  vs_ok "hf-graphics/renders/$P.mov"
done

[ "$CHECK_ONLY" = 1 ] && { vs_ok "check complete, nothing rendered"; exit 0; }

vs_dim "join them: workflows/scripts/hf_concat_parts.sh $JOB"
