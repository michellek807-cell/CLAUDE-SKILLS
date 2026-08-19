#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""captions_build.py - pipeline step 5. Captions, short-form only.

LOCK: built from the canonical transcript, never re-transcribed. Those word
timings came out of the single WhisperX pass and were remapped through the cut
list. Running a second model over the rendered file would produce a second,
disagreeing truth, and the two would drift apart with every re-cut.

LOCK: rendered as parts from one shared timeline, same as the graphics, so a
fixed typo re-renders one part.

LOCK: safe zones. The caption stack lives inside y 200-1620 on 1080x1920, and
the box is asserted, not assumed.

Also writes a word-level .srt next to the canonical transcript, because every
platform wants one and nobody should be generating it a second way.
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


MAX_CARD_GAP = 0.45      # a pause this long ends the card
MAX_CARD_SPAN = 2.6
HIGHLIGHT_MIN_LEN = 5    # only lift words worth lifting


def load_preset(root, name):
    path = os.path.join(root, "presets", name, "build.py")
    spec = importlib.util.spec_from_file_location("preset_cap", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if not hasattr(mod, "caption_card"):
        vslib.die("preset '%s' has no caption_card() - captions need a short-form preset" % name)
    return mod


def make_cards(words, per_card):
    cards, cur = [], []
    for w in words:
        if cur:
            gap = w["s"] - cur[-1]["e"]
            span = w["e"] - cur[0]["s"]
            if len(cur) >= per_card or gap > MAX_CARD_GAP or span > MAX_CARD_SPAN:
                cards.append(cur)
                cur = []
        cur.append(w)
    if cur:
        cards.append(cur)
    return cards


def highlight_index(card):
    """One highlight per card at most: the longest word, if it earns it."""
    best, best_i = 0, None
    for i, w in enumerate(card):
        core = vslib.normalize_token(w["w"])
        if len(core) > best and len(core) >= HIGHLIGHT_MIN_LEN:
            best, best_i = len(core), i
    return best_i


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--job-dir", required=True)
    ap.add_argument("--root", required=True)
    ap.add_argument("--per-card", type=int, default=None)
    ap.add_argument("--force-long", action="store_true",
                    help="build captions for a 16:9 job anyway")
    a = ap.parse_args()

    job = vslib.read_json(os.path.join(a.job_dir, "job.json"))
    name, fmt = job["name"], job.get("format", "short")
    if fmt != "short" and not a.force_long:
        vslib.warn("captions are short-form only; this job is 16:9. "
                   "Pass --force-long if you really want them.")
        return

    tpath = os.path.join(a.job_dir, "outputs", "%s.transcript.json" % name)
    if not os.path.exists(tpath):
        vslib.die("no canonical transcript - captions are derived from it, never re-transcribed")
    tr = vslib.read_json(tpath)

    gtl_path = os.path.join(a.job_dir, "hf-graphics", "timeline.json")
    if os.path.exists(gtl_path):
        gtl = vslib.read_json(gtl_path)
        canvas, preset_name, part_target = gtl["canvas"], gtl["preset"], gtl["part_target"]
    else:
        canvas = {"w": 1080, "h": 1920, "safe_top": 200, "safe_bottom": 300}
        preset_name, part_target = "short-form-punch", 15.0
    # Caption parts are shorter than graphics parts on purpose. A caption part
    # is what you re-render to fix one word, so it should be cheap; 13 cards on
    # one track is also more timeline than anyone wants to read.
    part_target = min(part_target, 10.0)
    preset = load_preset(a.root, preset_name)
    per_card = a.per_card or getattr(preset, "CAPTION", {}).get("words_per_card", 4)

    words = tr["words"]
    cards = make_cards(words, per_card)
    for c in cards:
        hi = highlight_index(c)
        for i, w in enumerate(c):
            w["_hi"] = (i == hi)
    vslib.step("captions: %d cards from %d words (max %d per card)"
               % (len(cards), len(words), per_card))

    # ---- slice into parts on gaps between cards ---------------------------
    duration = tr["duration"]
    bounds = [0.0]
    for i in range(len(cards) - 1):
        seam = round((cards[i][-1]["e"] + cards[i + 1][0]["s"]) / 2.0, 3)
        if seam - bounds[-1] >= part_target:
            bounds.append(seam)
    bounds.append(round(duration, 3))
    if len(bounds) > 2 and bounds[-1] - bounds[-2] < part_target * 0.5:
        del bounds[-2]

    cdir = os.path.join(a.job_dir, "hf-graphics", "captions")
    shared = os.path.join(cdir, "shared")
    os.makedirs(shared, exist_ok=True)
    css_text = ("/* generated from presets/%s/build.py - edit the preset */\n" % preset_name)
    css_text += preset.css(canvas) + preset.caption_css(canvas)
    with open(os.path.join(shared, "captions.css"), "w", encoding="utf-8") as fh:
        fh.write(css_text)

    parts_dir = os.path.join(cdir, "parts")
    manifest_parts, violations = [], []
    for pi in range(len(bounds) - 1):
        t0, t1 = bounds[pi], bounds[pi + 1]
        comp = "part-%02d" % (pi + 1)
        mine = [c for c in cards if c[0]["s"] < t1 - 1e-6 and c[-1]["e"] > t0 + 1e-6]
        bodies, scripts = [], []
        # One caption on screen at a time. Each card's hold is clamped to the
        # next card's entry, otherwise the tails overlap on the same track and
        # the renderer has two clips fighting for the same frames.
        for ci, card in enumerate(mine):
            card_in = max(0.0, round(card[0]["s"] - t0 - 0.06, 3))
            card_out = min(round(t1 - t0, 3), round(card[-1]["e"] - t0 + 0.22, 3))
            if ci + 1 < len(mine):
                next_in = max(0.0, round(mine[ci + 1][0]["s"] - t0 - 0.06, 3))
                card_out = min(card_out, round(next_in - 0.001, 3))
            card_out = max(card_out, card_in + 0.25)
            uid = "%s-c%02d" % (comp, ci)
            built = preset.caption_card(
                [{"text": w["w"], "s": w["s"] - t0, "hi": w["_hi"]} for w in card],
                canvas, uid, card_in)
            top, bottom = built["box"]
            if top < canvas["safe_top"] or bottom > canvas["h"] - canvas["safe_bottom"]:
                violations.append("%s: caption box y %d-%d outside safe band %d-%d"
                                  % (uid, top, bottom, canvas["safe_top"],
                                     canvas["h"] - canvas["safe_bottom"]))
            bodies.append('    <section id="%s-clip" class="clip" data-start="%.3f" '
                          'data-duration="%.3f" data-track-index="1">\n'
                          '      <div class="safe">%s</div>\n    </section>'
                          % (uid, card_in, max(0.25, card_out - card_in), built["html"]))
            scripts.append("      // card %d\n      %s" % (ci, built["js"]))

        pdir = os.path.join(parts_dir, comp)
        os.makedirs(os.path.join(pdir, "shared"), exist_ok=True)
        ensure_gsap(a.root, os.path.join(pdir, "shared"))
        with open(os.path.join(pdir, "shared", "captions.css"), "w", encoding="utf-8") as fh:
            fh.write(css_text)
        html = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=%(w)d, height=%(h)d" />
    <title>%(job)s captions &mdash; %(comp)s</title>
    <script src="%(gsap)s"></script>
    <link rel="stylesheet" href="shared/captions.css" />
  </head>
  <body>
    <!-- Generated by workflows/scripts/captions_build.py from
         outputs/%(job)s.transcript.json. Never re-transcribed. Do not hand-edit:
         fix transcript/corrections.txt and rebuild. -->
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
""" % dict(w=canvas["w"], h=canvas["h"], job=name, comp=comp, gsap=GSAP,
           dur=round(t1 - t0, 3), fps=tr["fps"],
           body="\n".join(bodies), script="\n".join(scripts))
        with open(os.path.join(pdir, "index.html"), "w", encoding="utf-8") as fh:
            fh.write(html)
        manifest_parts.append({"i": pi + 1, "id": comp, "t0": t0, "t1": t1,
                               "dur": round(t1 - t0, 3), "cards": len(mine),
                               "path": "parts/%s/index.html" % comp})
        vslib.ok("captions %s  %6.2f-%6.2fs  %d card(s)" % (comp, t0, t1, len(mine)))

    if os.path.isdir(parts_dir):
        keep = set(p["id"] for p in manifest_parts)
        for entry in sorted(os.listdir(parts_dir)):
            if entry.startswith("part-") and entry not in keep:
                shutil.rmtree(os.path.join(parts_dir, entry))

    vslib.write_json(os.path.join(cdir, "parts.json"), {
        "schema": "video-system/caption-parts@1",
        "job": name, "preset": preset_name, "canvas": canvas, "fps": tr["fps"],
        "duration": duration, "words_per_card": per_card,
        "derived_from": "outputs/%s.transcript.json" % name,
        "parts": manifest_parts,
    })

    # ---- word-level srt, same source ---------------------------------------
    srt = []
    for i, card in enumerate(cards, 1):
        def ts(t):
            ms = int(round(t * 1000)); h, ms = divmod(ms, 3600000)
            m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
            return "%02d:%02d:%02d,%03d" % (h, m, s, ms)
        srt += [str(i), "%s --> %s" % (ts(card[0]["s"]), ts(card[-1]["e"])),
                " ".join(w["w"] for w in card), ""]
    with open(os.path.join(a.job_dir, "outputs", "%s.captions.srt" % name),
              "w", encoding="utf-8") as fh:
        fh.write("\n".join(srt))

    if violations:
        for v in violations:
            vslib.warn(v)
        vslib.die("short-form safe zones are not advisory - move CAPTION['y'] in the preset")

    job["stage"] = "captioned"
    job.setdefault("outputs", {})["captions_srt"] = "outputs/%s.captions.srt" % name
    job.setdefault("captions", {})
    job["captions"] = {"parts": len(manifest_parts), "cards": len(cards),
                       "manifest": "hf-graphics/captions/parts.json"}
    vslib.write_json(os.path.join(a.job_dir, "job.json"), job)

    vslib.ok("hf-graphics/captions/  %d part(s), %d card(s)" % (len(manifest_parts), len(cards)))
    vslib.ok("outputs/%s.captions.srt" % name)
    vslib.dim("render: workflows/scripts/captions.sh %s --render" % name)


if __name__ == "__main__":
    main()
