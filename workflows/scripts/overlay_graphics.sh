#!/usr/bin/env bash
# overlay_graphics.sh - composite the graphics (and captions) over the cut.
#
#   overlay_graphics.sh <job>
#
# Reframes the cut to the delivery canvas, then overlays the alpha tracks.
# Audio is STREAM COPIED: it was mastered exactly once at AAC 256k and nothing
# downstream is allowed to touch it again.

set -eu
. "$(cd "$(dirname "$0")/../lib" && pwd -P)/common.sh"
vs_require ffmpeg ffprobe

JOB="${1:-}"
DIR=$(vs_require_job "$JOB")
BASE="$DIR/cut/$JOB.mastered.mp4"
[ -f "$BASE" ] || vs_die "no cut/$JOB.mastered.mp4 - run render_cut.sh $JOB (the flat path)"

MANIFEST="$DIR/hf-graphics/parts.json"
[ -f "$MANIFEST" ] || vs_die "no hf-graphics/parts.json - run hf_build.sh $JOB"
W=$(vs_json "$MANIFEST" canvas.w)
H=$(vs_json "$MANIFEST" canvas.h)
FPS=$(vs_json "$MANIFEST" fps 30)

GFX="$DIR/hf-graphics/graphics.mov"
CAPS="$DIR/hf-graphics/captions.mov"
OUT="$DIR/cut/$JOB.graded.mp4"

# Reframe: cover the delivery canvas, then crop. Nudge the crop with
# VS_CROP_X / VS_CROP_Y when the subject is not centred.
CX="${VS_CROP_X:-(iw-ow)/2}"
CY="${VS_CROP_Y:-(ih-oh)/2}"
REFRAME="scale=$W:$H:force_original_aspect_ratio=increase,crop=$W:$H:$CX:$CY,setsar=1"

INPUTS="-i $BASE"
CHAIN="[0:v]$REFRAME[base]"
LAST="base"
IDX=1
for LAYER in "$GFX" "$CAPS"; do
  [ -f "$LAYER" ] || continue
  INPUTS="$INPUTS -i $LAYER"
  CHAIN="$CHAIN;[$IDX:v]scale=$W:$H[l$IDX];[$LAST][l$IDX]overlay=0:0:format=auto:eof_action=pass[ov$IDX]"
  LAST="ov$IDX"
  IDX=$((IDX+1))
done
[ "$IDX" = 1 ] && vs_die "nothing to overlay - render graphics first (hf_render.sh $JOB)"

vs_step "compositing $((IDX-1)) layer(s) onto a ${W}x${H} frame"
ENC_ARGS=$(vs_video_encoder_args)
# shellcheck disable=SC2086
ffmpeg -hide_banner -loglevel error -stats -nostdin -y \
  $INPUTS \
  -filter_complex "$CHAIN" \
  -map "[$LAST]" -map 0:a:0 \
  $ENC_ARGS -fps_mode cfr -r "$FPS" \
  -c:a copy -movflags +faststart \
  "$OUT" || vs_die "overlay failed"

vs_ok "cut/$JOB.graded.mp4  ${W}x${H}  $(vs_duration "$OUT")s  (audio stream-copied)"
vs_dim "promote it: ./finalize.sh $JOB"
