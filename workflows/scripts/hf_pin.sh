#!/usr/bin/env bash
# hf_pin.sh - the ONLY sanctioned way the HyperFrames skill pack enters or
# changes in this repo. Never hand-edit a file under .claude/skills/.
#
#   hf_pin.sh install          npx hyperframes@<pin> skills + doctor, then sync
#   hf_pin.sh sync             copy installed skills in, rewrite skills-lock.json
#   hf_pin.sh verify           re-hash every SKILL.md against skills-lock.json
#   hf_pin.sh version          print the current pin
#   hf_pin.sh bump <version>   move the pin deliberately (prints the checklist)
#
# Why the pin exists: `npx hyperframes` floats to latest, and past releases have
# broken the composition contract mid-job. 0.7.42 started requiring data-start,
# data-composition-id, data-width and data-height on the root comp or the render
# capture dies. 0.7.67 shipped a change that was reverted in 0.7.68. We start at
# 0.7.68 and move one part at a time, re-rendered and reviewed.

set -eu

. "$(cd "$(dirname "$0")/../lib" && pwd -P)/common.sh"

LOCK="$VS_ROOT/skills-lock.json"
ROSTER="$VS_ROOT/workflows/hyperframes-skills.txt"
DEST="$VS_ROOT/.claude/skills"
SOURCE_REPO="https://github.com/heygen-com/hyperframes.git"

# Where `npx hyperframes skills` drops the pack. Checked in this order.
hf_src_root() {
  for d in "$HOME/.claude/skills" "$HOME/.agents/skills"; do
    [ -d "$d" ] && { printf '%s\n' "$d"; return 0; }
  done
  return 1
}

strip_ansi() { sed -e 's/\x1b\[[0-9;?]*[a-zA-Z]//g'; }

# ------------------------------------------------------------------ install --
cmd_install() {
  vs_require npx
  vs_step "installing HyperFrames skill pack, pinned to $VS_HF_VERSION"
  _log="$VS_ROOT/.hf-skills-install.log"
  npx --yes "hyperframes@${VS_HF_VERSION}" skills 2>&1 | tee "$_log" | tail -3
  # The install summary is the authoritative roster of what this release owns.
  strip_ansi < "$_log" \
    | grep -o '~/\.agents/skills/[a-zA-Z0-9._-]*' \
    | sed 's#.*/##' | sort -u > "$ROSTER.new"
  if [ ! -s "$ROSTER.new" ]; then
    rm -f "$ROSTER.new"
    vs_die "could not read the skill roster out of the installer output ($_log)"
  fi
  mv "$ROSTER.new" "$ROSTER"
  rm -f "$_log"
  vs_ok "roster: $(wc -l < "$ROSTER" | tr -d ' ') skills recorded in workflows/hyperframes-skills.txt"

  vs_step "hyperframes doctor (downloads the headless browser it renders with)"
  npx --yes "hyperframes@${VS_HF_VERSION}" doctor 2>&1 | tail -30 || true
  npx --yes "hyperframes@${VS_HF_VERSION}" browser ensure 2>&1 | tail -5 || \
    vs_warn "browser ensure failed - local renders will not work until it succeeds"

  cmd_sync
}

# --------------------------------------------------------------------- sync --
cmd_sync() {
  [ -f "$ROSTER" ] || vs_die "no roster at $ROSTER - run: hf_pin.sh install"
  SRC=$(hf_src_root) || vs_die "no installed skill pack found - run: hf_pin.sh install"
  mkdir -p "$DEST"

  vs_step "syncing $(wc -l < "$ROSTER" | tr -d ' ') HyperFrames skills from $SRC"
  _copied=0; _absent=0
  while IFS= read -r name; do
    [ -n "$name" ] || continue
    if [ -d "$SRC/$name" ]; then
      rm -rf "$DEST/$name"
      cp -R "$SRC/$name" "$DEST/$name"
      _copied=$((_copied+1))
    else
      vs_warn "roster lists '$name' but it is not installed at $SRC"
      _absent=$((_absent+1))
    fi
  done < "$ROSTER"
  vs_ok "$_copied copied${_absent:+, $_absent absent}"

  cmd_lock
}

# --------------------------------------------------------------------- lock --
# Rewrites skills-lock.json: source, path, and the sha256 of each SKILL.md's
# bytes. Entries from other packs (higgsfield, local) are preserved as-is.
cmd_lock() {
  vs_step "writing skills-lock.json"
  vs_py "$VS_SCRIPTS/hf_lock.py" \
    --root "$VS_ROOT" --lock "$LOCK" --roster "$ROSTER" \
    --source "$SOURCE_REPO" --version "$VS_HF_VERSION"
}

# ------------------------------------------------------------------- verify --
cmd_verify() {
  vs_py "$VS_SCRIPTS/hf_lock.py" --root "$VS_ROOT" --lock "$LOCK" --verify
}

# --------------------------------------------------------------------- bump --
cmd_bump() {
  _new="${1:-}"
  [ -n "$_new" ] || vs_die "usage: hf_pin.sh bump <version>   e.g. hf_pin.sh bump 0.7.69"
  _old="$VS_HF_VERSION"
  [ "$_new" = "$_old" ] && vs_die "already pinned to $_old"

  vs_info ""
  vs_info "Moving the HyperFrames pin $_old -> $_new."
  vs_info "This is a deliberate move. The rule from CLAUDE.md > Lab Notes:"
  vs_info "  re-render ONE graphics part on the new pin and review it before"
  vs_info "  re-rendering anything else. Contract breakages land silently -"
  vs_info "  the capture dies or the comp renders blank, not a clean error."
  vs_info ""

  # The pin lives in exactly one place: VS_HF_VERSION in workflows/lib/common.sh.
  _tmp="$VS_ROOT/workflows/lib/common.sh.bump"
  sed "s/^VS_HF_VERSION=\"\${VS_HF_VERSION:-.*}\"$/VS_HF_VERSION=\"\${VS_HF_VERSION:-$_new}\"/" \
    "$VS_ROOT/workflows/lib/common.sh" > "$_tmp"
  grep -q "VS_HF_VERSION:-$_new" "$_tmp" || { rm -f "$_tmp"; vs_die "could not rewrite the pin in workflows/lib/common.sh"; }
  mv "$_tmp" "$VS_ROOT/workflows/lib/common.sh"
  vs_ok "pin is now $_new in workflows/lib/common.sh"

  VS_HF_VERSION="$_new"
  cmd_install

  vs_info ""
  vs_info "Next, in order:"
  vs_info "  1. pick the smallest graphics part in the active job"
  vs_info "  2. workflows/scripts/hf_render.sh <job> <part>   (re-renders that part only)"
  vs_info "  3. eyeball it against the previous render before touching any other part"
  vs_info "  4. if it broke: hf_pin.sh bump $_old  and note what broke in CLAUDE.md > Lab Notes"
}

case "${1:-}" in
  install) shift; cmd_install "$@" ;;
  sync)    shift; cmd_sync "$@" ;;
  lock)    shift; cmd_lock "$@" ;;
  verify)  shift; cmd_verify "$@" ;;
  bump)    shift; cmd_bump "$@" ;;
  version) printf '%s\n' "$VS_HF_VERSION" ;;
  *) sed -n '2,20p' "$0" | sed 's/^# \{0,1\}//'; exit 1 ;;
esac
