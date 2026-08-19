#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""make_test_clip.py - synthesise a take with known ground truth.

Used by verify_pipeline.sh. Produces a wav plus a words.json whose timings are
deliberately WRONG in the way real forced alignment is wrong: every word start
is reported 50-100 ms after the real acoustic attack. If plan_cut.py's envelope
measurement is working, it pulls those boundaries back to the true onsets.

Continuous low-level room tone runs under the whole take, so the joint
crossfades have real continuing tone to work with.
"""
import argparse
import json
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vslib  # noqa: E402

RATE = 48000

SCRIPT = [
    ["so", "here", "is", "the", "thing", "about", "rough", "cuts"],
    ["um"],
    ["they", "are", "not", "hard", "they", "are", "just", "tedious"],
    ["uh"],
    ["and", "tedious", "is", "exactly", "what", "a", "machine", "is", "for"],
    ["you", "you", "point", "it", "at", "the", "footage"],
    ["um"],
    ["and", "it", "gives", "you", "back", "a", "timeline"],
    ["that", "is", "the", "whole", "trick"],
]
# Long pauses after these phrase indices - dead air the planner must remove.
DEAD_AIR_AFTER = {2: 2.10, 5: 1.60}


def word_burst(rng, dur, f0):
    import numpy as np
    n = int(dur * RATE)
    t = np.arange(n) / RATE
    vib = 1.0 + 0.02 * np.sin(2 * np.pi * 5.0 * t)
    sig = np.zeros(n)
    for k, amp in ((1, 1.0), (2, 0.5), (3, 0.28), (4, 0.14), (5, 0.07)):
        sig += amp * np.sin(2 * np.pi * f0 * k * vib * t + rng.uniform(0, 6.28))
    sig /= 2.0
    # A little fricative energy so the envelope has a realistic edge.
    sig += 0.10 * rng.standard_normal(n) * np.exp(-3 * t)
    atk = int(0.018 * RATE)
    rel = int(0.030 * RATE)
    env = np.ones(n)
    env[:atk] = np.linspace(0, 1, atk)
    env[-rel:] = np.linspace(1, 0, rel)
    env *= 0.55 + 0.45 * np.sin(np.linspace(0, np.pi, n))
    return sig * env


def main():
    import numpy as np

    ap = argparse.ArgumentParser()
    ap.add_argument("--out-wav", required=True)
    ap.add_argument("--out-words", required=True)
    ap.add_argument("--seed", type=int, default=7)
    a = ap.parse_args()

    rng = np.random.default_rng(a.seed)
    lead, tail = 0.90, 1.10
    events = []          # (true_onset, true_offset, text)
    t = lead
    for pi, phrase in enumerate(SCRIPT):
        for wi, text in enumerate(phrase):
            dur = float(rng.uniform(0.20, 0.34))
            events.append((t, t + dur, text))
            t += dur + float(rng.uniform(0.045, 0.100))
        t += DEAD_AIR_AFTER.get(pi, 0.34)
    total = t + tail

    n = int(total * RATE)
    # Room tone: continuous, low, present everywhere. This is what the joints
    # crossfade through.
    tone = rng.standard_normal(n) * 0.0022
    b = 0.0
    for i in range(n):                       # cheap one-pole -> pink-ish
        b = 0.94 * b + 0.06 * tone[i]
        tone[i] = b * 3.0
    buf = tone.astype("float64")

    for onset, offset, text in events:
        f0 = 118.0 if text not in ("um", "uh") else 104.0
        amp = 0.26 if text not in ("um", "uh") else 0.17
        burst = word_burst(rng, offset - onset, f0) * amp
        s = int(onset * RATE)
        buf[s:s + burst.size] += burst[:max(0, n - s)]

    # Level it like a sane recording: speech RMS about -24 dBFS, peaks near
    # -12 dBFS. The master stage's +10 dB then lands where it is designed to.
    speech = np.concatenate([buf[int(o * RATE):int(f * RATE)] for o, f, _ in events])
    rms = float(np.sqrt((speech ** 2).mean()))
    buf = buf * (10 ** (-24.0 / 20.0) / max(rms, 1e-9))
    peak = float(np.abs(buf).max())
    ceiling = 10 ** (-12.0 / 20.0)
    if peak > ceiling:
        buf *= ceiling / peak
    pcm = np.clip(buf, -1, 1)
    stereo = np.repeat((pcm * 32767).astype("<i2")[:, None], 2, axis=1).tobytes()

    with open(a.out_wav, "wb") as fh:
        data = stereo
        fh.write(b"RIFF" + struct.pack("<I", 36 + len(data)) + b"WAVEfmt ")
        fh.write(struct.pack("<IHHIIHH", 16, 1, 2, RATE, RATE * 4, 4, 16))
        fh.write(b"data" + struct.pack("<I", len(data)) + data)

    # words.json with the realistic late bias baked in.
    words = []
    for onset, offset, text in events:
        late = float(rng.uniform(0.050, 0.100))
        early_end = float(rng.uniform(0.010, 0.045))
        words.append({
            "i": len(words), "w": text,
            "s": round(onset + late, 3),
            "e": round(max(onset + late + 0.02, offset - early_end), 3),
            "p": 0.95,
        })
    doc = {
        "schema": "video-system/words@1",
        "created": "synthetic",
        "source": {"file": None, "sha256": None, "duration": round(total, 3)},
        "model": {"asr": "synthetic-test-fixture", "device": "none"},
        "language": "en",
        "note": "Test fixture. Word starts are deliberately 50-100 ms late.",
        "words": words,
        "_truth": [{"w": w, "onset": round(o, 4), "offset": round(f, 4)}
                   for o, f, w in events],
    }
    vslib.write_json(a.out_words, doc)
    print("%.3f" % total)


if __name__ == "__main__":
    main()
