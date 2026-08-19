#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10,<3.13"
# dependencies = [
#   "whisperx>=3.3.1",
#   "numpy",
# ]
# ///
"""transcribe.py - pipeline step 2a. WhisperX large-v3 transcribe + word align.

LOCK: transcribe ONCE per video, into transcript/words.json, and reuse it
forever. Every downstream step - the cut list, the canonical transcript, the
captions, the editing-app handoff - reads this file. Nothing re-transcribes,
ever. Re-running with the same raw bytes is a no-op unless you pass --force.

words.json is the raw machine output. It is never hand-edited: spelling fixes
live in transcript/corrections.txt and are applied when the canonical
transcript is written (see make_transcript.py).
"""
import argparse
import contextlib
import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vslib  # noqa: E402

SCHEMA = "video-system/words@1"


@contextlib.contextmanager
def _weights(what):
    """Turn a failed weights fetch into one actionable line, not a traceback.

    The first run of a machine downloads several GB from Hugging Face. Behind a
    proxy or a locked-down network that fails deep inside huggingface_hub, and
    the stack trace says nothing about what to do.
    """
    try:
        yield
    except Exception as exc:                      # noqa: BLE001 - re-raised below
        text = "%s: %s" % (type(exc).__name__, exc)
        if any(k in text for k in ("Proxy", "ConnectionError", "MaxRetry", "Tunnel",
                                   "Temporary failure", "getaddrinfo", "403", "OfflineMode")):
            vslib.die(
                "could not download %s from Hugging Face.\n"
                "       This machine cannot reach huggingface.co right now.\n"
                "       %s\n"
                "       Fixes, in order of preference:\n"
                "         - run this once on a network that allows huggingface.co;\n"
                "           the weights cache in %s and every later job reuses them\n"
                "         - point HF_HOME at a cache you already have\n"
                "         - set HF_HUB_OFFLINE=1 if the weights are already cached"
                % (what, text.split("(Request ID")[0].strip(),
                   os.environ.get("HF_HOME", os.path.expanduser("~/.cache/huggingface"))))
        raise


def pick_device(requested):
    if requested and requested != "auto":
        return requested
    try:
        import torch
        if torch.cuda.is_available():
            return "cuda"
    except Exception:
        pass
    # faster-whisper (CTranslate2) has no MPS backend; Apple silicon runs on CPU.
    return "cpu"


def fill_gaps(words):
    """Alignment leaves numerals and stray symbols without timings.

    Interpolate them from their neighbours so no word in words.json is timeless.
    A word we had to guess is marked est=true and is never used as a cut
    boundary by plan_cut.py.
    """
    n = len(words)
    for i, w in enumerate(words):
        if w.get("s") is not None and w.get("e") is not None:
            continue
        prev = next((words[j] for j in range(i - 1, -1, -1) if words[j].get("e") is not None), None)
        nxt = next((words[j] for j in range(i + 1, n) if words[j].get("s") is not None), None)
        if prev and nxt:
            lo, hi = prev["e"], nxt["s"]
        elif prev:
            lo, hi = prev["e"], prev["e"] + 0.20
        elif nxt:
            lo, hi = max(0.0, nxt["s"] - 0.20), nxt["s"]
        else:
            lo, hi = 0.0, 0.0
        if hi < lo:
            hi = lo
        w["s"], w["e"], w["est"] = round(lo, 3), round(hi, 3), True
    return words


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--job-dir", required=True)
    ap.add_argument("--model", default=os.environ.get("VS_WHISPER_MODEL", "large-v3"))
    ap.add_argument("--language", default=os.environ.get("VS_LANGUAGE", "en"))
    ap.add_argument("--device", default=os.environ.get("VS_DEVICE", "auto"))
    ap.add_argument("--batch-size", type=int, default=int(os.environ.get("VS_BATCH_SIZE", "8")))
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()

    job_path = os.path.join(a.job_dir, "job.json")
    job = vslib.read_json(job_path)
    if not job.get("raw"):
        vslib.die("nothing ingested yet - run intake.sh first")

    raw = os.path.join(a.job_dir, job["raw"]["file"])
    out_path = os.path.join(a.job_dir, "transcript", "words.json")
    raw_sha = job["raw"]["sha256"]

    # ---- the lock: transcribe once ----------------------------------------
    if os.path.exists(out_path) and not a.force:
        try:
            prev = vslib.read_json(out_path)
        except Exception:
            prev = {}
        if prev.get("source", {}).get("sha256") == raw_sha:
            vslib.ok("transcript/words.json already covers these raw bytes (%d words) - reusing"
                     % len(prev.get("words", [])))
            return
        vslib.warn("transcript/words.json was made from different raw bytes - re-transcribing")

    device = pick_device(a.device)
    compute_type = "float16" if device == "cuda" else "int8"
    vslib.step("whisperx %s on %s (%s)" % (a.model, device, compute_type))
    vslib.dim("first run downloads the weights once; later jobs reuse the cache")

    try:
        import whisperx
    except ImportError as exc:  # pragma: no cover - environment problem, not logic
        vslib.die("whisperx unavailable: %s\n"
                  "       This script is meant to run through uv, which resolves it:\n"
                  "         uv run workflows/scripts/transcribe.py --job-dir <dir>" % exc)

    audio = whisperx.load_audio(raw)
    with _weights("the %s weights" % a.model):
        model = whisperx.load_model(
            a.model, device, compute_type=compute_type,
            language=(None if a.language in ("", "auto") else a.language),
        )
    result = model.transcribe(audio, batch_size=a.batch_size)
    lang = result.get("language") or a.language
    vslib.ok("transcribed: %d segments, language=%s" % (len(result.get("segments", [])), lang))

    # Free the ASR model before the aligner loads; on a laptop this matters.
    del model
    try:
        import gc
        gc.collect()
    except Exception:
        pass

    vslib.step("forced word alignment")
    with _weights("the %s alignment model" % lang):
        align_model, meta = whisperx.load_align_model(language_code=lang, device=device)
    aligned = whisperx.align(result["segments"], align_model, meta, audio, device,
                             return_char_alignments=False)

    words = []
    for w in aligned.get("word_segments", []):
        text = (w.get("word") or "").strip()
        if not text:
            continue
        words.append({
            "i": len(words),
            "w": text,
            "s": (round(float(w["start"]), 3) if w.get("start") is not None else None),
            "e": (round(float(w["end"]), 3) if w.get("end") is not None else None),
            "p": (round(float(w["score"]), 3) if w.get("score") is not None else None),
        })
    if not words:
        vslib.die("alignment produced no words - is there speech in this file?")
    words = fill_gaps(words)
    est = sum(1 for w in words if w.get("est"))

    payload = {
        "schema": SCHEMA,
        "created": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": {
            "file": job["raw"]["file"],
            "sha256": raw_sha,
            "duration": job["raw"]["duration"],
        },
        "model": {"asr": a.model, "device": device, "compute_type": compute_type,
                  "aligner": meta.get("type", "wav2vec2") if isinstance(meta, dict) else "wav2vec2"},
        "language": lang,
        "note": "Raw machine output. Never hand-edit. Spelling fixes go in "
                "transcript/corrections.txt and are applied to the canonical transcript.",
        "words": words,
    }
    vslib.write_json(out_path, payload)

    job["stage"] = "transcribed"
    job["transcript"] = {"words": "transcript/words.json", "count": len(words), "language": lang}
    vslib.write_json(job_path, job)

    vslib.ok("transcript/words.json: %d words%s"
             % (len(words), (", %d interpolated" % est) if est else ""))
    preview = " ".join(w["w"] for w in words[:28])
    vslib.dim('opens: "%s..."' % preview)


if __name__ == "__main__":
    main()
