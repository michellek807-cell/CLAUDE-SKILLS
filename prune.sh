#!/usr/bin/env bash
# prune.sh - reclaim regenerable bytes. Nothing else.
#
#   ./prune.sh <job>            prune one job
#   ./prune.sh --all            prune every job that has a final
#   ./prune.sh <job> --dry-run  say what it would delete
#   ./prune.sh <job> --deep     also drop the graphics part renders
#
# What it will delete: frame caches, filtergraph scratch, the pre-master PCM
# splice, part renders (--deep only). All of it rebuilds from cutlist.json,
# timeline.json and the raw file.
#
# What it will NEVER touch, at any flag:
#     raw/        the footage. Deleting it is unrecoverable.
#     outputs/    the deliverables and the canonical transcript.
#     transcript/ words.json is one WhisperX pass you are not paying for twice.
#     audio/ assets/ broll/   things you sourced by hand.
#     cut/*.json  cutlist.json IS the edit.
#
# The list of protected directories is hard-coded below, not configurable.

set -eu
ROOT=$(cd "$(dirname "$0")" && pwd -P)
. "$ROOT/workflows/lib/common.sh"

PROTECTED="raw outputs transcript audio assets broll"

DRY=0; DEEP=0; ALL=0; JOB=""
while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run|-n) DRY=1; shift ;;
    --deep)       DEEP=1; shift ;;
    --all)        ALL=1; shift ;;
    --help|-h)    sed -n '2,25p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    --*)          vs_die "unknown flag: $1" ;;
    *)            JOB="$1"; shift ;;
  esac
done

human() {  # bytes -> something readable, portable across bash 3.2
  uv run --quiet - "$1" <<'PYEOF'
import sys
n = float(sys.argv[1])
for u in ("B", "KB", "MB", "GB"):
    if n < 1024 or u == "GB":
        print("%.1f %s" % (n, u)); break
    n /= 1024
PYEOF
}

# Size of a file OR a directory, in bytes. `du -sk` handles both; the earlier
# -d guard here silently reported 0 for every file it was about to delete.
path_bytes() {
  [ -e "$1" ] || { printf '0\n'; return; }
  du -sk "$1" 2>/dev/null | awk '{print $1 * 1024}' | head -1
}

prune_one() {
  _job="$1"
  _dir="$VS_ROOT/projects/$_job"
  [ -f "$_dir/job.json" ] || { vs_warn "$_job: no job.json, skipping"; return; }

  # A hard guard, not a comment. If any protected directory is missing, the job
  # folder is not what we think it is and we stop.
  for p in $PROTECTED; do
    [ -d "$_dir/$p" ] || { vs_warn "$_job: no $p/ - refusing to prune an unfamiliar folder"; return; }
  done

  _freed=0
  _targets="$_dir/cache"
  _targets="$_targets $_dir/cut/$_job.spliced.mkv"
  if [ "$DEEP" = 1 ]; then
    _targets="$_targets $_dir/hf-graphics/renders $_dir/hf-graphics/captions/renders"
  fi

  vs_step "$_job"
  _stage=$(vs_json "$_dir/job.json" stage "?")
  if [ "$_stage" != "final" ] && [ "$ALL" = 1 ]; then
    vs_dim "stage is '$_stage', not final - skipping (prune it by name to force)"
    return
  fi

  for t in $_targets; do
    [ -e "$t" ] || continue
    # Belt and braces: never delete inside a protected directory, whatever the
    # path arithmetic above produced.
    _rel="${t#$_dir/}"
    _top="${_rel%%/*}"
    case " $PROTECTED " in
      *" $_top "*) vs_warn "refusing to touch $_rel"; continue ;;
    esac
    _b=$(path_bytes "$t")
    _freed=$((_freed + _b))
    if [ "$DRY" = 1 ]; then
      vs_dim "would remove  $_rel  ($(human "$_b"))"
    else
      rm -rf "$t"
      vs_ok "removed $_rel  ($(human "$_b"))"
    fi
  done

  if [ "$_freed" = 0 ]; then
    vs_dim "nothing regenerable left"
  else
    vs_ok "$( [ "$DRY" = 1 ] && printf 'would reclaim' || printf 'reclaimed') $(human "$_freed")"
  fi
  [ "$DRY" = 1 ] || "$VS_SCRIPTS/project_doc.sh" "$_job" >/dev/null
}

if [ "$ALL" = 1 ]; then
  for d in "$VS_ROOT"/projects/*/; do
    [ -f "$d/job.json" ] || continue
    prune_one "$(basename "$d")"
  done
else
  [ -n "$JOB" ] || vs_die "usage: ./prune.sh <job> [--dry-run] [--deep]   or  ./prune.sh --all"
  vs_require_job "$JOB" >/dev/null
  prune_one "$JOB"
fi

printf '\n'
vs_dim "raw/, outputs/, transcript/, audio/, assets/ and broll/ were not touched"
