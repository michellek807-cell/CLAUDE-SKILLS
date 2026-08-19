#!/usr/bin/env bash
# rough_cut.sh - pipeline step 2, end to end. This is the "rough cut this" button.
#
#   rough_cut.sh <path/to/footage.mov> [--title "..."] [--format short|long] [flags]
#   rough_cut.sh <existing-job>                        resume / re-run
#
# Flags
#   --title "..."     content title; the job folder is its kebab-case slug
#   --format short    9:16 short-form (default) | long  16:9
#   --aggressive      also drop like / so / basically / actually / literally
#   --keep-fillers    dead air only, leave every word in
#   --to-app          stop after the cut list and hand off to Premiere/CapCut
#                     (the default finish - no flat render, seconds to timeline)
#   --flat            also render the flat mastered mp4
#   --retranscribe    force a re-transcribe (the one thing you should rarely do)
#
# Order is fixed: intake -> transcribe once -> plan -> (splice + master + QA)
# -> canonical transcript. Every stage is idempotent, so re-running after a
# config tweak only redoes what changed.

set -eu
. "$(cd "$(dirname "$0")/../lib" && pwd -P)/common.sh"

INPUT=""; TITLE=""; FORMAT=""; PLAN_FLAGS=""; FORCE_TX=0; TO_APP=""; FLAT=0
while [ $# -gt 0 ]; do
  case "$1" in
    --title)        TITLE="${2:-}"; shift 2 ;;
    --format)       FORMAT="${2:-}"; shift 2 ;;
    --aggressive)   PLAN_FLAGS="$PLAN_FLAGS --aggressive"; shift ;;
    --keep-fillers) PLAN_FLAGS="$PLAN_FLAGS --keep-fillers"; shift ;;
    --retranscribe) FORCE_TX=1; shift ;;
    --to-app)       TO_APP=1; shift ;;
    --flat)         FLAT=1; shift ;;
    --help|-h)      sed -n '2,22p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    --*)            vs_die "unknown flag: $1" ;;
    *)              INPUT="$1"; shift ;;
  esac
done
[ -n "$INPUT" ] || vs_die 'usage: rough_cut.sh <footage-file|job-name> [--title "..."]'

vs_require ffmpeg ffprobe uv

# ------------------------------------------------------- resolve the job -----
if [ -d "$VS_ROOT/projects/$INPUT" ]; then
  JOB="$INPUT"
  DIR="$VS_ROOT/projects/$JOB"
  vs_step "resuming projects/$JOB"
else
  [ -f "$INPUT" ] || vs_die "not a file and not an existing job: $INPUT"
  if [ -z "$TITLE" ]; then
    # No title yet. Park it under a provisional name, transcribe, and let the
    # content name itself - never the camera filename.
    JOB="untitled-$(date -u +%Y%m%d-%H%M%S)"
    vs_warn "no --title given; parking as '$JOB' and naming it from the transcript"
  else
    JOB=$(vs_slug "$TITLE")
  fi
  if [ -d "$VS_ROOT/projects/$JOB" ]; then
    vs_dim "projects/$JOB already exists - adding to it"
  else
    "$VS_SCRIPTS/new-job.sh" "${TITLE:-$JOB}" --format "${FORMAT:-short}" >/dev/null
  fi
  DIR="$VS_ROOT/projects/$JOB"
  "$VS_SCRIPTS/intake.sh" "$JOB" "$INPUT"
fi

[ -n "$FORMAT" ] && uv run --quiet - "$DIR/job.json" "$FORMAT" <<'PYEOF'
import json, sys
p = sys.argv[1]; d = json.load(open(p)); d["format"] = sys.argv[2]
json.dump(d, open(p, "w"), indent=2); open(p, "a").write("\n")
PYEOF

# --------------------------------------------- 2a transcribe (exactly once) --
TX_FLAGS=""
[ "$FORCE_TX" = 1 ] && TX_FLAGS="--force"
# shellcheck disable=SC2086
vs_py "$VS_SCRIPTS/transcribe.py" --job-dir "$DIR" $TX_FLAGS

# ------------------------------------------- auto-title from the content -----
case "$JOB" in
  untitled-*)
    NEW=$(vs_py "$VS_SCRIPTS/name_job.py" --job-dir "$DIR")
    if [ -n "$NEW" ] && [ "$NEW" != "$JOB" ] && [ ! -d "$VS_ROOT/projects/$NEW" ]; then
      mv "$VS_ROOT/projects/$JOB" "$VS_ROOT/projects/$NEW"
      JOB="$NEW"; DIR="$VS_ROOT/projects/$JOB"
      vs_ok "named from the content: projects/$JOB"
      vs_dim "rename any time: workflows/scripts/rename-job.sh $JOB \"A Better Title\""
    fi ;;
esac

# ------------------------------------------------------------ 2b plan cut ----
# shellcheck disable=SC2086
vs_py "$VS_SCRIPTS/plan_cut.py" --job-dir "$DIR" --root "$VS_ROOT" $PLAN_FLAGS

# ----------------------------------------------- 2c splice + master + QA -----
# The default finish is inside an editing app: the cut list and the transcript
# are what the app needs, and both exist now. Rendering a flat file first throws
# away every edit point. Only render flat when it is actually the deliverable.
if [ "${TO_APP:-0}" = 1 ] || { [ "$FLAT" = 0 ] && [ "${VS_DEFAULT_FINISH:-app}" = "app" ]; }; then
  vs_py "$VS_SCRIPTS/make_transcript.py" --job-dir "$DIR" --root "$VS_ROOT"
  "$VS_SCRIPTS/to_editing_app.sh" "$JOB"
  vs_step "rough cut ready for the timeline"
  vs_dim "flat render if you want one: workflows/scripts/render_cut.sh $JOB"
else
  "$VS_SCRIPTS/render_cut.sh" "$JOB"
  vs_py "$VS_SCRIPTS/make_transcript.py" --job-dir "$DIR" --root "$VS_ROOT"
  "$VS_SCRIPTS/to_editing_app.sh" "$JOB"
fi

"$VS_SCRIPTS/project_doc.sh" "$JOB" >/dev/null

vs_step "done: projects/$JOB"
vs_dim "resume doc: projects/$JOB/PROJECT.md"
