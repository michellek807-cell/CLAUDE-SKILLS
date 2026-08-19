#!/usr/bin/env bash
# render_cut.sh - pipeline step 2c. Splice, then master the audio exactly once.
#
#   render_cut.sh <job>
#
# Two stages, and the split between them is the whole point.
#
#   A. splice   one ffmpeg pass, one filtergraph. Video encoded once with the
#               platform encoder; audio carried out as 24-bit PCM, untouched.
#   B. master   the assembled track is polished ONCE: static +10 dB, then a
#               -6 dBFS limiter, then AAC 256k. Video is stream-copied, so it
#               is never re-encoded and generation loss cannot accumulate.
#
# Never dynamic loudnorm - it pumps on speech. Never per-segment audio FX -
# every segment edge becomes a click. One static gain, one limiter, one encode.

set -eu
. "$(cd "$(dirname "$0")/../lib" && pwd -P)/common.sh"
vs_require ffmpeg ffprobe

JOB="${1:-}"
DIR=$(vs_require_job "$JOB")
CUTLIST="$DIR/cut/cutlist.json"
[ -f "$CUTLIST" ] || vs_die "no cut/cutlist.json - run plan_cut.py first"

RAWREL=$(vs_json "$DIR/job.json" raw.file)
RAW="$DIR/$RAWREL"
[ -f "$RAW" ] || vs_die "raw file missing: $RAWREL"
FPS=$(vs_json "$CUTLIST" source.fps)

SPLICED="$DIR/cut/$JOB.spliced.mkv"
MASTER="$DIR/cut/$JOB.mastered.mp4"
GRAPH="$DIR/cache/filtergraph.txt"

# ---------------------------------------------------------------- stage A ----
vs_step "splice: one lossless filtergraph"
vs_py "$VS_SCRIPTS/build_filtergraph.py" --cutlist "$CUTLIST" --out "$GRAPH"

ENC_ARGS=$(vs_video_encoder_args)
vs_dim "encoder: $(vs_video_encoder_name)  fps: $FPS"

# shellcheck disable=SC2086
ffmpeg -hide_banner -loglevel error -stats -nostdin -y \
  -i "$RAW" \
  -filter_complex_script "$GRAPH" \
  -map '[vout]' -map '[aout]' \
  $ENC_ARGS -fps_mode cfr -r "$FPS" \
  -c:a pcm_s24le -ar 48000 -ac 2 \
  "$SPLICED" || vs_die "splice failed - the filtergraph is at $GRAPH"

vs_ok "cut/$JOB.spliced.mkv  $(vs_duration "$SPLICED")s  (PCM audio, not yet mastered)"

# ---------------------------------------------------------------- stage B ----
vs_step "master: +${VS_GAIN_DB} dB -> ${VS_LIMIT_DBFS} dBFS limiter -> AAC ${VS_AAC_BITRATE}"
AF=$(vs_master_filter)
vs_dim "$AF"

ffmpeg -hide_banner -loglevel error -stats -nostdin -y \
  -i "$SPLICED" \
  -map 0:v:0 -map 0:a:0 \
  -c:v copy \
  -af "$AF" -c:a aac -b:a "$VS_AAC_BITRATE" -ar 48000 -ac 2 \
  -movflags +faststart \
  "$MASTER" || vs_die "master failed"

vs_ok "cut/$JOB.mastered.mp4  $(vs_duration "$MASTER")s"

# ------------------------------------------------------------------- QA ------
vs_py "$VS_SCRIPTS/audio_qa.py" --job-dir "$DIR" --media "$MASTER" --spliced "$SPLICED"

uv run --quiet - "$DIR/job.json" "$JOB" <<'PYEOF'
import json, sys
p = sys.argv[1]
d = json.load(open(p))
d["stage"] = "cut"
d.setdefault("cut", {})
d["cut"]["spliced"] = "cut/%s.spliced.mkv" % sys.argv[2]
d["cut"]["mastered"] = "cut/%s.mastered.mp4" % sys.argv[2]
json.dump(d, open(p, "w"), indent=2)
open(p, "a").write("\n")
PYEOF

"$VS_SCRIPTS/project_doc.sh" "$JOB" >/dev/null
