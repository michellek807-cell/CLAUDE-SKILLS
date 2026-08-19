#!/usr/bin/env bash
# captions.sh - pipeline step 5. Build (and optionally render) the captions.
#
#   captions.sh <job>              build the caption compositions + srt
#   captions.sh <job> --render     build, then render every caption part
#   captions.sh <job> --render part-02   re-render one part
#
# Short-form only, and always from the canonical transcript. Nothing here
# transcribes anything.

set -eu
. "$(cd "$(dirname "$0")/../lib" && pwd -P)/common.sh"

JOB="${1:-}"; shift 2>/dev/null || true
DIR=$(vs_require_job "$JOB")
RENDER=0; WHICH=""
while [ $# -gt 0 ]; do
  case "$1" in
    --render) RENDER=1; shift ;;
    part-*)   WHICH="$1"; shift ;;
    *) vs_die "unknown argument: $1" ;;
  esac
done

vs_py "$VS_SCRIPTS/captions_build.py" --job-dir "$DIR" --root "$VS_ROOT"

[ "$RENDER" = 1 ] || { "$VS_SCRIPTS/project_doc.sh" "$JOB" >/dev/null; exit 0; }

CDIR="$DIR/hf-graphics/captions"
[ -f "$CDIR/parts.json" ] || exit 0
CACHE="$DIR/cache/hf-frames"
mkdir -p "$CACHE" "$CDIR/renders"
FPS=$(vs_json "$CDIR/parts.json" fps 30)

PARTS=$(vs_py "$VS_SCRIPTS/parts_ids.py" --job-dir "$DIR" --kind captions)
[ -n "$WHICH" ] && PARTS="$WHICH"

vs_step "hyperframes $VS_HF_VERSION rendering captions"
RENDERS=$(cd "$CDIR/renders" && pwd -P)
CACHE=$(cd "$CACHE" && pwd -P)
for P in $PARTS; do
  PDIR="$CDIR/parts/$P"
  ( cd "$PDIR" && vs_hf check . ) || \
    vs_warn "$P has lint findings - fix the preset, never the generated html"
  ( cd "$PDIR" && vs_hf render . \
      --output "$RENDERS/$P.mov" --format mov \
      --fps "$FPS" --quality "${VS_HF_QUALITY:-high}" \
      --frames-cache-dir "$CACHE" --quiet ) || vs_die "captions $P failed to render"
  vs_ok "hf-graphics/captions/renders/$P.mov"
done

"$VS_SCRIPTS/hf_concat_parts.sh" "$JOB" --captions
"$VS_SCRIPTS/project_doc.sh" "$JOB" >/dev/null
