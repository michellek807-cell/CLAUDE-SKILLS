#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""intake_probe.py - probe the ingested raw file once and record it in job.json.

Every later step reads fps/duration/geometry from here instead of re-probing,
so the whole job agrees on one frame grid.
"""
import argparse
import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vslib  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--job-dir", required=True)
    ap.add_argument("--raw", required=True)
    ap.add_argument("--source", required=True)
    a = ap.parse_args()

    job_path = os.path.join(a.job_dir, "job.json")
    job = vslib.read_json(job_path)

    info = vslib.probe_media(a.raw)
    if not info["has_video"]:
        vslib.warn("no video stream - audio-only job")
    if not info["has_audio"]:
        vslib.die("no audio stream: the rough cut is driven by speech, there is nothing to cut on")

    job["raw"] = {
        "file": os.path.relpath(a.raw, a.job_dir),
        "ingested_from": a.source,
        "ingested_at": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sha256": vslib.sha256_file(a.raw),
        "duration": round(info["duration"], 3),
        "fps": info.get("fps"),
        "width": info.get("width"),
        "height": info.get("height"),
        "vcodec": info.get("vcodec"),
        "acodec": info.get("acodec"),
        "sample_rate": info.get("sample_rate"),
        "channels": info.get("channels"),
    }
    job["stage"] = "intake"

    # Format is a claim about the delivery frame, so sanity-check it against the
    # source. Vertical source with format:long is nearly always a mistake.
    w, h = info.get("width") or 0, info.get("height") or 0
    if w and h:
        src_vertical = h > w
        if job.get("format") == "long" and src_vertical:
            vslib.warn("source is vertical (%dx%d) but format is 'long' (16:9)" % (w, h))
        if job.get("format") == "short" and not src_vertical:
            vslib.dim("source is %dx%d; short-form delivers 1080x1920, reframing happens at export" % (w, h))

    vslib.write_json(job_path, job)
    fps = info.get("fps", "n/a")
    vslib.ok("probed: %s  %sx%s  %s fps  %s"
             % (vslib.tc(info["duration"]), w, h, fps, info.get("vcodec")))
    if info.get("sample_rate"):
        vslib.dim("audio: %s ch @ %s Hz (%s)"
                  % (info.get("channels"), info.get("sample_rate"), info.get("acodec")))


if __name__ == "__main__":
    main()
