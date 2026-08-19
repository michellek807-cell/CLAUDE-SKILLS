#!/usr/bin/env bash
# music_bed.sh - pipeline step 6, optional. A flat bed under the voice.
#
#   music_bed.sh <job> <track.mp3|wav> [--level -22] [--none]
#
# Flat means flat: one static level for the whole piece. No sidechain ducking,
# no automation, no compressor riding the voice. Dynamic gain on a music bed is
# the same failure as loudnorm on a voice track - it breathes, and once you
# hear it you cannot stop hearing it. If the bed is fighting the voice, the bed
# is too loud; turn it down, do not automate it.
#
# The mix happens on the PRE-MASTER PCM and then the one master chain runs
# again over the sum. That keeps the lock intact: the assembled track is
# polished exactly once, +10 dB then a -6 dBFS limiter then AAC 256k. Mixing
# into the already-mastered AAC would be a second lossy generation.

set -eu
. "$(cd "$(dirname "$0")/../lib" && pwd -P)/common.sh"
vs_require ffmpeg ffprobe

JOB="${1:-}"; shift 2>/dev/null || true
DIR=$(vs_require_job "$JOB")
TRACK=""; LEVEL="${VS_MUSIC_DB:--22}"; REMOVE=0
while [ $# -gt 0 ]; do
  case "$1" in
    --level) LEVEL="${2:-}"; shift 2 ;;
    --none)  REMOVE=1; shift ;;
    --*)     vs_die "unknown flag: $1" ;;
    *)       TRACK="$1"; shift ;;
  esac
done

SPLICED="$DIR/cut/$JOB.spliced.mkv"
MASTER="$DIR/cut/$JOB.mastered.mp4"
[ -f "$SPLICED" ] || vs_die "no cut/$JOB.spliced.mkv - the flat render path has not run"

AF=$(vs_master_filter)

if [ "$REMOVE" = 1 ]; then
  vs_step "removing the music bed, re-mastering the voice alone"
  ffmpeg -hide_banner -loglevel error -stats -nostdin -y -i "$SPLICED" \
    -map 0:v:0 -map 0:a:0 -c:v copy \
    -af "$AF" -c:a aac -b:a "$VS_AAC_BITRATE" -ar 48000 -ac 2 \
    -movflags +faststart "$MASTER" || vs_die "re-master failed"
  rm -f "$DIR/audio/$JOB.bed.wav"
  vs_ok "cut/$JOB.mastered.mp4 back to voice only"
  vs_py "$VS_SCRIPTS/audio_qa.py" --job-dir "$DIR" --media "$MASTER" --spliced "$SPLICED"
  exit 0
fi

[ -n "$TRACK" ] || vs_die "usage: music_bed.sh <job> <track> [--level -22] [--none]"
[ -f "$TRACK" ] || vs_die "no such track: $TRACK"

# Keep a copy in the job. audio/ is never pruned.
BED="$DIR/audio/$(basename "$TRACK")"
[ -f "$BED" ] || cp "$TRACK" "$BED"

DUR=$(vs_duration "$SPLICED")
BEDDUR=$(vs_duration "$BED")
vs_step "bed: $(basename "$BED")  ${LEVEL} dB under the voice"
vs_dim "voice ${DUR}s, track ${BEDDUR}s"

FADE_IN=1.2
FADE_OUT=1.6
FADE_AT=$(uv run --quiet - "$DUR" "$FADE_OUT" <<'PYEOF'
import sys
print("%.3f" % max(0.0, float(sys.argv[1]) - float(sys.argv[2])))
PYEOF
)

# Loop the bed if it is short, trim it if long, then one fade at each end of
# the FILM - never at a joint, where the voice track's own room tone carries.
GRAPH="[1:a]aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo"
GRAPH="$GRAPH,atrim=0:$DUR,asetpts=PTS-STARTPTS,volume=${LEVEL}dB"
GRAPH="$GRAPH,afade=t=in:st=0:d=$FADE_IN,afade=t=out:st=$FADE_AT:d=$FADE_OUT[bed];"
GRAPH="$GRAPH[0:a]aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo[voice];"
# duration=longest, NOT first: with `first`, amix ends on the first input's
# last whole frame and drops ~50 ms off the tail. The bed is already
# atrimmed to the voice length, so `longest` is exactly the voice length.
GRAPH="$GRAPH[voice][bed]amix=inputs=2:duration=longest:dropout_transition=0:normalize=0[sum];"
GRAPH="$GRAPH[sum]$AF[out]"

ffmpeg -hide_banner -loglevel error -stats -nostdin -y \
  -i "$SPLICED" -stream_loop -1 -i "$BED" \
  -filter_complex "$GRAPH" \
  -map 0:v:0 -map "[out]" -c:v copy \
  -c:a aac -b:a "$VS_AAC_BITRATE" -ar 48000 -ac 2 \
  -movflags +faststart "$MASTER" || vs_die "music mix failed"

vs_ok "cut/$JOB.mastered.mp4 with a flat bed at ${LEVEL} dB"

vs_py "$VS_SCRIPTS/audio_qa.py" --job-dir "$DIR" --media "$MASTER" --spliced "$SPLICED"

uv run --quiet - "$DIR/job.json" "$(basename "$BED")" "$LEVEL" <<'PYEOF'
import json, sys
p = sys.argv[1]; d = json.load(open(p))
d["stage"] = "music"
d["music"] = {"track": "audio/%s" % sys.argv[2], "level_db": float(sys.argv[3]),
              "mode": "flat bed, no ducking"}
json.dump(d, open(p, "w"), indent=2); open(p, "a").write("\n")
PYEOF
"$VS_SCRIPTS/project_doc.sh" "$JOB" >/dev/null
