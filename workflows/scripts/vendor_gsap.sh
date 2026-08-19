#!/usr/bin/env bash
# vendor_gsap.sh - refresh workflows/vendor/gsap.min.js from npm.
#
#   vendor_gsap.sh [version]      default 3.14.2
#
# Compositions load GSAP from disk, not from a CDN. A composition that reaches
# out over the network at render time renders silently wrong the day the network
# says no: the capture still succeeds, every tween is simply missing, and the
# only trace is a sub_timeline_script_failure warning in the log. Vendoring it
# turns that into a build-time error instead.

set -eu
. "$(cd "$(dirname "$0")/../lib" && pwd -P)/common.sh"
vs_require npm

VERSION="${1:-3.14.2}"
DEST="$VS_ROOT/workflows/vendor"
WORK="$VS_ROOT/workflows/vendor/.unpack"     # never /tmp
mkdir -p "$DEST" "$WORK"

vs_step "vendoring gsap@$VERSION"
( cd "$WORK" && npm pack "gsap@$VERSION" >/dev/null 2>&1 ) || vs_die "npm pack gsap@$VERSION failed"
TGZ=$(ls "$WORK"/gsap-*.tgz | head -1)
[ -n "$TGZ" ] || vs_die "npm pack produced no tarball"
tar xzf "$TGZ" -C "$WORK"
[ -f "$WORK/package/dist/gsap.min.js" ] || vs_die "gsap.min.js not in the tarball"
cp "$WORK/package/dist/gsap.min.js" "$DEST/gsap.min.js"
printf '%s\n' "$VERSION" > "$DEST/gsap.version"
rm -rf "$WORK"

vs_ok "workflows/vendor/gsap.min.js  $(vs_sha256 "$DEST/gsap.min.js" | cut -c1-12)  v$VERSION"
vs_dim "rebuild the parts to pick it up: workflows/scripts/hf_build.sh <job>"
