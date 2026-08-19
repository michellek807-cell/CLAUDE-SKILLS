#!/usr/bin/env bash
# intake.sh - pipeline step 1. COPY the raw file into the job.
#
#   intake.sh <job> <path/to/footage.mov>
#
# LOCK: copy, never move. The card or the Downloads folder stays the way the
# camera left it. Everything after this point reads projects/<job>/raw/ and
# treats it as immutable.

set -eu
. "$(cd "$(dirname "$0")/../lib" && pwd -P)/common.sh"
vs_require ffprobe

JOB="${1:-}"; SRC="${2:-}"
DIR=$(vs_require_job "$JOB")
[ -n "$SRC" ] || vs_die "usage: intake.sh <job> <file>"
[ -f "$SRC" ] || vs_die "no such file: $SRC"

SRC=$(vs_abspath "$SRC")
BASE=$(basename "$SRC")
DEST="$DIR/raw/$BASE"

vs_step "intake: $BASE"

if [ -f "$DEST" ]; then
  if [ "$(vs_sha256 "$SRC")" = "$(vs_sha256 "$DEST")" ]; then
    vs_ok "already in raw/, identical bytes - not re-copying"
  else
    vs_die "raw/$BASE exists with different bytes. raw/ is immutable; rename the incoming file."
  fi
else
  cp "$SRC" "$DEST"          # copy, never move
  vs_ok "copied -> raw/$BASE  ($(vs_sha256 "$DEST" | cut -c1-12))"
fi

# Everything downstream reads this instead of re-probing.
vs_py "$VS_SCRIPTS/intake_probe.py" --job-dir "$DIR" --raw "$DEST" --source "$SRC"
"$VS_SCRIPTS/project_doc.sh" "$JOB" >/dev/null
