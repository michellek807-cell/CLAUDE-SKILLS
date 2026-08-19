#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""assert_pipeline.py - check that every lock actually held on the self test."""
import argparse
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vslib  # noqa: E402

FAILURES = []
PASSES = []


def check(label, cond, detail=""):
    (PASSES if cond else FAILURES).append(label)
    mark = "  %sPASS%s" % (vslib._G, vslib._O) if cond else "  %sFAIL%s" % (vslib._R, vslib._O)
    print("%s %-46s %s" % (mark, label, detail), file=sys.stderr)


def main():
    import numpy as np

    ap = argparse.ArgumentParser()
    ap.add_argument("--job-dir", required=True)
    ap.add_argument("--truth", required=True)
    a = ap.parse_args()

    job = vslib.read_json(os.path.join(a.job_dir, "job.json"))
    name = job["name"]
    cut = vslib.read_json(os.path.join(a.job_dir, "cut", "cutlist.json"))
    tr = vslib.read_json(os.path.join(a.job_dir, "outputs", "%s.transcript.json" % name))
    truth = vslib.read_json(a.truth)
    grid = vslib.FrameGrid(cut["source"]["fps"])
    segs = cut["segments"]

    # ---- 1. boundaries were measured, not copied from the transcript -------
    onset = {round(t["onset"], 3): t["w"] for t in truth["_truth"]}
    onsets = sorted(onset)
    err = []
    for s in segs:
        near = min(onsets, key=lambda o: abs(o - s["src_in"]))
        err.append(s["src_in"] - near)
    mean_err = sum(err) / len(err)
    # Every in-point should sit just BEFORE the true acoustic attack (head_pad),
    # not 50-100 ms after it where the transcript claimed.
    check("in-points land before the true onset",
          all(e < 0.015 for e in err) and -0.16 < mean_err < 0.0,
          "mean %+.0f ms, worst %+.0f ms" % (mean_err * 1000, max(err) * 1000))

    deltas = [s["measured"]["in_delta"] for s in segs]
    check("measurement moved boundaries off transcript time",
          all(d < -0.02 for d in deltas),
          "mean %+.0f ms" % (1000 * sum(deltas) / len(deltas)))

    # ---- 2. frame grid ----------------------------------------------------
    off = [s for s in segs
           if abs(s["src_in"] - grid.snap(s["src_in"])) > 1e-6
           or abs(s["src_out"] - grid.snap(s["src_out"])) > 1e-6]
    check("every boundary on the frame grid", not off,
          "%d segments @ %s fps" % (len(segs), cut["source"]["fps"]))

    frames_ok = all(s["frames"] == round(s["dur"] * float(grid.fps)) for s in segs)
    check("segment durations are whole frames", frames_ok)

    # ---- 3. audio handles cancel exactly ----------------------------------
    v_total = sum(s["dur"] for s in segs)
    a_total = sum(s["a_out"] - s["a_in"] for s in segs) - sum(s["xfade_out"] for s in segs[:-1])
    check("audio window sum == video length", abs(v_total - a_total) < 1e-4,
          "%.6f vs %.6f" % (v_total, a_total))

    handles_inside = all(
        segs[i]["a_out"] <= segs[i + 1]["a_in"] + 1e-9 for i in range(len(segs) - 1))
    check("crossfade handles stay inside removed gaps", handles_inside,
          "no duplicated speech at joints")

    # ---- 4. filler and dead air are gone ----------------------------------
    kept_words = set(vslib.normalize_token(w["w"]) for w in tr["words"])
    check("filler words removed", not (kept_words & {"um", "uh"}),
          "checked um, uh")
    dupes = sum(1 for i in range(1, len(tr["words"]))
                if vslib.normalize_token(tr["words"][i]["w"])
                == vslib.normalize_token(tr["words"][i - 1]["w"]))
    check("stutters collapsed", dupes == 0, "%d immediate repeats left" % dupes)

    longest_gap = 0.0
    for i in range(1, len(tr["words"])):
        longest_gap = max(longest_gap, tr["words"][i]["s"] - tr["words"][i - 1]["e"])
    check("no dead air left over 0.6 s", longest_gap <= 0.62,
          "longest gap %.0f ms" % (longest_gap * 1000))

    # ---- 5. the rendered file ---------------------------------------------
    master = os.path.join(a.job_dir, "cut", "%s.mastered.mp4" % name)
    check("mastered file exists", os.path.exists(master))
    if os.path.exists(master):
        info = vslib.probe_media(master)
        expected = segs[-1]["out_out"]
        drift = abs(info["duration"] - expected)
        check("rendered length matches the cut list", drift < 0.045,
              "%.3f vs %.3f  (%.0f ms)" % (info["duration"], expected, drift * 1000))

        pr = vslib.ffprobe_json(master)
        astream = next(s for s in pr["streams"] if s["codec_type"] == "audio")
        kbps = int(astream.get("bit_rate") or 0) // 1000
        check("audio is AAC >= 256k", astream["codec_name"] == "aac" and kbps >= 250,
              "%s %d kbps" % (astream["codec_name"], kbps))

        samples = vslib.decode_mono(master, sample_rate=48000)
        peak_db = vslib.peak_dbfs(master)      # per-channel, not a downmix
        check("limiter held the ceiling", peak_db <= -5.0,
              "peak %.2f dBFS (ceiling -6)" % peak_db)

        # No holes at joints: room tone must carry through every one.
        env, hop = vslib.rms_envelope(samples, 48000, hop_ms=5.0, win_ms=15.0)
        worst_hole, worst_at = 0.0, None
        for s in segs[:-1]:
            c = int(s["out_out"] / hop)
            lo, hi = max(0, c - 8), min(len(env), c + 8)
            floor_here = float(env[lo:hi].min())
            if floor_here < worst_hole or worst_at is None:
                worst_hole, worst_at = floor_here, s["out_out"]
        check("no fade-to-zero at any joint", worst_hole > -70.0,
              "quietest joint %.1f dBFS at %s" % (worst_hole, vslib.tc(worst_at or 0)))

        # Clicks: reuse the shipped QA pass, in strict mode.
        qa = subprocess.run(
            ["uv", "run", "--quiet",
             os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio_qa.py"),
             "--job-dir", a.job_dir, "--media", master,
             "--spliced", os.path.join(a.job_dir, "cut", "%s.spliced.mkv" % name),
             "--strict"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        check("audio QA passes in strict mode", qa.returncode == 0,
              qa.stderr.decode("utf-8", "replace").strip().splitlines()[-1][:60]
              if qa.returncode else "")

    # ---- 6. handoff --------------------------------------------------------
    for rel in ("cut/%s.fcp7.xml" % name, "cut/%s.edl" % name,
                "cut/%s.capcut/draft_content.json" % name, "cut/%s.cuts.md" % name,
                "outputs/%s.srt" % name, "outputs/%s.script.md" % name):
        check("wrote %s" % rel, os.path.exists(os.path.join(a.job_dir, rel)))

    xml = open(os.path.join(a.job_dir, "cut", "%s.fcp7.xml" % name), encoding="utf-8").read()
    check("XML carries one clip per cut, not one flat clip",
          xml.count("<clipitem") == len(segs) * 2,
          "%d clipitems for %d cuts (video + audio)" % (xml.count("<clipitem"), len(segs)))

    import xml.etree.ElementTree as ET
    try:
        ET.fromstring(xml)
        check("XML is well-formed", True)
    except ET.ParseError as exc:
        check("XML is well-formed", False, str(exc))

    # ---- 7. nothing re-transcribed ----------------------------------------
    check("canonical transcript derived from the one words.json",
          tr["derived_from"]["raw_sha256"] == cut["source"]["sha256"]
          and tr["derived_from"]["words"] == "transcript/words.json")

    print("", file=sys.stderr)
    if FAILURES:
        print("  %s%d passed, %d FAILED%s: %s"
              % (vslib._R, len(PASSES), len(FAILURES), vslib._O, ", ".join(FAILURES)),
              file=sys.stderr)
        sys.exit(1)
    print("  %sall %d checks passed%s" % (vslib._G, len(PASSES), vslib._O), file=sys.stderr)


if __name__ == "__main__":
    main()
