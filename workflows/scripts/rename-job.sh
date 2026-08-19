#!/usr/bin/env bash
# rename-job.sh - give a job the title it deserves.
#
#   rename-job.sh <job> "Why Your Rough Cut Sounds Cheap"
#
# Renames the folder, rewrites job.json, and renames the files inside outputs/
# and cut/ that carry the job name. Safe to run at any stage.

set -eu
. "$(cd "$(dirname "$0")/../lib" && pwd -P)/common.sh"

OLD="${1:-}"; shift 2>/dev/null || true
TITLE="$*"
[ -n "$OLD" ] && [ -n "$TITLE" ] || vs_die 'usage: rename-job.sh <job> "A Title About The Content"'
SRC=$(vs_require_job "$OLD")
NEW=$(vs_slug "$TITLE")
[ -n "$NEW" ] || vs_die "title slugged to nothing"
DST="$VS_ROOT/projects/$NEW"
[ "$OLD" = "$NEW" ] || [ ! -d "$DST" ] || vs_die "projects/$NEW already exists"

if [ "$OLD" != "$NEW" ]; then
  mv "$SRC" "$DST"
else
  DST="$SRC"
fi

for f in "$DST"/outputs/"$OLD".* "$DST"/cut/"$OLD".*; do
  [ -e "$f" ] || continue
  b=$(basename "$f"); d=$(dirname "$f")
  mv "$f" "$d/$NEW${b#$OLD}"
done

uv run --quiet - "$DST/job.json" "$NEW" "$TITLE" <<'PYEOF'
import json, sys
p, name, title = sys.argv[1], sys.argv[2], sys.argv[3]
d = json.load(open(p))
old = d.get("name")
d["name"], d["title"] = name, title
for k, v in list((d.get("outputs") or {}).items()):
    d["outputs"][k] = v.replace(old + ".", name + ".")
for k, v in list((d.get("cut") or {}).items()):
    if isinstance(v, str):
        d["cut"][k] = v.replace(old + ".", name + ".")
json.dump(d, open(p, "w"), indent=2); open(p, "a").write("\n")
PYEOF

"$VS_SCRIPTS/project_doc.sh" "$NEW" >/dev/null
vs_ok "projects/$OLD -> projects/$NEW   \"$TITLE\""
