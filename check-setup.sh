#!/usr/bin/env bash
# check-setup.sh - report only. Verifies every dependency this system needs and
# says exactly what is missing and how to install it on THIS machine.
# It never installs anything and never modifies the repo.
#
#   ./check-setup.sh            full report
#   ./check-setup.sh --quiet    only problems
#   ./check-setup.sh --strict   exit 1 if a required dependency is missing

set -u

ROOT=$(cd "$(dirname "$0")" && pwd -P)
. "$ROOT/workflows/lib/common.sh"

QUIET=0; STRICT=0
for a in "$@"; do
  case "$a" in
    --quiet|-q)  QUIET=1 ;;
    --strict|-s) STRICT=1 ;;
    --help|-h)   sed -n '2,9p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) vs_die "unknown flag: $a" ;;
  esac
done

OS=$(vs_os)
MISSING_REQ=0
MISSING_OPT=0

case "$OS" in
  macos) PKG="brew install"; PY_PIL_HINT="brew install pillow || uv pip install --system pillow" ;;
  linux) PKG="sudo apt-get install -y"; PY_PIL_HINT="sudo apt-get install -y python3-pil   # never bare pip on Linux" ;;
esac

say()  { [ "$QUIET" = 1 ] || printf '%s\n' "$*"; }
row_ok()   { [ "$QUIET" = 1 ] || printf '  %sok%s     %-18s %s\n' "$VS_C_GRN" "$VS_C_OFF" "$1" "$2"; }
row_miss() { printf '  %smissing%s %-18s %s\n' "$VS_C_RED" "$VS_C_OFF" "$1" "$2"; MISSING_REQ=$((MISSING_REQ+1)); }
row_opt()  { printf '  %sabsent%s  %-18s %s\n' "$VS_C_YEL" "$VS_C_OFF" "$1" "$2"; MISSING_OPT=$((MISSING_OPT+1)); }

check_req() { # name  command  install-hint  [version-cmd]
  if vs_have "$2"; then
    _v=""
    [ -n "${4-}" ] && _v=$(eval "$4" 2>/dev/null | head -1)
    row_ok "$1" "${_v:-$(command -v "$2")}"
  else
    row_miss "$1" "install: $3"
  fi
}

check_opt() { # name  command  install-hint  [version-cmd]
  if vs_have "$2"; then
    _v=""
    [ -n "${4-}" ] && _v=$(eval "$4" 2>/dev/null | head -1)
    row_ok "$1" "${_v:-$(command -v "$2")}"
  else
    row_opt "$1" "optional - $3"
  fi
}

say ""
say "video system setup report"
say "  machine       $(uname -s) $(uname -m)  ->  $OS"
say "  repo          $ROOT"
say "  video encoder $(vs_video_encoder_name)   (the only platform branch in this system)"
say "  hyperframes   pinned to $VS_HF_VERSION"
say ""

# ------------------------------------------------------------------ core ----
say "core"
check_req "ffmpeg"   ffmpeg   "$PKG ffmpeg"  "ffmpeg -version | head -1 | cut -d' ' -f1-3"
check_req "ffprobe"  ffprobe  "$PKG ffmpeg"  "ffprobe -version | head -1 | cut -d' ' -f1-3"
check_req "uv"       uv       "curl -LsSf https://astral.sh/uv/install.sh | sh"  "uv --version"
check_req "node"     node     "$PKG node"    "node --version"
check_req "npx"      npx      "$PKG node"    "npx --version"
check_req "python3"  python3  "$PKG python3" "python3 --version"

# --------------------------------------------------------------- encoder ----
say ""
say "video encoder"
if vs_have ffmpeg; then
  ENC=$(vs_video_encoder_name)
  if ffmpeg -hide_banner -encoders 2>/dev/null | grep -q " $ENC "; then
    row_ok "$ENC" "available in this ffmpeg build"
  else
    if [ "$OS" = macos ]; then
      row_miss "$ENC" "this ffmpeg has no VideoToolbox; reinstall: brew reinstall ffmpeg"
    else
      row_miss "$ENC" "this ffmpeg has no libx264; reinstall: $PKG ffmpeg"
    fi
  fi
  if ffmpeg -hide_banner -filters 2>/dev/null | grep -q " alimiter "; then
    row_ok "alimiter" "present (audio master stage)"
  else
    row_miss "alimiter" "ffmpeg built without alimiter; reinstall: $PKG ffmpeg"
  fi
  if ffmpeg -hide_banner -filters 2>/dev/null | grep -q " acrossfade "; then
    row_ok "acrossfade" "present (equal-power joints)"
  else
    row_miss "acrossfade" "ffmpeg built without acrossfade; reinstall: $PKG ffmpeg"
  fi
else
  row_miss "encoder check" "needs ffmpeg first"
fi

# ---------------------------------------------------------------- python ----
say ""
say "python"
if vs_have python3; then
  if python3 -c 'import PIL, sys; sys.stdout.write(PIL.__version__)' >/dev/null 2>&1; then
    row_ok "PIL (Pillow)" "$(python3 -c 'import PIL;print("Pillow "+PIL.__version__)')"
  else
    row_miss "PIL (Pillow)" "install: $PY_PIL_HINT"
  fi
else
  row_miss "PIL (Pillow)" "needs python3 first"
fi
if vs_have uv; then
  row_ok "uv script deps" "numpy/whisperx resolved per-script via PEP 723 (no system installs)"
fi

# ----------------------------------------------------------- transcription ---
say ""
say "transcription (step 2 - the only slow step allowed)"
if vs_have uv; then
  row_ok "whisperx" "resolved on demand by uv from workflows/scripts/transcribe.py"
  HF_CACHE="${HF_HOME:-$HOME/.cache/huggingface}"
  if ls -d "$HF_CACHE"/hub/models--Systran--faster-whisper-large-v3 >/dev/null 2>&1; then
    row_ok "large-v3 weights" "cached in $HF_CACHE"
  else
    row_opt "large-v3 weights" "first rough-cut downloads them once (~3 GB) into $HF_CACHE"
  fi
else
  row_miss "whisperx" "needs uv first"
fi

# ------------------------------------------------------------ hyperframes ----
say ""
say "graphics engine (HyperFrames $VS_HF_VERSION - npm package, never a cloned repo)"
if vs_have npx; then
  HF_SKILLS=$(ls "$ROOT/.claude/skills" 2>/dev/null | grep -c '^hyperframes' || true)
  if [ "${HF_SKILLS:-0}" -ge 1 ]; then
    row_ok "skill pack" "$(ls "$ROOT/.claude/skills" | wc -l | tr -d ' ') skills in .claude/skills"
  else
    row_miss "skill pack" "npx hyperframes@$VS_HF_VERSION skills  then  workflows/scripts/hf_pin.sh sync"
  fi
  if [ -f "$ROOT/skills-lock.json" ]; then
    row_ok "skills-lock.json" "present - verify with workflows/scripts/hf_pin.sh verify"
  else
    row_miss "skills-lock.json" "workflows/scripts/hf_pin.sh sync"
  fi
  CHROME_DIR="${HOME}/.cache/hyperframes"
  if [ -d "$CHROME_DIR" ] || [ -d "${HOME}/Library/Caches/hyperframes" ]; then
    row_ok "headless browser" "hyperframes cache present"
  else
    row_opt "headless browser" "npx hyperframes@$VS_HF_VERSION doctor   (downloads the renderer)"
  fi
else
  row_miss "hyperframes" "needs node/npx first"
fi

# --------------------------------------------------------------- editing -----
say ""
say "editing-app handoff (default finish after step 2)"
if [ "$OS" = macos ]; then
  if [ -d "/Applications/Adobe Premiere Pro 2025" ] || ls -d /Applications/Adobe\ Premiere\ Pro* >/dev/null 2>&1; then
    row_ok "Premiere Pro" "found in /Applications"
  else
    row_opt "Premiere Pro" "not found - FCP7 XML is still written to cut/ for any host"
  fi
  if [ -d "/Applications/CapCut.app" ]; then
    row_ok "CapCut" "/Applications/CapCut.app"
  else
    row_opt "CapCut" "not found - draft folder is still written to cut/"
  fi
else
  row_opt "editing app" "WSL2/Linux: XML + draft are written to cut/, open them from the Windows host"
fi

# ------------------------------------------------------------------ disk -----
say ""
say "workspace"
[ -d "$ROOT/projects" ] && row_ok "projects/" "$(ls "$ROOT/projects" 2>/dev/null | grep -v '^\.' | wc -l | tr -d ' ') job(s)" \
  || row_miss "projects/" "mkdir -p projects"
[ -d "$ROOT/presets" ]   && row_ok "presets/"   "$(ls "$ROOT/presets"/*.md 2>/dev/null | wc -l | tr -d ' ') locked look(s)" || row_opt "presets/" "no presets yet"
if [ -w "$ROOT" ]; then row_ok "writable" "builds live in the job folder, never /tmp"; else row_miss "writable" "repo is not writable"; fi

# --------------------------------------------------------------- summary -----
printf '\n'
if [ "$MISSING_REQ" -eq 0 ]; then
  printf '  %sready%s   all required dependencies present' "$VS_C_GRN" "$VS_C_OFF"
  [ "$MISSING_OPT" -gt 0 ] && printf '  (%s optional item(s) absent)' "$MISSING_OPT"
  printf '\n\n'
  exit 0
fi
printf '  %s%s required dependenc(ies) missing%s - install the lines above, then re-run ./check-setup.sh\n\n' \
  "$VS_C_RED" "$MISSING_REQ" "$VS_C_OFF"
[ "$STRICT" = 1 ] && exit 1
exit 0
