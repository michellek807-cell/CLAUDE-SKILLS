#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""plan_cut.py - pipeline step 2b. Decide every cut, then measure it.

Reads transcript/words.json, kills filler and dead air, and writes
cut/cutlist.json: the single source of truth for the render, the canonical
transcript, and the editing-app handoff.

Three locks live in this file.

  Measure, do not trust.   Forced alignment reports a word's start 50-100 ms
                           after its real acoustic attack. Every boundary is
                           moved to the edge measured on an RMS envelope of the
                           raw audio, then padded outward.

  Snap to the frame grid.  Boundaries land on video frames, so per-segment
                           video and audio durations agree and concat has
                           nothing to pad.

  Room-tone joints.        Each segment carries a short handle of REAL audio
                           from just past its own cut point. The renderer
                           equal-power crossfades those handles. Half the fade
                           comes out of each side, so the assembled audio is
                           exactly as long as the assembled video - no drift.
"""
import argparse
import datetime
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vslib  # noqa: E402

SCHEMA = "video-system/cutlist@1"

DEFAULTS = {
    # Disfluencies that are always dead weight.
    "fillers": ["um", "uh", "umm", "uhh", "uhm", "er", "erm", "ah", "eh",
                "hmm", "hm", "mm", "mmm", "mhm", "uhhuh", "huh"],
    # Words that are sometimes meaning and sometimes noise. Off by default:
    # cutting these blind mangles sentences.
    "aggressive_fillers": ["like", "so", "basically", "actually", "literally",
                           "honestly", "kinda", "sorta", "right"],
    "drop_aggressive": False,
    "drop_stutters": True,        # "the the", "I I"
    "min_confidence": 0.0,        # drop words the aligner is unsure of (0 = off)

    "max_gap": 0.60,              # silence longer than this between kept words is dead air
    "join_gap": 0.10,             # removing less than this is not worth a joint
    "min_segment": 0.20,          # segments shorter than this are noise

    "search": 0.30,               # how far to scan the envelope for the real edge
    "head_pad": 0.060,            # room tone left in front of a measured attack
    "tail_pad": 0.100,            # room tone left after a measured decay
    "sentence_tail_pad": 0.180,   # a beat after . ? !
    "floor_offset_db": 8.0,       # speech threshold, above the measured noise floor
    "abs_floor_db": -55.0,

    "crossfade_ms": 24.0,         # equal-power joint length
    "envelope_hop_ms": 5.0,
    "envelope_win_ms": 20.0,
    "envelope_rate": 16000,
}

SENTENCE_END = (".", "?", "!", "…")


def load_config(job_dir, root):
    cfg = dict(DEFAULTS)
    for path in (os.path.join(root, "workflows", "cut.config.json"),
                 os.path.join(job_dir, "cut", "cut.config.json")):
        if os.path.exists(path):
            cfg.update(vslib.read_json(path))
    return cfg


# --------------------------------------------------------------- selection ---
def mark_drops(words, cfg):
    fillers = set(cfg["fillers"])
    if cfg.get("drop_aggressive"):
        fillers |= set(cfg["aggressive_fillers"])
    min_conf = float(cfg.get("min_confidence") or 0.0)

    reasons = [None] * len(words)
    prev_kept_tok = None
    for i, w in enumerate(words):
        tok = vslib.normalize_token(w["w"])
        if not tok:
            reasons[i] = "punctuation"
            continue
        if tok in fillers:
            reasons[i] = "filler:%s" % tok
            continue
        if min_conf and w.get("p") is not None and w["p"] < min_conf:
            reasons[i] = "low-confidence:%.2f" % w["p"]
            continue
        if cfg.get("drop_stutters") and tok == prev_kept_tok and len(tok) <= 4:
            # Only immediate repeats of short words; "very very good" survives.
            reasons[i] = "stutter:%s" % tok
            continue
        prev_kept_tok = tok
    return reasons


def build_intervals(words, reasons, cfg):
    """Kept words -> raw source intervals, breaking at every removal and at dead air."""
    intervals = []
    cur = None
    prev_idx = None
    for i, w in enumerate(words):
        if reasons[i] is not None:
            continue
        if cur is None:
            cur = {"in": w["s"], "out": w["e"], "words": [i]}
            prev_idx = i
            continue
        removed_between = any(reasons[j] is not None for j in range(prev_idx + 1, i))
        gap = w["s"] - words[prev_idx]["e"]
        if removed_between or gap > cfg["max_gap"]:
            intervals.append(cur)
            cur = {"in": w["s"], "out": w["e"], "words": [i]}
        else:
            cur["out"] = w["e"]
            cur["words"].append(i)
        prev_idx = i
    if cur is not None:
        intervals.append(cur)
    return intervals


# ------------------------------------------------------------- measurement ---
class Envelope:
    def __init__(self, path, cfg):
        import numpy as np
        self.np = np
        rate = int(cfg["envelope_rate"])
        samples = vslib.decode_mono(path, sample_rate=rate)
        self.db, self.hop = vslib.rms_envelope(
            samples, rate, hop_ms=cfg["envelope_hop_ms"], win_ms=cfg["envelope_win_ms"])
        self.floor = vslib.noise_floor(self.db, 10.0)
        self.thresh = max(self.floor + float(cfg["floor_offset_db"]), float(cfg["abs_floor_db"]))
        self.n = len(self.db)
        self.duration = self.n * self.hop

    def idx(self, t):
        return max(0, min(self.n - 1, int(round(float(t) / self.hop))))

    def time(self, i):
        return max(0.0, i * self.hop)

    def loud(self, i):
        return self.db[i] >= self.thresh

    def attack_before(self, t, search):
        """Walk back from t to the real onset of this word."""
        i = self.idx(t)
        lo = self.idx(max(0.0, t - search))
        if not self.loud(i):
            # Reported start is early or lands in a dip - walk forward to the onset.
            j = i
            hi = self.idx(t + search)
            while j < hi and not self.loud(j):
                j += 1
            return self.time(j)
        while i > lo and self.loud(i - 1):
            i -= 1
        return self.time(i)

    def decay_after(self, t, search):
        """Walk forward from t to where this word actually stops sounding."""
        i = self.idx(t)
        hi = self.idx(min(self.duration, t + search))
        if not self.loud(i):
            j = i
            lo = self.idx(max(0.0, t - search))
            while j > lo and not self.loud(j):
                j -= 1
            return self.time(j + 1)
        while i < hi and self.loud(i + 1 if i + 1 < self.n else i):
            i += 1
        return self.time(i + 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--job-dir", required=True)
    ap.add_argument("--root", required=True)
    ap.add_argument("--aggressive", action="store_true",
                    help="also drop like/so/basically/actually/literally")
    ap.add_argument("--keep-fillers", action="store_true",
                    help="dead air only; leave every word in")
    a = ap.parse_args()

    job_dir = a.job_dir
    job = vslib.read_json(os.path.join(job_dir, "job.json"))
    words_path = os.path.join(job_dir, "transcript", "words.json")
    if not os.path.exists(words_path):
        vslib.die("no transcript/words.json - run transcribe.py first (once per video, forever)")

    doc = vslib.read_json(words_path)
    words = doc["words"]
    raw = os.path.join(job_dir, job["raw"]["file"])

    cfg = load_config(job_dir, a.root)
    if a.aggressive:
        cfg["drop_aggressive"] = True
    if a.keep_fillers:
        cfg["fillers"] = []
        cfg["drop_aggressive"] = False
        cfg["drop_stutters"] = False

    grid = vslib.FrameGrid(job["raw"].get("fps") or "30/1")
    duration = float(job["raw"]["duration"])
    vslib.step("planning the cut on %s" % grid)

    # ---- 1. what goes ------------------------------------------------------
    reasons = mark_drops(words, cfg)
    dropped = sum(1 for r in reasons if r is not None and not r.startswith("punctuation"))
    intervals = build_intervals(words, reasons, cfg)
    if not intervals:
        vslib.die("every word was dropped - check cut.config.json")
    vslib.ok("%d words in, %d dropped, %d speech runs" % (len(words), dropped, len(intervals)))

    # ---- 2. measure every boundary ----------------------------------------
    vslib.step("measuring boundaries against an RMS envelope of the raw audio")
    env = Envelope(raw, cfg)
    vslib.dim("noise floor %.1f dBFS, speech threshold %.1f dBFS, %.0f ms hop"
              % (env.floor, env.thresh, env.hop * 1000))

    measured = []
    for iv in intervals:
        last_word = words[iv["words"][-1]]
        tail_pad = (cfg["sentence_tail_pad"]
                    if last_word["w"].rstrip().endswith(SENTENCE_END) else cfg["tail_pad"])
        attack = env.attack_before(iv["in"], cfg["search"])
        decay = env.decay_after(iv["out"], cfg["search"])
        m_in = max(0.0, attack - cfg["head_pad"])
        m_out = min(duration, decay + tail_pad)
        measured.append({
            "in": m_in, "out": m_out, "words": iv["words"],
            "in_delta": round(m_in - iv["in"], 4),
            "out_delta": round(m_out - iv["out"], 4),
        })

    deltas_in = [m["in_delta"] for m in measured]
    vslib.ok("in-points moved %+.0f ms mean (%+.0f..%+.0f ms)"
             % (1000 * sum(deltas_in) / len(deltas_in),
                1000 * min(deltas_in), 1000 * max(deltas_in)))

    # ---- 3. snap to the frame grid ----------------------------------------
    for m in measured:
        m["in"] = max(0.0, grid.floor(m["in"]))
        m["out"] = min(grid.ceil(duration), grid.ceil(m["out"]))

    # ---- 4. resolve overlaps, merge pointless joints ----------------------
    merged = [measured[0]]
    dropped_short = 0
    for m in measured[1:]:
        prev = merged[-1]
        if m["in"] <= prev["out"] + cfg["join_gap"]:
            prev["out"] = max(prev["out"], m["out"])
            prev["words"] = prev["words"] + m["words"]
            prev["out_delta"] = m["out_delta"]
        else:
            merged.append(m)
    kept = []
    for m in merged:
        if m["out"] - m["in"] < cfg["min_segment"]:
            dropped_short += 1
            continue
        kept.append(m)
    if not kept:
        vslib.die("nothing survived merging - min_segment is probably too large")
    if len(merged) != len(measured) or dropped_short:
        vslib.dim("merged %d joint(s) shorter than %.0f ms%s"
                  % (len(measured) - len(merged), cfg["join_gap"] * 1000,
                     ", dropped %d sub-%.0f ms segment(s)" % (dropped_short, cfg["min_segment"] * 1000)
                     if dropped_short else ""))

    # ---- 5. joints: equal-power crossfade length per gap -------------------
    xf_default = float(cfg["crossfade_ms"]) / 1000.0
    joints = []
    for i in range(len(kept) - 1):
        gap = kept[i + 1]["in"] - kept[i]["out"]
        room = min(kept[i]["out"] - kept[i]["in"], kept[i + 1]["out"] - kept[i + 1]["in"])
        # The handles must fit inside the removed gap (so they are real room tone
        # from a part of the take we are throwing away, not duplicated speech),
        # and inside both neighbouring segments.
        x = min(xf_default, gap, room * 0.5)
        joints.append(max(0.0, round(x, 4)))

    # ---- 6. emit -----------------------------------------------------------
    segments = []
    t = 0.0
    for i, m in enumerate(kept):
        dur = m["out"] - m["in"]
        xf_in = joints[i - 1] if i > 0 else 0.0
        xf_out = joints[i] if i < len(joints) else 0.0
        segments.append({
            "i": i,
            "src_in": round(m["in"], 6),
            "src_out": round(m["out"], 6),
            "src_in_frame": grid.frame_of(m["in"]),
            "src_out_frame": grid.frame_of(m["out"]),
            "frames": grid.frame_of(m["out"]) - grid.frame_of(m["in"]),
            "dur": round(dur, 6),
            "out_in": round(t, 6),
            "out_out": round(t + dur, 6),
            # audio window, widened by half a crossfade at each joint
            "a_in": round(max(0.0, m["in"] - xf_in / 2.0), 6),
            "a_out": round(min(duration, m["out"] + xf_out / 2.0), 6),
            "xfade_in": xf_in,
            "xfade_out": xf_out,
            "words": m["words"],
            "measured": {"in_delta": m["in_delta"], "out_delta": m["out_delta"]},
        })
        t += dur

    removed = []
    cursor = 0.0
    for seg in segments:
        if seg["src_in"] > cursor + 1e-6:
            span = (cursor, seg["src_in"])
            why = "head" if cursor == 0.0 else "cut"
            inner = [reasons[i] for i in range(len(words))
                     if reasons[i] and span[0] <= words[i]["s"] < span[1]]
            if inner:
                why = inner[0].split(":")[0]
            elif why != "head":
                why = "dead-air"
            removed.append({"src_in": round(span[0], 3), "src_out": round(span[1], 3),
                            "dur": round(span[1] - span[0], 3), "reason": why})
        cursor = seg["src_out"]
    if duration - cursor > 1e-6:
        removed.append({"src_in": round(cursor, 3), "src_out": round(duration, 3),
                        "dur": round(duration - cursor, 3), "reason": "tail"})

    out_dur = segments[-1]["out_out"]
    payload = {
        "schema": SCHEMA,
        "created": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": {
            "file": job["raw"]["file"],
            "sha256": job["raw"]["sha256"],
            "duration": duration,
            "fps": str(grid.fps),
            "fps_float": float(grid.fps),
        },
        "transcript": {"file": "transcript/words.json", "words": len(words)},
        "config": cfg,
        "measurement": {
            "noise_floor_db": round(env.floor, 2),
            "threshold_db": round(env.thresh, 2),
            "hop_ms": round(env.hop * 1000, 2),
        },
        "stats": {
            "segments": len(segments),
            "joints": len(joints),
            "words_in": len(words),
            "words_dropped": dropped,
            "source_duration": round(duration, 3),
            "output_duration": round(out_dur, 3),
            "removed": round(duration - out_dur, 3),
            "removed_pct": round(100.0 * (duration - out_dur) / duration, 1) if duration else 0.0,
        },
        "segments": segments,
        "removed": removed,
    }
    out_path = os.path.join(job_dir, "cut", "cutlist.json")
    vslib.write_json(out_path, payload)

    job["stage"] = "planned"
    job["cut"] = {"list": "cut/cutlist.json", "segments": len(segments),
                  "duration": round(out_dur, 3)}
    vslib.write_json(os.path.join(job_dir, "job.json"), job)

    vslib.step("cut planned")
    vslib.ok("%d segments, %d joints" % (len(segments), len(joints)))
    vslib.ok("%s -> %s  (%.1f%% removed)"
             % (vslib.tc(duration), vslib.tc(out_dur), payload["stats"]["removed_pct"]))
    if joints:
        vslib.dim("joint crossfades %.0f-%.0f ms, equal power, real room tone"
                  % (1000 * min(joints), 1000 * max(joints)))
        tight = sum(1 for j in joints if j < xf_default - 1e-6)
        if tight:
            vslib.dim("%d joint(s) shortened to fit the gap they sit in" % tight)


if __name__ == "__main__":
    main()
