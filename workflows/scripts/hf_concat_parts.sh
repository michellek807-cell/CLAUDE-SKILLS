#!/usr/bin/env bash
# hf_concat_parts.sh - join the rendered graphics parts into one alpha track.
#
#   hf_concat_parts.sh <job> [--captions]
#
# Stream copy only. The parts came off one shared timeline at identical codec
# settings, so joining them is a container operation, not a re-encode - which is
# exactly why re-rendering part 3 does not cost you the other parts' quality.

set -eu
. "$(cd "$(dirname "$0")/../lib" && pwd -P)/common.sh"
vs_require ffmpeg

JOB="${1:-}"
DIR=$(vs_require_job "$JOB")
KIND="graphics"
[ "${2:-}" = "--captions" ] && KIND="captions"

if [ "$KIND" = captions ]; then
  SRC="$DIR/hf-graphics/captions/renders"; OUT="$DIR/hf-graphics/captions.mov"
else
  SRC="$DIR/hf-graphics/renders";          OUT="$DIR/hf-graphics/graphics.mov"
fi
[ -d "$SRC" ] || vs_die "no renders in $SRC - run hf_render.sh $JOB first"

LIST="$DIR/cache/$KIND-parts.txt"
: > "$LIST"
N=0
for f in "$SRC"/part-*.mov; do
  [ -e "$f" ] || continue
  printf "file '%s'\n" "$f" >> "$LIST"
  N=$((N+1))
done
[ "$N" -gt 0 ] || vs_die "no part-*.mov in $SRC"

MISSING=$(vs_py "$VS_SCRIPTS/parts_ids.py" --job-dir "$DIR" --kind "$KIND" --missing | tr "\n" " ")
[ -z "$MISSING" ] || vs_die "not every part is rendered: $MISSING"

vs_step "joining $N $KIND part(s), stream copy"
ffmpeg -hide_banner -loglevel error -nostdin -y \
  -f concat -safe 0 -i "$LIST" -c copy "$OUT" || vs_die "concat failed"
vs_ok "$(basename "$OUT")  $(vs_duration "$OUT")s"
