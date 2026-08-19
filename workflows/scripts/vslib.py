"""vslib.py - shared helpers for the Python steps of the pipeline.

Not a script. Imported by the PEP 723 scripts next to it, which each declare
their own dependencies so `uv run` resolves them without touching the system
interpreter. Every importer does:

    import os, sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import vslib

Everything here is deliberately dependency-light: only numpy, and only in the
functions that genuinely need it.
"""
from __future__ import annotations

import json
import math
import os
import re
import subprocess
import sys
from fractions import Fraction

# ------------------------------------------------------------------ output ---
_TTY = sys.stderr.isatty()
_G, _Y, _R, _D, _O = (
    ("\033[32m", "\033[33m", "\033[31m", "\033[2m", "\033[0m") if _TTY else ("",) * 5
)


def step(msg):
    print("\n%s==>%s %s" % (_G, _O, msg), file=sys.stderr)


def ok(msg):
    print("  %sok%s   %s" % (_G, _O, msg), file=sys.stderr)


def dim(msg):
    print("  %s%s%s" % (_D, msg, _O), file=sys.stderr)


def warn(msg):
    print("  %swarn%s %s" % (_Y, _O, msg), file=sys.stderr)


def die(msg, code=1):
    print("  %sfail%s %s" % (_R, _O, msg), file=sys.stderr)
    sys.exit(code)


# ------------------------------------------------------------------- probe ---
def run(cmd, **kw):
    kw.setdefault("check", True)
    kw.setdefault("stdout", subprocess.PIPE)
    kw.setdefault("stderr", subprocess.PIPE)
    proc = subprocess.run(cmd, **kw)
    return proc


def ffprobe_json(path):
    proc = run([
        "ffprobe", "-v", "error", "-print_format", "json",
        "-show_format", "-show_streams", str(path),
    ])
    return json.loads(proc.stdout)


def probe_media(path):
    """Everything downstream needs to know about a source file, in one shot."""
    info = ffprobe_json(path)
    v = next((s for s in info["streams"] if s.get("codec_type") == "video"), None)
    a = next((s for s in info["streams"] if s.get("codec_type") == "audio"), None)
    dur = float(info.get("format", {}).get("duration") or 0.0)
    out = {
        "path": str(path),
        "duration": dur,
        "container": info.get("format", {}).get("format_name"),
        "size": int(info.get("format", {}).get("size") or 0),
        "has_video": v is not None,
        "has_audio": a is not None,
    }
    if v:
        rate = v.get("r_frame_rate") or v.get("avg_frame_rate") or "30/1"
        if rate in ("0/0", "N/A", None):
            rate = "30/1"
        out.update({
            "fps": rate,
            "fps_float": float(Fraction(rate)),
            "width": int(v.get("width") or 0),
            "height": int(v.get("height") or 0),
            "vcodec": v.get("codec_name"),
            "pix_fmt": v.get("pix_fmt"),
        })
    if a:
        out.update({
            "sample_rate": int(a.get("sample_rate") or 48000),
            "channels": int(a.get("channels") or 1),
            "acodec": a.get("codec_name"),
        })
    return out


# ------------------------------------------------------------- frame grid ---
class FrameGrid:
    """LOCK: every cut boundary snaps to the video frame grid.

    If a boundary lands between frames, the video segment and the audio segment
    end up different lengths, concat pads the difference, and the timeline
    drifts a little further with every joint. Snapping first makes per-segment
    video and audio durations agree by construction.
    """

    def __init__(self, fps):
        self.fps = Fraction(fps) if not isinstance(fps, Fraction) else fps
        if self.fps <= 0:
            raise ValueError("bad frame rate: %r" % (fps,))

    def frame_of(self, t):
        return int(round(Fraction(t).limit_denominator(1000000) * self.fps))

    def time_of(self, frame):
        return float(Fraction(int(frame)) / self.fps)

    def snap(self, t):
        return self.time_of(self.frame_of(t))

    def floor(self, t):
        """Snap outward at an IN point - never clip the front of a word."""
        return self.time_of(math.floor(float(t) * float(self.fps) + 1e-9))

    def ceil(self, t):
        """Snap outward at an OUT point - never clip the tail of a word."""
        return self.time_of(math.ceil(float(t) * float(self.fps) - 1e-9))

    @property
    def frame_dur(self):
        return float(1 / self.fps)

    def __repr__(self):
        return "FrameGrid(%s = %.4f fps)" % (self.fps, float(self.fps))


# ----------------------------------------------------------- audio decode ---
# Downmix with honest 0.5/0.5 coefficients. `-ac 1` does NOT do this: swresample
# uses -3 dB (1/sqrt2) coefficients for stereo->mono, so two identical channels
# come back sqrt(2) hot and every level you measure is 3 dB wrong.
_DOWNMIX = "aformat=channel_layouts=stereo,pan=mono|c0=0.5*c0+0.5*c1"


def _decode(path, args, sample_rate, start=None, duration=None):
    import numpy as np

    cmd = ["ffmpeg", "-v", "error", "-nostdin"]
    if start is not None:
        cmd += ["-ss", "%.6f" % start]
    cmd += ["-i", str(path)]
    if duration is not None:
        cmd += ["-t", "%.6f" % duration]
    cmd += ["-map", "0:a:0"] + args + ["-ar", str(sample_rate),
                                       "-f", "f32le", "-acodec", "pcm_f32le", "-"]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode != 0:
        die("ffmpeg could not decode audio from %s\n%s"
            % (path, proc.stderr.decode("utf-8", "replace")[-800:]))
    return np.frombuffer(proc.stdout, dtype="<f4").astype("float32")


def decode_mono(path, sample_rate=16000, start=None, duration=None):
    """Decode to a true 0.5/0.5 mono downmix at `sample_rate`."""
    return _decode(path, ["-af", _DOWNMIX], sample_rate, start, duration)


def peak_dbfs(path, sample_rate=48000):
    """Highest sample peak across ALL channels, in dBFS.

    Measured per-channel on purpose: a downmix hides a peak that only one
    channel has, and inflates one that both share.
    """
    import numpy as np
    samples = _decode(path, [], sample_rate)
    if samples.size == 0:
        return float("-inf")
    return float(20.0 * np.log10(max(float(np.abs(samples).max()), 1e-12)))


def rms_envelope(samples, sample_rate, hop_ms=5.0, win_ms=20.0):
    """RMS envelope in dBFS, one value every `hop_ms`.

    LOCK: measure cut boundaries, do not trust transcript timestamps. Forced
    alignment reports a word's start 50-100 ms after the real acoustic attack,
    so every boundary gets moved to the measured edge of this envelope.
    """
    import numpy as np

    hop = max(1, int(round(sample_rate * hop_ms / 1000.0)))
    win = max(hop, int(round(sample_rate * win_ms / 1000.0)))
    if samples.size < win:
        samples = np.pad(samples, (0, win - samples.size))
    n = 1 + (samples.size - win) // hop
    # Strided view -> no copy of the whole file.
    strides = (samples.strides[0] * hop, samples.strides[0])
    frames = np.lib.stride_tricks.as_strided(samples, shape=(n, win), strides=strides)
    rms = np.sqrt(np.maximum((frames.astype("float64") ** 2).mean(axis=1), 1e-20))
    db = 20.0 * np.log10(rms)
    return db.astype("float32"), hop / float(sample_rate)


def noise_floor(env_db, percentile=10.0):
    import numpy as np
    return float(np.percentile(env_db, percentile))


# ------------------------------------------------------------------- text ---
_WORD_RE = re.compile(r"[^\W\d_]+(?:['’][^\W\d_]+)*", re.UNICODE)


def normalize_token(word):
    """Lowercased, punctuation-stripped form used for whole-word matching."""
    m = _WORD_RE.findall(word or "")
    return "".join(m).lower() if m else (word or "").strip().lower()


def load_corrections(paths):
    """Spelling fixes, applied when the canonical transcript is written.

    LOCK: corrections live upstream in one file, are single-token whole-word
    swaps only, and touch text - never timings. The raw words.json is never
    edited. Format, one per line:

        teh -> the
        hyperfrhames -> HyperFrames
        # comments and blank lines ignored
    """
    table = {}
    rejected = []
    for path in paths:
        if not path or not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as fh:
            for lineno, raw in enumerate(fh, 1):
                line = raw.split("#", 1)[0].strip()
                if not line:
                    continue
                if "->" not in line:
                    rejected.append((path, lineno, line, "no '->'"))
                    continue
                left, right = (p.strip() for p in line.split("->", 1))
                if not left or not right:
                    rejected.append((path, lineno, line, "empty side"))
                    continue
                if " " in left or " " in right:
                    rejected.append((path, lineno, line, "multi-token; single whole words only"))
                    continue
                table[normalize_token(left)] = right
    return table, rejected


def apply_correction(word, table):
    """Whole-word swap that keeps the original leading/trailing punctuation."""
    key = normalize_token(word)
    if key not in table:
        return word, False
    repl = table[key]
    m = re.match(r"^(\W*)(.*?)(\W*)$", word, re.UNICODE | re.DOTALL)
    if not m:
        return repl, True
    lead, core, trail = m.groups()
    if not core:
        return word, False
    if core[:1].isupper() and repl[:1].islower():
        repl = repl[:1].upper() + repl[1:]
    return lead + repl + trail, True


# ------------------------------------------------------------------- json ---
def read_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def write_json(path, data):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    tmp = str(path) + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    os.replace(tmp, path)


def sha256_file(path):
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def tc(seconds, fps=None):
    """h:mm:ss.mmm for humans."""
    s = max(0.0, float(seconds))
    h = int(s // 3600); m = int((s % 3600) // 60); rest = s - h * 3600 - m * 60
    return "%d:%02d:%06.3f" % (h, m, rest)


def smpte(seconds, fps):
    """HH:MM:SS:FF non-drop, for EDLs."""
    f = int(round(float(seconds) * float(fps)))
    fps_i = int(round(float(fps)))
    ff = f % fps_i
    total_s = f // fps_i
    return "%02d:%02d:%02d:%02d" % (total_s // 3600, (total_s // 60) % 60, total_s % 60, ff)
