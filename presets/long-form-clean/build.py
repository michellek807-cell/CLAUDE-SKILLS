"""long-form-clean - locked look for 16:9 long-form graphics.

Same module contract as short-form-punch: css(canvas) and beat(b, canvas, uid).
Quieter than the short-form look on purpose - a 16:9 piece is watched, not
scrolled past, so the graphics support the talking rather than shout over it.

The 16:9 frame has no platform chrome eating the edges, so the safe band is a
thin title-safe margin rather than a 200/300 px keep-out.
"""

NAME = "long-form-clean"
FORMAT = "long"
CANVAS = {"w": 1920, "h": 1080, "safe_top": 60, "safe_bottom": 60}

TOKENS = {
    "ink": "#f4f4f5",
    "ink_dim": "rgba(244,244,245,0.66)",
    "accent": "#7cc4ff",
    "card": "rgba(14,16,20,0.86)",
    "edge": "rgba(255,255,255,0.10)",
    "display": '"Inter Tight","Inter",system-ui,sans-serif',
    "body": '"Inter",system-ui,sans-serif',
}


def css(canvas):
    return """
:root {
  --ink: %(ink)s; --ink-dim: %(ink_dim)s; --accent: %(accent)s;
  --card: %(card)s; --edge: %(edge)s;
}
html, body { margin: 0; background: transparent; }
#root { position: relative; width: %(w)dpx; height: %(h)dpx; overflow: hidden;
        background: transparent; font-family: %(body)s; color: var(--ink); }
.clip { position: absolute; inset: 0; }
.safe { position: absolute; left: 96px; right: 96px;
        top: %(safe_top)dpx; bottom: %(safe_bottom)dpx; }

.lower3 { position: absolute; left: 0; bottom: 72px; max-width: 980px; }
.centered { position: absolute; left: 0; right: 0; top: 300px; text-align: center; }
.corner { position: absolute; right: 0; top: 40px; max-width: 620px; }

.bar { position: relative; display: block; padding: 26px 34px 28px 34px;
       background: var(--card); border-left: 8px solid var(--accent);
       border-radius: 4px 18px 18px 4px; }
.bar .name { display: block; margin: 0; font-family: %(display)s; font-size: 46px;
             font-weight: 700; letter-spacing: -0.01em; line-height: 1.1; }
.bar .role { display: block; margin: 10px 0 0 0; font-size: 28px; line-height: 1.3;
             color: var(--ink-dim); }

.title { position: relative; margin: 0; font-family: %(display)s; font-size: 96px;
         font-weight: 800; letter-spacing: -0.03em; line-height: 1.04;
         text-wrap: balance; text-shadow: 0 8px 44px rgba(0,0,0,0.5); }
.title .hi { color: var(--accent); }
.sub { position: relative; display: block; margin: 24px 0 0 0; font-size: 34px;
       color: var(--ink-dim); }
.pill { position: relative; display: inline-block; padding: 16px 28px;
        background: var(--card); border: 1px solid var(--edge); border-radius: 999px;
        font-size: 30px; font-weight: 600; letter-spacing: 0.01em; }
.scrim { position: absolute; left: -80px; right: -80px; top: -60px; bottom: -60px;
         background: radial-gradient(90%% 80%% at 50%% 50%%, rgba(0,0,0,0.55), rgba(0,0,0,0)); }
""" % dict(TOKENS, w=canvas["w"], h=canvas["h"],
           safe_top=canvas["safe_top"], safe_bottom=canvas["safe_bottom"])


def _esc(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def beat(b, canvas, uid):
    kind = b.get("kind", "lower-third")
    text, sub = b.get("text", ""), b.get("sub", "")

    if kind in ("title", "endcard"):
        parts = _esc(text).rsplit(" ", 1)
        head = parts[0] if len(parts) == 1 else '%s <span class="hi">%s</span>' % tuple(parts)
        inner = '<div class="scrim"></div><h1 id="%s-h" class="title">%s</h1>' % (uid, head)
        if sub:
            inner += '<span class="sub">%s</span>' % _esc(sub)
        cls, box = "centered", (300, 300 + (240 if not sub else 330))
        enter = {"y": 40, "x": 0}
    elif kind == "kicker":
        inner = '<span id="%s-p" class="pill">%s</span>' % (uid, _esc(text))
        cls, box = "corner", (40, 130)
        enter = {"y": -24, "x": 0}
    else:  # lower-third
        inner = ('<div class="bar"><span class="name">%s</span>%s</div>'
                 % (_esc(text),
                    '<span class="role">%s</span>' % _esc(sub) if sub else ""))
        cls, box = "lower3", (canvas["h"] - 72 - 170, canvas["h"] - 72)
        enter = {"y": 0, "x": -56}

    html = '<div id="%s" class="%s">%s</div>' % (uid, cls, inner)
    dur = float(b["dur"])
    js = [
        'tl.fromTo("#%s", {x: %d, y: %d, autoAlpha: 0},'
        ' {x: 0, y: 0, autoAlpha: 1, duration: 0.46, ease: "power3.out"}, %.3f);'
        % (uid, enter["x"], enter["y"], b["_local"]),
        'tl.to("#%s", {autoAlpha: 0, duration: 0.34, ease: "power2.in"}, %.3f);'
        % (uid, b["_local"] + max(0.40, dur - 0.34)),
    ]
    return {"html": html, "js": "\n      ".join(js), "box": box}
