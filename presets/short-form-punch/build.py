"""short-form-punch - locked look for 9:16 short-form graphics.

Imported by workflows/scripts/hf_build_parts.py. Everything visual about this
format lives here and in spec.md next to it; the builder only slices time.

LOCK: safe zones. On 1080x1920 the top 200 px and the bottom 300 px belong to
the platform - handle, follow button, caption stack, progress bar. Nothing that
carries meaning goes there. Every box this module returns is asserted against
that band by the builder, so a hand edit that drifts out gets caught at build
time instead of on the phone.
"""

NAME = "short-form-punch"
FORMAT = "short"
CANVAS = {"w": 1080, "h": 1920, "safe_top": 200, "safe_bottom": 300}

TOKENS = {
    "ink": "#ffffff",
    "ink_dim": "rgba(255,255,255,0.72)",
    "accent": "#f5c451",
    "warn": "#e2564b",
    "card": "rgba(12,10,14,0.82)",
    "edge": "rgba(255,255,255,0.14)",
    "display": '"Archivo Black","Inter",system-ui,sans-serif',
    "body": '"Inter",system-ui,sans-serif',
}

# Vertical anchors, all inside y 200-1620.
ANCHOR_Y = {"upper": 380, "center": 820, "lower": 1180, "low": 1360}


def css(canvas):
    t = TOKENS
    return """
:root {
  --ink: %(ink)s; --ink-dim: %(ink_dim)s; --accent: %(accent)s;
  --warn: %(warn)s; --card: %(card)s; --edge: %(edge)s;
}
html, body { margin: 0; background: transparent; }
#root { position: relative; width: %(w)dpx; height: %(h)dpx; overflow: hidden;
        background: transparent; font-family: %(body)s; color: var(--ink); }
.clip { position: absolute; inset: 0; }

/* The safe band. Every beat box is laid out inside this element, so drift is
   structurally impossible rather than merely discouraged. */
.safe { position: absolute; left: 0; right: 0;
        top: %(safe_top)dpx; bottom: %(safe_bottom)dpx; }

.stack { position: absolute; left: 72px; right: 72px; }
.stack.upper  { top: %(upper)dpx; }
.stack.center { top: %(center)dpx; }
.stack.lower  { top: %(lower)dpx; }
.stack.low    { top: %(low)dpx; }

.scrim { position: absolute; left: -72px; right: -72px; top: -48px; bottom: -48px;
         background: radial-gradient(120%% 90%% at 50%% 50%%, rgba(0,0,0,0.62), rgba(0,0,0,0));
         border-radius: 64px; }

.headline { position: relative; margin: 0; font-family: %(display)s;
            font-size: 104px; line-height: 1.02; letter-spacing: -0.02em;
            text-transform: uppercase; text-wrap: balance;
            text-shadow: 0 6px 40px rgba(0,0,0,0.55); }
.headline.sm { font-size: 78px; }
.headline.xs { font-size: 62px; }
.headline .hi { color: var(--accent); }

.kicker.sm { font-size: 62px; }
.kicker.xs { font-size: 52px; }
.kicker { position: relative; margin: 0; font-family: %(display)s;
          font-size: 72px; line-height: 1.06; text-align: center;
          text-transform: uppercase; letter-spacing: -0.01em;
          text-shadow: 0 6px 34px rgba(0,0,0,0.6); }

.card { position: relative; display: block; padding: 40px 48px;
        background: var(--card); border: 2px solid var(--edge);
        border-radius: 36px; backdrop-filter: blur(14px); }
.card .label { display: block; margin: 0 0 14px 0; font-family: %(display)s;
               font-size: 30px; letter-spacing: 0.16em; text-transform: uppercase;
               color: var(--accent); }
.card .body { display: block; margin: 0; font-size: 50px; line-height: 1.24;
              font-weight: 600; color: var(--ink); }

.rule { position: relative; display: block; height: 10px; width: 180px;
        margin: 0 0 26px 0; border-radius: 6px; background: var(--accent); }
.sub { position: relative; display: block; margin: 22px 0 0 0; font-size: 38px;
       line-height: 1.3; color: var(--ink-dim); }
""" % dict(t, w=canvas["w"], h=canvas["h"],
           safe_top=canvas["safe_top"], safe_bottom=canvas["safe_bottom"],
           upper=ANCHOR_Y["upper"] - canvas["safe_top"],
           center=ANCHOR_Y["center"] - canvas["safe_top"],
           lower=ANCHOR_Y["lower"] - canvas["safe_top"],
           low=ANCHOR_Y["low"] - canvas["safe_top"])


def _esc(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _lines(text, chars_per_line):
    """Rough line count. Deliberately pessimistic: over-estimating costs a
    slightly smaller box, under-estimating costs a graphic in the keep-out."""
    words, line, n = text.split(), 0, 1
    for w in words:
        if line and line + 1 + len(w) > chars_per_line:
            n += 1
            line = len(w)
        else:
            line += (1 if line else 0) + len(w)
    return n


def _fit(text, sizes, chars_per_line):
    """Step the type down until the headline fits in three lines."""
    for px, cpl, cls in zip(sizes, chars_per_line, ("", " sm", " xs")):
        if _lines(text, cpl) <= 3:
            return cls, px
    return " xs", sizes[-1]


def _emphasise(text):
    """Lift the last word into the accent colour. One highlight, never two."""
    parts = _esc(text).rsplit(" ", 1)
    if len(parts) == 1:
        return parts[0]
    return '%s <span class="hi">%s</span>' % (parts[0], parts[1])


def beat(b, canvas, uid):
    """Return {html, js, box} for one beat. `uid` is unique across the page."""
    kind = b.get("kind", "kicker")
    anchor = {"title": "center", "endcard": "center", "kicker": "lower",
              "callout": "lower", "lower-third": "low"}.get(kind, "lower")
    text = b.get("text", "")
    sub = b.get("sub", "")

    if kind in ("title", "endcard"):
        size_cls, px = _fit(text, (104, 78, 62), chars_per_line=(11, 15, 19))
        lines = _lines(text, {104: 11, 78: 15, 62: 19}[px])
        inner = ('<div class="scrim"></div>'
                 '<h1 id="%s-h" class="headline%s">%s</h1>'
                 % (uid, size_cls, _emphasise(text)))
        height = int(lines * px * 1.02) + 40
        if sub:
            inner += '<span id="%s-s" class="sub">%s</span>' % (uid, _esc(sub))
            height += 80
    elif kind == "kicker":
        size_cls, px = _fit(text, (72, 62, 52), chars_per_line=(16, 19, 23))
        lines = _lines(text, {72: 16, 62: 19, 52: 23}[px])
        inner = ('<div class="scrim"></div>'
                 '<h2 id="%s-h" class="kicker%s">%s</h2>'
                 % (uid, size_cls.replace("headline", "kicker"), _emphasise(text)))
        height = int(lines * px * 1.06) + 40
    else:  # callout / lower-third
        inner = ('<div id="%s-c" class="card">'
                 '<span class="label">%s</span>'
                 '<span class="body">%s</span></div>'
                 % (uid, _esc(b.get("label") or kind.replace("-", " ")), _esc(text)))
        height = 260

    html = ('<div id="%s" class="stack %s">%s</div>' % (uid, anchor, inner))

    # fromTo only - never a CSS transform plus a tween on the same property.
    target = "#%s" % uid
    dur = float(b["dur"])
    js = [
        'tl.fromTo("%s", {y: 46, autoAlpha: 0, scale: 0.965},'
        ' {y: 0, autoAlpha: 1, scale: 1, duration: 0.42, ease: "power3.out"}, %.3f);'
        % (target, b["_local"]),
        'tl.to("%s", {y: -26, autoAlpha: 0, duration: 0.30, ease: "power2.in"}, %.3f);'
        % (target, b["_local"] + max(0.34, dur - 0.30)),
    ]
    top = ANCHOR_Y[anchor]
    return {"html": html, "js": "\n      ".join(js), "box": (top, top + height)}


# ---------------------------------------------------------------- captions ---
# LOCK: captions are short-form only, and they are built from the canonical
# transcript - never re-transcribed. The word timings below came out of one
# WhisperX pass and were remapped through the cut list; asking a second model
# for them would produce a second, disagreeing truth.
#
# The stack sits at y 1240-1560: inside the safe band (200-1620), above the
# platform's own caption furniture, below the face.
CAPTION = {
    "y": 1240,
    "height": 320,
    "words_per_card": 4,
    "size": 86,
    "hi": TOKENS["accent"],
}


def caption_css(canvas):
    return """
.caption { position: absolute; left: 64px; right: 64px; top: %(y)dpx;
           text-align: center; }
/* .cap-line, not .card: the callout kind already owns .card, and a caption
   inheriting its padded panel is a collision you only see in the render. */
.caption .cap-line { position: relative; display: block; margin: 0;
                 font-family: %(display)s; font-size: %(size)dpx; line-height: 1.08;
                 text-transform: uppercase; letter-spacing: -0.015em;
                 text-shadow: 0 6px 30px rgba(0,0,0,0.7), 0 2px 6px rgba(0,0,0,0.8); }
.caption .w { display: inline-block; margin: 0 0.14em; }
.caption .w.hi { color: %(hi)s; }
""" % dict(TOKENS, y=CAPTION["y"] - canvas["safe_top"],
           size=CAPTION["size"], hi=CAPTION["hi"])


def caption_card(words, canvas, uid, card_in):
    """One caption card. Words pop in on their own timings inside the card."""
    spans, js = [], []
    for i, w in enumerate(words):
        wid = "%s-w%d" % (uid, i)
        cls = "w hi" if w.get("hi") else "w"
        spans.append('<span id="%s" class="%s">%s</span>' % (wid, cls, _esc(w["text"])))
        at = max(0.0, w["s"] - card_in)
        js.append('tl.fromTo("#%s", {autoAlpha: 0, y: 18, scale: 0.88},'
                  ' {autoAlpha: 1, y: 0, scale: 1, duration: 0.14, ease: "back.out(2.2)"}, %.3f);'
                  % (wid, at))
    html = '<div id="%s" class="caption"><span class="cap-line">%s</span></div>' % (
        uid, "".join(spans))
    top = CAPTION["y"]
    return {"html": html, "js": "\n      ".join(js),
            "box": (top, top + CAPTION["height"])}
