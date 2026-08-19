#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""graphics_plan.py - pipeline step 3a. Plan the graphics beat by beat.

Plan first, build second. The plan is a markdown beat sheet you can argue with
in thirty seconds; the build is HTML that takes minutes to render. Getting the
order wrong is how you end up re-rendering a whole video to move one word.

Reads the canonical transcript (never re-transcribing) and proposes one beat per
sentence-ish unit, with the timings already in cut-relative time. You then edit
hf-graphics/timeline.json - change kinds, text, drop beats - and run
hf_build_parts.py.

LOCK: short-form safe zones. On 1080x1920 nothing that matters goes in the top
200 px or the bottom 300 px - that is where the platform chrome, the handle and
the caption stack live. Face, captions and graphics stay inside y 200-1620.
"""
import argparse
import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vslib  # noqa: E402

SCHEMA = "video-system/graphics-timeline@1"

CANVAS = {
    "short": {"w": 1080, "h": 1920, "safe_top": 200, "safe_bottom": 300},
    "long":  {"w": 1920, "h": 1080, "safe_top": 60,  "safe_bottom": 60},
}

MIN_BEAT = 1.2          # anything shorter reads as a flicker
MAX_BEAT = 5.0
LEAD = 0.12             # a graphic lands just after the word that earns it


def beat_kind(i, n, text, fmt):
    if i == 0:
        return "title"
    if i == n - 1:
        return "endcard"
    words = len(text.split())
    if words <= 5:
        return "kicker"
    if fmt == "short":
        return "callout"
    return "lower-third"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--job-dir", required=True)
    ap.add_argument("--preset", default=None)
    ap.add_argument("--part-target", type=float, default=None)
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()

    job = vslib.read_json(os.path.join(a.job_dir, "job.json"))
    name, fmt = job["name"], job.get("format", "short")
    tpath = os.path.join(a.job_dir, "outputs", "%s.transcript.json" % name)
    if not os.path.exists(tpath):
        vslib.die("no canonical transcript - run rough_cut.sh first "
                  "(graphics are planned against the cut, not the raw)")
    tr = vslib.read_json(tpath)

    out_json = os.path.join(a.job_dir, "hf-graphics", "timeline.json")
    if os.path.exists(out_json) and not a.force:
        vslib.warn("hf-graphics/timeline.json exists - keeping your edits; --force to regenerate")
        existing = vslib.read_json(out_json)
        vslib.ok("%d beats already planned" % len(existing.get("beats", [])))
        return

    canvas = dict(CANVAS[fmt])
    preset = a.preset or ("short-form-punch" if fmt == "short" else "long-form-clean")
    # Long-form gets longer parts: fewer seams, still small enough that one tweak
    # is one re-render.
    part_target = a.part_target or (15.0 if fmt == "short" else 25.0)

    sentences = tr["segments"]
    beats = []
    for i, seg in enumerate(sentences):
        dur = min(MAX_BEAT, max(MIN_BEAT, seg["e"] - seg["s"]))
        t = round(max(0.0, seg["s"] + LEAD), 3)
        if t + dur > tr["duration"]:
            dur = round(max(0.4, tr["duration"] - t), 3)
        text = seg["text"].strip().rstrip(".,")
        # A graphic is a headline, not a subtitle. The sentence it came from is
        # already being spoken; the beat only has to name it.
        limit = 40 if beat_kind(i, len(sentences), text, fmt) in ("title", "kicker", "endcard") else 64
        beats.append({
            "id": "b%02d" % (i + 1),
            "t": t,
            "dur": round(dur, 3),
            "kind": beat_kind(i, len(sentences), text, fmt),
            "text": text if len(text) <= limit else text[:limit - 3].rsplit(" ", 1)[0] + "...",
            "sub": "",
            "anchor": "lower" if fmt == "short" else "lower-left",
            "enabled": i == 0 or i == len(sentences) - 1 or len(text.split()) <= 8,
            "words": seg["words"][:1] + seg["words"][-1:],
        })

    # Seams: the only places a part boundary may fall. A part must never split a
    # beat, or the two halves animate out of phase and the join shows.
    seams = [0.0]
    for i in range(len(beats) - 1):
        end = beats[i]["t"] + beats[i]["dur"]
        nxt = beats[i + 1]["t"]
        if nxt - end >= 0.15:
            seams.append(round((end + nxt) / 2.0, 3))
    seams.append(round(tr["duration"], 3))

    timeline = {
        "schema": SCHEMA,
        "created": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "job": name,
        "title": job.get("title"),
        "format": fmt,
        "preset": preset,
        "canvas": canvas,
        "fps": tr["fps"],
        "duration": tr["duration"],
        "part_target": part_target,
        "derived_from": "outputs/%s.transcript.json" % name,
        "seams": seams,
        "beats": beats,
    }
    vslib.write_json(out_json, timeline)

    # ---- the beat sheet ---------------------------------------------------
    on = [b for b in beats if b["enabled"]]
    L = [
        "# %s - graphics plan" % (job.get("title") or name),
        "",
        "%s, %s canvas %dx%d, preset `%s`."
        % (vslib.tc(tr["duration"]),
           "9:16 short-form" if fmt == "short" else "16:9 long-form",
           canvas["w"], canvas["h"], preset),
        "",
        "Plan first. Every row below is a proposal - flip `enabled`, rewrite `text`,",
        "change `kind`, or delete beats in `hf-graphics/timeline.json`, then build.",
        "",
        "**Safe zone:** nothing that matters above y=%d or below y=%d."
        % (canvas["safe_top"], canvas["h"] - canvas["safe_bottom"]),
        "" if fmt != "short" else
        "Face, captions and graphics all live inside y 200-1620 on 1080x1920.",
        "",
        "| beat | in | out | kind | on | text |",
        "|---|---|---|---|:-:|---|",
    ]
    for b in beats:
        L.append("| `%s` | %s | %s | %s | %s | %s |"
                 % (b["id"], vslib.tc(b["t"]), vslib.tc(b["t"] + b["dur"]),
                    b["kind"], "x" if b["enabled"] else " ", b["text"]))
    L += [
        "",
        "## Parts",
        "",
        "%d candidate seam(s); parts target %.0fs each."
        % (len(seams) - 2, part_target),
        "",
        "A part is a self-contained slice of ONE shared timeline. Re-rendering",
        "part 3 after a note costs one part, not the whole video, and the joins",
        "are frame-exact because every part reads the same `timeline.json`.",
        "",
        "Build:  `workflows/scripts/hf_build_parts.py --job-dir . `  (via hf_build.sh)",
        "Render: `workflows/scripts/hf_render.sh %s part-02`" % name,
        "",
    ]
    with open(os.path.join(a.job_dir, "hf-graphics", "PLAN.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(L))

    job["stage"] = "graphics"
    job.setdefault("graphics", {})
    job["graphics"] = {"timeline": "hf-graphics/timeline.json", "plan": "hf-graphics/PLAN.md",
                       "preset": preset, "beats": len(beats), "enabled": len(on)}
    vslib.write_json(os.path.join(a.job_dir, "job.json"), job)

    vslib.ok("hf-graphics/PLAN.md  %d beats, %d on by default" % (len(beats), len(on)))
    vslib.ok("hf-graphics/timeline.json  %d seam(s), parts target %.0fs"
             % (len(seams) - 2, part_target))
    vslib.dim("edit the plan, then: workflows/scripts/hf_build.sh %s" % name)


if __name__ == "__main__":
    main()
