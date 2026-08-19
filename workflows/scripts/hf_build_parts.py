#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""hf_build_parts.py - pipeline step 3b. Build the graphics as re-renderable parts.

LOCK: long graphics render as short seamless parts from ONE shared timeline.
hf-graphics/timeline.json holds every beat in absolute cut-relative time. This
slices it at pre-computed seams - gaps where no beat is in flight - and writes
one standalone HyperFrames composition per slice. A note on part 3 costs one
re-render of part 3; the joins stay frame-exact because nothing was re-timed,
only re-sliced.

LOCK: safe zones. Every box the preset returns is asserted against the canvas
safe band. A beat that drifts out fails the build, not the phone.

The HyperFrames composition contract (root data-composition-id / data-start /
data-width / data-height, one paused GSAP timeline on window.__timelines) has
been mandatory since 0.7.42 - a root missing data-start does not warn, the
render capture dies. It is emitted here, never hand-written.
"""
import argparse
import importlib.util
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vslib  # noqa: E402

GSAP = "shared/gsap.min.js"

GSAP_VERSION = "3.14.2"


def ensure_gsap(root, shared_dir):
    """Put GSAP next to the composition instead of trusting a CDN at render time.

    A composition that loads gsap over the network is a composition that renders
    silently wrong the day the network says no: the capture still runs, every
    tween is missing, and the only sign is a `sub_timeline_script_failure`
    warning buried in the log. Vendored once into workflows/vendor/, copied into
    each job. Refresh it with:  npm pack gsap@<version>
    """
    src = os.path.join(root, "workflows", "vendor", "gsap.min.js")
    if not os.path.exists(src):
        vslib.die("no workflows/vendor/gsap.min.js - run: workflows/scripts/vendor_gsap.sh")
    dst = os.path.join(shared_dir, "gsap.min.js")
    if not os.path.exists(dst) or os.path.getsize(dst) != os.path.getsize(src):
        shutil.copyfile(src, dst)
    return "gsap.min.js"



def load_preset(root, name):
    path = os.path.join(root, "presets", name, "build.py")
    if not os.path.exists(path):
        vslib.die("no preset at presets/%s/build.py" % name)
    spec = importlib.util.spec_from_file_location("preset_%s" % name.replace("-", "_"), path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def slice_parts(beats, seams, duration, target):
    """Choose part boundaries: seams only, as close to `target` as possible."""
    bounds = [0.0]
    for seam in seams:
        if seam <= bounds[-1] + 1e-6 or seam >= duration - 0.05:
            continue
        if seam - bounds[-1] >= target:
            bounds.append(seam)
    bounds.append(round(duration, 3))
    # A runt tail part is all overhead and no benefit: fold it back.
    if len(bounds) > 2 and bounds[-1] - bounds[-2] < target * 0.5:
        del bounds[-2]

    parts = []
    for i in range(len(bounds) - 1):
        t0, t1 = bounds[i], bounds[i + 1]
        inside = [b for b in beats
                  if b.get("enabled", True) and b["t"] < t1 - 1e-6 and b["t"] + b["dur"] > t0 + 1e-6]
        straddlers = [b["id"] for b in inside if b["t"] < t0 - 1e-6 or b["t"] + b["dur"] > t1 + 1e-6]
        parts.append({"i": i + 1, "t0": round(t0, 3), "t1": round(t1, 3),
                      "dur": round(t1 - t0, 3), "beats": inside, "straddlers": straddlers})
    return parts


def render_part_html(part, timeline, preset, fps):
    canvas = timeline["canvas"]
    comp_id = "part-%02d" % part["i"]
    bodies, scripts, violations = [], [], []

    for b in part["beats"]:
        # A beat that straddles a seam is clamped to this part's window. Its
        # neighbour part clamps the other half, so the two halves meet exactly.
        local_in = max(0.0, round(b["t"] - part["t0"], 3))
        local_out = min(part["dur"], round(b["t"] + b["dur"] - part["t0"], 3))
        span = max(0.2, round(local_out - local_in, 3))

        beat = dict(b)
        beat["_local"] = local_in        # tween times are part-timeline times
        beat["dur"] = span
        uid = "%s-%s" % (comp_id, b["id"])
        built = preset.beat(beat, canvas, uid)

        top, bottom = built["box"]
        if top < canvas["safe_top"] or bottom > canvas["h"] - canvas["safe_bottom"]:
            violations.append("%s: y %d-%d is outside the safe band %d-%d"
                              % (b["id"], top, bottom, canvas["safe_top"],
                                 canvas["h"] - canvas["safe_bottom"]))

        bodies.append(
            '    <section id="%s-clip" class="clip" data-start="%.3f" data-duration="%.3f" '
            'data-track-index="%d">\n'
            '      <div class="safe">%s</div>\n'
            "    </section>"
            % (uid, local_in, span, 1 + (b["_track"] % 4), built["html"]))
        scripts.append("      // %s  %s @ %.2fs\n      %s"
                       % (b["id"], b.get("kind", ""), local_in, built["js"]))

    body = "\n".join(bodies)
    script = "\n".join(scripts)

    html = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=%(w)d, height=%(h)d" />
    <title>%(title)s &mdash; %(comp)s</title>
    <script src="%(gsap)s"></script>
    <link rel="stylesheet" href="shared/preset.css" />
  </head>
  <body>
    <!-- Generated by workflows/scripts/hf_build_parts.py from ../../timeline.json.
         Do not hand-edit: change timeline.json or the preset and rebuild.
         Part %(i)d of one shared timeline, covering %(t0).3f-%(t1).3f s. -->
    <div
      id="root"
      data-composition-id="%(comp)s"
      data-start="0"
      data-width="%(w)d"
      data-height="%(h)d"
      data-duration="%(dur).3f"
      data-fps="%(fps)s"
    >
%(body)s
    </div>
    <script>
      window.__timelines = window.__timelines || {};
      const tl = gsap.timeline({ paused: true });
%(script)s
      window.__timelines["%(comp)s"] = tl;
    </script>
  </body>
</html>
""" % dict(w=canvas["w"], h=canvas["h"],
           title=vslib._esc_title(timeline.get("title") or timeline["job"]),
           comp=comp_id, gsap=GSAP, i=part["i"], t0=part["t0"], t1=part["t1"],
           dur=part["dur"], fps=fps, body=body, script=script)
    return html, violations


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--job-dir", required=True)
    ap.add_argument("--root", required=True)
    ap.add_argument("--strict-safe", action="store_true",
                    help="fail the build on a safe-zone violation (default for short-form)")
    a = ap.parse_args()

    gdir = os.path.join(a.job_dir, "hf-graphics")
    tl_path = os.path.join(gdir, "timeline.json")
    if not os.path.exists(tl_path):
        vslib.die("no hf-graphics/timeline.json - run graphics_plan.py first (plan, then build)")
    timeline = vslib.read_json(tl_path)
    preset = load_preset(a.root, timeline["preset"])
    canvas = timeline["canvas"]
    fps = timeline.get("fps", "30")

    for i, b in enumerate(timeline["beats"]):
        b["_track"] = i

    parts = slice_parts(timeline["beats"], timeline["seams"], timeline["duration"],
                        timeline["part_target"])

    vslib.step("building %d part(s) from one shared timeline" % len(parts))

    # Reference copy of the generated CSS, for reading. Each part gets its own.
    shared = os.path.join(gdir, "shared")
    os.makedirs(shared, exist_ok=True)
    css_text = ("/* %s - generated from presets/%s/build.py. Edit the preset, not this. */\n"
                % (preset.NAME, timeline["preset"])) + preset.css(canvas)
    with open(os.path.join(shared, "preset.css"), "w", encoding="utf-8") as fh:
        fh.write(css_text)

    parts_dir = os.path.join(gdir, "parts")
    all_violations = []
    written = []
    for part in parts:
        pdir = os.path.join(parts_dir, "part-%02d" % part["i"])
        # A part is a self-contained HyperFrames project: its own root, its own
        # assets, root-relative paths. That is what lets one part re-render on
        # its own, and it keeps `check` and `render` resolving the same URLs.
        os.makedirs(os.path.join(pdir, "shared"), exist_ok=True)
        ensure_gsap(a.root, os.path.join(pdir, "shared"))
        with open(os.path.join(pdir, "shared", "preset.css"), "w", encoding="utf-8") as fh:
            fh.write(css_text)
        html, violations = render_part_html(part, timeline, preset, fps)
        all_violations += violations
        with open(os.path.join(pdir, "index.html"), "w", encoding="utf-8") as fh:
            fh.write(html)
        written.append(part)
        note = ""
        if part["straddlers"]:
            note = "  (holds %s across the seam)" % ", ".join(part["straddlers"])
        vslib.ok("part-%02d  %6.2f-%6.2fs  %2d beat(s)%s"
                 % (part["i"], part["t0"], part["t1"], len(part["beats"]), note))

    # Drop parts left over from a previous, longer build.
    if os.path.isdir(parts_dir):
        keep = set("part-%02d" % p["i"] for p in written)
        for entry in sorted(os.listdir(parts_dir)):
            if entry.startswith("part-") and entry not in keep:
                shutil.rmtree(os.path.join(parts_dir, entry))
                vslib.dim("removed stale %s" % entry)

    manifest = {
        "schema": "video-system/graphics-parts@1",
        "job": timeline["job"],
        "preset": timeline["preset"],
        "canvas": canvas,
        "fps": fps,
        "duration": timeline["duration"],
        "parts": [{"i": p["i"], "id": "part-%02d" % p["i"], "t0": p["t0"], "t1": p["t1"],
                   "dur": p["dur"], "beats": [b["id"] for b in p["beats"]],
                   "path": "parts/part-%02d/index.html" % p["i"]} for p in written],
    }
    vslib.write_json(os.path.join(gdir, "parts.json"), manifest)

    if all_violations:
        vslib.warn("safe-zone violations (%dx%d, band y %d-%d):"
                   % (canvas["w"], canvas["h"], canvas["safe_top"],
                      canvas["h"] - canvas["safe_bottom"]))
        for v in all_violations:
            vslib.warn("    " + v)
        if a.strict_safe or timeline.get("format") == "short":
            vslib.die("short-form safe zones are not advisory - fix the preset or the beat")

    vslib.ok("hf-graphics/parts.json  %d part(s), %.1fs total"
             % (len(written), timeline["duration"]))
    vslib.dim("render one: workflows/scripts/hf_render.sh %s part-01" % timeline["job"])


if __name__ == "__main__":
    main()
