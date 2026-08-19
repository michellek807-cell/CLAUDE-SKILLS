#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""audio_qa.py - LOCK: run an audio QA pass after every splice.

Joint clicks, silence gaps, limiter pressure, and A/V drift. It prints what it
found. It does not silently pass, and it does not quietly "fix" anything - a
click means the splice was wrong and the fix belongs upstream in the cut list.

  --strict  exit non-zero when something is over threshold
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vslib  # noqa: E402

QA_RATE = 48000
CLICK_WINDOW = 0.040          # +/- around a joint
CLICK_RATIO = 8.0             # x the file's own 99.9th-percentile sample step
SILENCE_DB = -50.0
SILENCE_MIN = 0.400
DRIFT_MS = 40.0
LIMITER_BUSY_PCT = 2.0


def db(x):
    import numpy as np
    return 20.0 * np.log10(np.maximum(np.abs(x), 1e-12))


def check_clicks(samples, joints, findings):
    """A joint that clicks shows a sample step far outside the file's own norm."""
    import numpy as np
    if not joints:
        vslib.dim("no joints to check (single segment)")
        return
    diff = np.abs(np.diff(samples))
    baseline = float(np.percentile(diff, 99.9)) if diff.size else 0.0
    if baseline <= 0:
        baseline = 1e-6
    thresh = baseline * CLICK_RATIO
    half = int(CLICK_WINDOW * QA_RATE)
    worst = []
    for i, t in enumerate(joints):
        c = int(t * QA_RATE)
        lo, hi = max(0, c - half), min(diff.size, c + half)
        if hi <= lo:
            continue
        peak = float(diff[lo:hi].max())
        worst.append((peak / thresh, i, t, peak))
    worst.sort(reverse=True)
    bad = [w for w in worst if w[0] >= 1.0]
    if bad:
        findings.append("clicks")
        vslib.warn("%d of %d joint(s) show a discontinuity above %.1fx the file's norm:"
                   % (len(bad), len(joints), CLICK_RATIO))
        for ratio, i, t, peak in bad[:6]:
            vslib.warn("    joint %-3d at %s   %.1fx" % (i, vslib.tc(t), ratio * CLICK_RATIO))
        vslib.dim("fix upstream: widen crossfade_ms, or move that boundary further "
                  "into silence in cut/cut.config.json - never patch the rendered audio")
    else:
        headroom = worst[0][0] * CLICK_RATIO if worst else 0.0
        vslib.ok("joints clean: %d checked, worst %.1fx of norm (limit %.0fx)"
                 % (len(joints), headroom, CLICK_RATIO))


def check_silence(samples, findings, total):
    """Fades to zero and over-eager cuts both show up as holes."""
    import numpy as np
    env, hop = vslib.rms_envelope(samples, QA_RATE, hop_ms=10.0, win_ms=30.0)
    quiet = env < SILENCE_DB
    runs = []
    start = None
    for i, q in enumerate(quiet):
        if q and start is None:
            start = i
        elif not q and start is not None:
            runs.append((start * hop, i * hop))
            start = None
    if start is not None:
        runs.append((start * hop, len(quiet) * hop))
    # Ignore silence at the very head/tail - that is topping and tailing.
    runs = [r for r in runs if r[0] > 0.25 and r[1] < total - 0.25]
    long_runs = [r for r in runs if (r[1] - r[0]) >= SILENCE_MIN]
    if long_runs:
        findings.append("silence")
        vslib.warn("%d silent hole(s) over %.0f ms below %.0f dBFS:"
                   % (len(long_runs), SILENCE_MIN * 1000, SILENCE_DB))
        for a, b in sorted(long_runs, key=lambda r: r[0] - r[1])[:6]:
            vslib.warn("    %s  for %.0f ms" % (vslib.tc(a), (b - a) * 1000))
        vslib.dim("a hole at a joint means a fade to zero crept in; room tone should carry through")
    else:
        vslib.ok("no silent holes over %.0f ms" % (SILENCE_MIN * 1000))


def check_limiter(spliced, findings, gain_db, limit_db):
    """How hard the master stage is working. Heavy pressure = flat, lifeless voice."""
    import numpy as np
    pre = vslib._decode(spliced, [], QA_RATE)     # all channels, no downmix
    if pre.size == 0:
        return
    gained = np.abs(pre) * (10.0 ** (gain_db / 20.0))
    limit = 10.0 ** (limit_db / 20.0)
    pct = 100.0 * float((gained > limit).sum()) / gained.size
    peak_db = float(db(gained.max()))
    over_db = peak_db - limit_db
    if pct > LIMITER_BUSY_PCT:
        findings.append("limiter")
        vslib.warn("limiter is working hard: %.1f%% of samples over %.0f dBFS, "
                   "peaks %.1f dB above the ceiling" % (pct, limit_db, over_db))
        vslib.dim("lower VS_GAIN_DB (currently +%.0f) rather than reaching for a compressor"
                  % gain_db)
    elif pct < 0.001 and peak_db < limit_db - 6:
        findings.append("quiet")
        vslib.warn("limiter never engages and peaks reach only %.1f dBFS - the take is quiet; "
                   "raise VS_GAIN_DB" % peak_db)
    else:
        vslib.ok("limiter pressure %.2f%% of samples, peaks %+.1f dB into the ceiling"
                 % (pct, over_db))


def check_encode(media, findings):
    info = vslib.ffprobe_json(media)
    a = next((s for s in info["streams"] if s.get("codec_type") == "audio"), None)
    if not a:
        findings.append("noaudio")
        vslib.warn("no audio stream in the master")
        return
    br = a.get("bit_rate") or info.get("format", {}).get("bit_rate")
    kbps = int(br) // 1000 if br else None
    if kbps is not None and kbps < 250:
        findings.append("bitrate")
        vslib.warn("audio is %d kbps - the lock is 256k or better for every re-encode" % kbps)
    else:
        vslib.ok("audio %s @ %s kbps, %s Hz"
                 % (a.get("codec_name"), kbps if kbps else "?", a.get("sample_rate")))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--job-dir", required=True)
    ap.add_argument("--media", required=True, help="the mastered file")
    ap.add_argument("--spliced", help="pre-master PCM, for limiter pressure")
    ap.add_argument("--strict", action="store_true")
    a = ap.parse_args()

    cutlist_path = os.path.join(a.job_dir, "cut", "cutlist.json")
    cutlist = vslib.read_json(cutlist_path) if os.path.exists(cutlist_path) else None

    vslib.step("audio QA")
    samples = vslib.decode_mono(a.media, sample_rate=QA_RATE)
    total = samples.size / float(QA_RATE)
    findings = []

    joints = []
    if cutlist:
        segs = cutlist["segments"]
        joints = [s["out_out"] for s in segs[:-1]]
        expected = segs[-1]["out_out"]
        drift = (total - expected) * 1000.0
        if abs(drift) > DRIFT_MS:
            findings.append("drift")
            vslib.warn("rendered %.0f ms %s than the cut list (%s vs %s) - "
                       "a boundary is off the frame grid"
                       % (abs(drift), "longer" if drift > 0 else "shorter",
                          vslib.tc(total), vslib.tc(expected)))
        else:
            vslib.ok("length matches the cut list within %.0f ms" % abs(drift))

    check_clicks(samples, joints, findings)
    check_silence(samples, findings, total)
    if a.spliced and os.path.exists(a.spliced):
        check_limiter(a.spliced, findings,
                      float(os.environ.get("VS_GAIN_DB", "10")),
                      float(os.environ.get("VS_LIMIT_DBFS", "-6")))
    check_encode(a.media, findings)

    if findings:
        vslib.warn("QA finished with %d finding(s): %s" % (len(findings), ", ".join(findings)))
        if a.strict:
            sys.exit(2)
    else:
        vslib.ok("QA clean")


if __name__ == "__main__":
    main()
