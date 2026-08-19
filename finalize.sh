#!/usr/bin/env bash
# finalize.sh - pipeline step 7. Promote the newest render and hand it over.
#
#   ./finalize.sh <job>              promote the newest render
#   ./finalize.sh <job> <file>       promote a specific file
#   ./finalize.sh <job> --no-copy    skip the ~/Downloads copy
#   ./finalize.sh --list             show every job and its final
#
# Picks the most recently written deliverable in the job (graded > mastered >
# whatever you name), copies it to outputs/<job>.final.mp4, and drops a copy in
# ~/Downloads so it is where you actually look for it.
#
# Promotion is a COPY, never a re-encode. The audio was mastered exactly once
# and re-encoding here would silently take a second generation off it. If the
# file needs a container change, finalize refuses and says so.

set -eu
ROOT=$(cd "$(dirname "$0")" && pwd -P)
. "$ROOT/workflows/lib/common.sh"
vs_require ffprobe

if [ "${1:-}" = "--list" ]; then
  printf '\n%-40s %-10s %s\n' "job" "stage" "final"
  for d in "$VS_ROOT"/projects/*/; do
    [ -f "$d/job.json" ] || continue
    j=$(basename "$d")
    st=$(vs_json "$d/job.json" stage "?")
    fin="-"
    [ -f "$d/outputs/$j.final.mp4" ] && fin="outputs/$j.final.mp4  ($(vs_duration "$d/outputs/$j.final.mp4")s)"
    printf '%-40s %-10s %s\n' "$j" "$st" "$fin"
  done
  printf '\n'
  exit 0
fi

JOB="${1:-}"; shift 2>/dev/null || true
DIR=$(vs_require_job "$JOB")
PICK=""; COPY=1
while [ $# -gt 0 ]; do
  case "$1" in
    --no-copy) COPY=0; shift ;;
    --*) vs_die "unknown flag: $1" ;;
    *) PICK="$1"; shift ;;
  esac
done

# ------------------------------------------------------- pick the render -----
if [ -z "$PICK" ]; then
  # Newest first, in preference order. `ls -t` is portable; find -printf is not.
  for cand in "$DIR/cut/$JOB.graded.mp4" "$DIR/cut/$JOB.mastered.mp4"; do
    [ -f "$cand" ] || continue
    if [ -z "$PICK" ] || [ "$cand" -nt "$PICK" ]; then PICK="$cand"; fi
  done
  for cand in "$DIR"/outputs/*.mp4; do
    case "$cand" in *"$JOB.final.mp4") continue ;; esac
    [ -f "$cand" ] || continue
    if [ -z "$PICK" ] || [ "$cand" -nt "$PICK" ]; then PICK="$cand"; fi
  done
fi
[ -n "$PICK" ] && [ -f "$PICK" ] || vs_die "nothing to promote in projects/$JOB (looked in cut/ and outputs/)"

# --------------------------------------------------------------- verify ------
ACODEC=$(vs_probe "$PICK" a:codec_name)
ABR=$(vs_probe "$PICK" a:bit_rate)
case "$PICK" in
  *.mp4|*.MP4) ;;
  *) vs_die "$(basename "$PICK") is not an mp4. Re-encoding here would cost a second
       audio generation - render it as mp4 upstream instead." ;;
esac
if [ -n "$ABR" ] && [ "$ABR" != "N/A" ]; then
  KBPS=$((ABR / 1000))
  if [ "$KBPS" -lt 250 ]; then
    vs_warn "audio is $ACODEC @ ${KBPS}k - the lock is 256k or better. Promoting anyway,"
    vs_warn "but find out which stage re-encoded it."
  fi
fi

FINAL="$DIR/outputs/$JOB.final.mp4"
vs_step "finalize: $(basename "$PICK")"
cp "$PICK" "$FINAL"
vs_ok "outputs/$JOB.final.mp4  $(vs_duration "$FINAL")s  $(vs_probe "$FINAL" v:width)x$(vs_probe "$FINAL" v:height)  $ACODEC"

# --------------------------------------------------------- ~/Downloads -------
if [ "$COPY" = 1 ]; then
  DL="${VS_DOWNLOADS:-$HOME/Downloads}"
  if [ -d "$DL" ]; then
    cp "$FINAL" "$DL/$JOB.mp4"
    vs_ok "$DL/$JOB.mp4"
  else
    vs_warn "no $DL - skipped the handover copy (set VS_DOWNLOADS to point elsewhere)"
  fi
fi

uv run --quiet - "$DIR/job.json" "$JOB" "$(basename "$PICK")" <<'PYEOF'
import json, sys, datetime
p = sys.argv[1]; d = json.load(open(p))
d["stage"] = "final"
d.setdefault("outputs", {})["final"] = "outputs/%s.final.mp4" % sys.argv[2]
d["final"] = {"promoted_from": sys.argv[3],
              "at": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")}
json.dump(d, open(p, "w"), indent=2); open(p, "a").write("\n")
PYEOF

"$VS_SCRIPTS/project_doc.sh" "$JOB" >/dev/null
vs_dim "reclaim the cache when you are done: ./prune.sh $JOB"
