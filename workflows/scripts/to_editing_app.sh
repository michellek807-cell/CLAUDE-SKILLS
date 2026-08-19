#!/usr/bin/env bash
# to_editing_app.sh - pipeline step 2, default finish. Drive the editing app.
#
#   to_editing_app.sh <job> [premiere|capcut|resolve|none]
#
# Replays the cut list against the ORIGINAL raw file so every cut lands on the
# timeline as a trimmable edit point. No flat render: a flattened mp4 is one
# clip with every boundary already burned in, and the first note you get back
# ("hold that beat two frames longer") sends you back to the script.
#
# Time to timeline is the metric. Transcription is the only slow step allowed.

set -eu
. "$(cd "$(dirname "$0")/../lib" && pwd -P)/common.sh"

JOB="${1:-}"
DIR=$(vs_require_job "$JOB")
APP="${2:-${VS_EDIT_APP:-auto}}"

[ -f "$DIR/cut/cutlist.json" ] || vs_die "no cut/cutlist.json - run rough_cut.sh first"

vs_py "$VS_SCRIPTS/edl_export.py" --job-dir "$DIR"

XML="$DIR/cut/$JOB.fcp7.xml"
DRAFT="$DIR/cut/$JOB.capcut"

# --------------------------------------------------------- open the app ------
# The one thing that differs by machine is whether an app can be launched at
# all. On macOS `open` does it; everywhere else we print the path, because a
# WSL2 shell cannot launch a Windows app reliably and guessing is worse than
# saying where the file is.
if [ "$APP" = auto ]; then
  if [ "$(vs_os)" = macos ] && [ -d /Applications/CapCut.app ] && ! ls -d /Applications/Adobe\ Premiere\ Pro* >/dev/null 2>&1; then
    APP=capcut
  elif [ "$(vs_os)" = macos ]; then
    APP=premiere
  else
    APP=none
  fi
fi

case "$APP" in
  premiere|resolve|fcp)
    if [ "$(vs_os)" = macos ]; then
      vs_step "opening $XML"
      open "$XML" 2>/dev/null || vs_warn "could not open it; import cut/$JOB.fcp7.xml by hand"
    else
      vs_step "import this into your editor"
      vs_info "  $XML"
    fi
    vs_dim "Premiere: File > Import, pick the .xml. It builds the sequence and relinks to raw/."
    ;;
  capcut)
    DEST=""
    if [ "$(vs_os)" = macos ]; then
      DEST="$HOME/Movies/CapCut/User Data/Projects/com.lveditor.draft"
    fi
    if [ -n "$DEST" ] && [ -d "$DEST" ]; then
      rm -rf "$DEST/$JOB"
      cp -R "$DRAFT" "$DEST/$JOB"
      vs_ok "draft installed: $DEST/$JOB"
      vs_dim "restart CapCut if it is already open, then pick '$JOB' from Drafts"
    else
      vs_step "CapCut draft ready"
      vs_info "  $DRAFT"
      vs_dim "copy it into CapCut's draft folder, or use cut/$JOB.cuts.md to razor by hand"
    fi
    ;;
  none)
    vs_step "interchange written - nothing launched"
    vs_info "  $XML"
    vs_info "  $DIR/cut/$JOB.edl"
    vs_info "  $DRAFT"
    vs_dim "on WSL2 these paths are reachable from Windows under \\\\wsl\$"
    ;;
  *) vs_die "unknown app: $APP (premiere|capcut|resolve|none)" ;;
esac

uv run --quiet - "$DIR/job.json" "$JOB" <<'PYEOF'
import json, sys
p, name = sys.argv[1], sys.argv[2]
d = json.load(open(p))
d.setdefault("handoff", {})
d["handoff"] = {"fcp7": "cut/%s.fcp7.xml" % name, "edl": "cut/%s.edl" % name,
                "capcut": "cut/%s.capcut" % name, "cuts": "cut/%s.cuts.md" % name}
json.dump(d, open(p, "w"), indent=2); open(p, "a").write("\n")
PYEOF
