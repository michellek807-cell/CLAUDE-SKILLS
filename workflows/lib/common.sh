#!/usr/bin/env bash
# common.sh - shared helpers for every script in this content system.
# Targets stock bash 3.2 (macOS) and bash 5 (Linux). No arrays-as-maps, no
# `mapfile`, no `${var,,}`, no globstar. Source it, never execute it.

# ---------------------------------------------------------------- output ----
if [ -t 2 ]; then
  VS_C_RED=$(printf '\033[31m'); VS_C_YEL=$(printf '\033[33m')
  VS_C_GRN=$(printf '\033[32m'); VS_C_DIM=$(printf '\033[2m')
  VS_C_OFF=$(printf '\033[0m')
else
  VS_C_RED=''; VS_C_YEL=''; VS_C_GRN=''; VS_C_DIM=''; VS_C_OFF=''
fi

vs_info() { printf '%s\n' "$*" >&2; }
vs_step() { printf '\n%s==>%s %s\n' "$VS_C_GRN" "$VS_C_OFF" "$*" >&2; }
vs_ok()   { printf '  %sok%s   %s\n' "$VS_C_GRN" "$VS_C_OFF" "$*" >&2; }
vs_dim()  { printf '  %s%s%s\n' "$VS_C_DIM" "$*" "$VS_C_OFF" >&2; }
vs_warn() { printf '  %swarn%s %s\n' "$VS_C_YEL" "$VS_C_OFF" "$*" >&2; }
vs_die()  { printf '  %sfail%s %s\n' "$VS_C_RED" "$VS_C_OFF" "$*" >&2; exit 1; }

# ------------------------------------------------------------------ paths ----
# Portable absolute path. `readlink -f` is not on stock macOS.
vs_abspath() {
  case "$1" in
    /*) printf '%s\n' "$1" ;;
     *) printf '%s\n' "$(pwd -P)/$1" ;;
  esac
}

vs_repo_root() {
  if [ -n "${VS_REPO_ROOT-}" ]; then printf '%s\n' "$VS_REPO_ROOT"; return 0; fi
  # common.sh lives at <root>/workflows/lib/common.sh
  _vs_d=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd -P)
  printf '%s\n' "$_vs_d"
}

VS_ROOT=$(vs_repo_root)
VS_SCRIPTS="$VS_ROOT/workflows/scripts"

vs_job_dir() {
  [ -n "$1" ] || vs_die "vs_job_dir: no job name"
  printf '%s\n' "$VS_ROOT/projects/$1"
}

vs_require_job() {
  _vs_j="$1"
  [ -n "$_vs_j" ] || vs_die "no job name given (usage: <script> <job-name> ...)"
  [ -d "$VS_ROOT/projects/$_vs_j" ] || vs_die "no such job: projects/$_vs_j (run new-job.sh first)"
  printf '%s\n' "$VS_ROOT/projects/$_vs_j"
}

# kebab-case-ify a title. Content title, never a camera filename.
vs_slug() {
  printf '%s' "$*" \
    | tr '[:upper:]' '[:lower:]' \
    | sed -e 's/[^a-z0-9]\{1,\}/-/g' -e 's/^-*//' -e 's/-*$//'
}

# ------------------------------------------------------------- platform ------
# The ONLY platform branch in this system is the video encoder.
vs_os() {
  case "$(uname -s)" in
    Darwin) printf 'macos\n' ;;
         *) printf 'linux\n' ;;
  esac
}

# Echoes encoder flags for the delivery encode. Word-split by the caller.
vs_video_encoder_args() {
  if [ "$(vs_os)" = "macos" ]; then
    printf '%s' "-c:v h264_videotoolbox -b:v ${VS_VIDEO_BITRATE:-14M} -profile:v high -pix_fmt yuv420p"
  else
    printf '%s' "-c:v libx264 -preset ${VS_X264_PRESET:-medium} -crf ${VS_X264_CRF:-16} -profile:v high -pix_fmt yuv420p"
  fi
}

vs_video_encoder_name() {
  if [ "$(vs_os)" = "macos" ]; then printf 'h264_videotoolbox\n'; else printf 'libx264\n'; fi
}

# ------------------------------------------------------------- utilities ----
vs_have() { command -v "$1" >/dev/null 2>&1; }

vs_require() {
  for _vs_c in "$@"; do
    vs_have "$_vs_c" || vs_die "missing dependency: $_vs_c  (run ./check-setup.sh)"
  done
}

vs_sha256() {
  if vs_have sha256sum; then sha256sum "$1" | awk '{print $1}'
  elif vs_have shasum;   then shasum -a 256 "$1" | awk '{print $1}'
  else vs_die "no sha256sum or shasum on PATH"; fi
}

# uv runs every Python step. Scripts carry PEP 723 inline dependency metadata,
# so nothing is ever installed into the system interpreter.
vs_py() {
  vs_require uv
  uv run --quiet "$@"
}

# ---------------------------------------------------------------- probing ----
vs_probe() { # vs_probe <file> <stream:entry>  e.g. vs_probe in.mov v:r_frame_rate
  _vs_f="$1"; _vs_sel="${2%%:*}"; _vs_key="${2#*:}"
  ffprobe -v error -select_streams "$_vs_sel" \
    -show_entries "stream=$_vs_key" -of default=nw=1:nk=1 "$_vs_f" 2>/dev/null | head -1
}

vs_duration() {
  ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 "$1" 2>/dev/null | head -1
}

vs_fps_rational() { # "30000/1001"
  _vs_r=$(vs_probe "$1" v:r_frame_rate)
  [ -n "$_vs_r" ] || _vs_r=$(vs_probe "$1" v:avg_frame_rate)
  case "$_vs_r" in ''|0/0|N/A) _vs_r="30/1" ;; esac
  printf '%s\n' "$_vs_r"
}

vs_has_audio() {
  _vs_n=$(ffprobe -v error -select_streams a -show_entries stream=index -of csv=p=0 "$1" 2>/dev/null | head -1)
  [ -n "$_vs_n" ]
}

# --------------------------------------------------------------- json bits ---
# Bash never parses JSON by hand. Reads one dotted path out of a JSON file.
vs_json() { # vs_json <file> <dotted.path> [default]
  uv run --quiet - "$1" "$2" "${3-}" <<'PYEOF'
import json, sys
cur = json.load(open(sys.argv[1]))
for part in sys.argv[2].split("."):
    if part == "":
        continue
    if isinstance(cur, list):
        cur = cur[int(part)]
    else:
        cur = cur.get(part) if isinstance(cur, dict) else None
    if cur is None:
        print(sys.argv[3] if len(sys.argv) > 3 else "")
        raise SystemExit(0)
print(cur if not isinstance(cur, (dict, list)) else json.dumps(cur))
PYEOF
}

# ---------------------------------------------------- locked audio master ----
# Lock: static +10 dB gain -> -6 dBFS limiter -> AAC 256k. Exactly once, on the
# assembled track. Never loudnorm, never per-segment FX.
VS_GAIN_DB="${VS_GAIN_DB:-10}"
VS_LIMIT_DBFS="${VS_LIMIT_DBFS:--6}"
VS_AAC_BITRATE="${VS_AAC_BITRATE:-256k}"

vs_limit_linear() { # -6 -> 0.5012
  uv run --quiet - "$1" <<'PYEOF'
import sys
print("%.6f" % (10 ** (float(sys.argv[1]) / 20.0)))
PYEOF
}

vs_master_filter() {
  _vs_lin=$(vs_limit_linear "$VS_LIMIT_DBFS")
  printf 'volume=%sdB,alimiter=level_in=1:level_out=1:limit=%s:attack=5:release=50:level=disabled' \
    "$VS_GAIN_DB" "$_vs_lin"
}

# --------------------------------------------------------- HyperFrames pin ---
# Pinned deliberately. npx floats to latest and past releases have broken the
# composition contract mid-job. Move it one part at a time, re-rendered and
# reviewed. See CLAUDE.md > Lab Notes.
VS_HF_VERSION="${VS_HF_VERSION:-0.7.68}"
vs_hf() { vs_require npx; npx --yes "hyperframes@${VS_HF_VERSION}" "$@"; }
