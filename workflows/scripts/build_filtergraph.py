#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""build_filtergraph.py - turn cut/cutlist.json into ONE ffmpeg filtergraph.

LOCK: cut A/V in a single lossless filtergraph. Not segment files plus a
concat demuxer - that is N encodes and N chances to drift. One graph, one pass,
audio carried out as PCM so the master stage downstream is the only lossy step.

LOCK: joints are short equal-power crossfades over real continuing room tone.
Each segment's audio window is widened by half a crossfade at each joint
(`a_in`/`a_out` in the cutlist), so the fade is made of audio the take actually
contains just past the cut, and the assembled audio comes out exactly as long
as the assembled video. Never a fade to zero: that trades a click for a hole.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vslib  # noqa: E402

MIN_XFADE = 0.004  # below this acrossfade is pointless; butt-join instead


def build(cutlist, sample_rate=48000, channel_layout="stereo"):
    segs = cutlist["segments"]
    n = len(segs)
    lines = []

    # Decode once, normalise once, then split. Nothing per-segment is ever
    # "processed" - no per-segment audio FX, that is what makes clicks.
    if n == 1:
        lines.append("[0:v]null[vsrc0]")
        lines.append("[0:a]aformat=sample_fmts=fltp:sample_rates=%d:channel_layouts=%s[asrc0]"
                     % (sample_rate, channel_layout))
    else:
        lines.append("[0:v]split=%d%s" % (n, "".join("[vsrc%d]" % i for i in range(n))))
        lines.append("[0:a]aformat=sample_fmts=fltp:sample_rates=%d:channel_layouts=%s,asplit=%d%s"
                     % (sample_rate, channel_layout, n, "".join("[asrc%d]" % i for i in range(n))))

    for s in segs:
        i = s["i"]
        lines.append("[vsrc%d]trim=start=%.6f:end=%.6f,setpts=PTS-STARTPTS[v%d]"
                     % (i, s["src_in"], s["src_out"], i))
        lines.append("[asrc%d]atrim=start=%.6f:end=%.6f,asetpts=PTS-STARTPTS[a%d]"
                     % (i, s["a_in"], s["a_out"], i))

    # Video: straight concat on the frame grid.
    if n == 1:
        lines.append("[v0]null[vout]")
    else:
        lines.append("%sconcat=n=%d:v=1:a=0[vout]" % ("".join("[v%d]" % i for i in range(n)), n))

    # Audio: pairwise equal-power crossfades, one per joint.
    cur = "a0"
    for i in range(n - 1):
        nxt = "a%d" % (i + 1)
        out = "ax%d" % (i + 1)
        x = float(segs[i].get("xfade_out") or 0.0)
        if x >= MIN_XFADE:
            lines.append("[%s][%s]acrossfade=d=%.6f:c1=qsin:c2=qsin[%s]" % (cur, nxt, x, out))
        else:
            # No room for a fade in this gap; a butt join is the honest fallback.
            lines.append("[%s][%s]concat=n=2:v=0:a=1[%s]" % (cur, nxt, out))
        cur = out
    lines.append("[%s]anull[aout]" % cur)
    return ";\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cutlist", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--sample-rate", type=int, default=48000)
    ap.add_argument("--channel-layout", default="stereo")
    a = ap.parse_args()

    cutlist = vslib.read_json(a.cutlist)
    graph = build(cutlist, a.sample_rate, a.channel_layout)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as fh:
        fh.write(graph)

    segs = cutlist["segments"]
    xf = [s["xfade_out"] for s in segs[:-1]]
    butt = sum(1 for x in xf if x < MIN_XFADE)
    vslib.ok("filtergraph: %d segments, %d crossfaded joint(s)%s"
             % (len(segs), len(xf) - butt, ", %d butt-joined" % butt if butt else ""))
    # Prove the arithmetic before ffmpeg spends minutes on it.
    v_total = sum(s["dur"] for s in segs)
    a_total = sum(s["a_out"] - s["a_in"] for s in segs) - sum(xf)
    drift = abs(v_total - a_total)
    if drift > 1e-4:
        vslib.warn("video %.4fs vs audio %.4fs - %.1f ms of drift in the plan"
                   % (v_total, a_total, drift * 1000))
    else:
        vslib.dim("A/V lengths agree to %.3f ms before encoding" % (drift * 1000))


if __name__ == "__main__":
    main()
