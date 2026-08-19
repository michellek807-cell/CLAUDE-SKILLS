#!/usr/bin/env bash
# hf_build.sh - pipeline step 3. Plan the graphics, then build the parts.
#
#   hf_build.sh <job> [--replan] [--preset <name>]
#
# Plan first (beat sheet you can argue with in 30 seconds), build second (HTML
# that takes minutes to render). The plan lives in hf-graphics/PLAN.md and
# hf-graphics/timeline.json; your edits to timeline.json survive a rebuild
# unless you pass --replan.

set -eu
. "$(cd "$(dirname "$0")/../lib" && pwd -P)/common.sh"

JOB="${1:-}"; shift 2>/dev/null || true
DIR=$(vs_require_job "$JOB")
PLAN_FLAGS=""
while [ $# -gt 0 ]; do
  case "$1" in
    --replan) PLAN_FLAGS="$PLAN_FLAGS --force"; shift ;;
    --preset) PLAN_FLAGS="$PLAN_FLAGS --preset $2"; shift 2 ;;
    *) vs_die "unknown flag: $1" ;;
  esac
done

# shellcheck disable=SC2086
vs_py "$VS_SCRIPTS/graphics_plan.py" --job-dir "$DIR" $PLAN_FLAGS
vs_py "$VS_SCRIPTS/hf_build_parts.py" --job-dir "$DIR" --root "$VS_ROOT"
"$VS_SCRIPTS/project_doc.sh" "$JOB" >/dev/null
