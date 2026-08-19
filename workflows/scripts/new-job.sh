#!/usr/bin/env bash
# new-job.sh - create a job folder.
#
#   new-job.sh "Why Your Rough Cut Sounds Cheap" [--format short|long]
#
# The job name is a kebab-case title about the CONTENT. Never the camera
# filename: C0042.MP4 tells you nothing six months later.

set -eu
. "$(cd "$(dirname "$0")/../lib" && pwd -P)/common.sh"

TITLE=""; FORMAT="short"
while [ $# -gt 0 ]; do
  case "$1" in
    --format) FORMAT="${2:-}"; shift 2 ;;
    --*) vs_die "unknown flag: $1" ;;
    *) TITLE="${TITLE:+$TITLE }$1"; shift ;;
  esac
done
[ -n "$TITLE" ] || vs_die 'usage: new-job.sh "A Title About The Content" [--format short|long]'
case "$FORMAT" in short|long) ;; *) vs_die "--format must be short or long, got: $FORMAT" ;; esac

JOB=$(vs_slug "$TITLE")
[ -n "$JOB" ] || vs_die "title slugged to nothing: $TITLE"
DIR="$VS_ROOT/projects/$JOB"
[ -d "$DIR" ] && vs_die "job already exists: projects/$JOB"

case "$JOB" in
  c[0-9]*|dji_*|img_*|mvi_*|gx[0-9]*|dsc*|clip[0-9]*|gopro*)
    vs_warn "'$JOB' looks like a camera filename. Job names are titles about the content." ;;
esac

for d in raw audio assets broll outputs hf-graphics transcript cut cache; do
  mkdir -p "$DIR/$d"
done

cat > "$DIR/job.json" <<JSON
{
  "name": "$JOB",
  "title": "$TITLE",
  "format": "$FORMAT",
  "created": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "hyperframes": "$VS_HF_VERSION",
  "raw": null,
  "stage": "created"
}
JSON

"$VS_SCRIPTS/project_doc.sh" "$JOB" >/dev/null

vs_ok "created projects/$JOB  (format: $FORMAT)"
printf '%s\n' "$DIR"
