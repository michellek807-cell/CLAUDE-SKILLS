#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""make_transcript.py - pipeline step 2d. Write the canonical transcript.

LOCK: derive it by remapping the kept words of transcript/words.json through
cut/cutlist.json. Nothing downstream ever re-transcribes - captions, the
editing-app handoff and the graphics plan all read this file.

LOCK: spelling fixes are applied HERE, from transcript/corrections.txt (plus a
repo-wide workflows/corrections.txt). Single-token whole-word swaps only, text
never timings. words.json stays exactly as the model wrote it.

Also writes the finished script as markdown, which is the other half of what
step 2 owes you.
"""
import argparse
import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vslib  # noqa: E402

SCHEMA = "video-system/transcript@1"
SENTENCE_END = (".", "?", "!", "…")
PARA_GAP = 0.90          # a pause this long starts a new paragraph
PARA_MAX_WORDS = 90


def group_sentences(words):
    out, cur = [], []
    for w in words:
        cur.append(w)
        gap_next = None
        ends = w["w"].rstrip().endswith(SENTENCE_END)
        if ends or len(cur) >= 40:
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    return out


def group_paragraphs(sentences):
    paras, cur = [], []
    for sent in sentences:
        if cur:
            gap = sent[0]["s"] - cur[-1][-1]["e"]
            words = sum(len(s) for s in cur)
            if gap >= PARA_GAP or words >= PARA_MAX_WORDS:
                paras.append(cur)
                cur = []
        cur.append(sent)
    if cur:
        paras.append(cur)
    return paras


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--job-dir", required=True)
    ap.add_argument("--root", required=True)
    a = ap.parse_args()

    job = vslib.read_json(os.path.join(a.job_dir, "job.json"))
    name = job["name"]
    words_doc = vslib.read_json(os.path.join(a.job_dir, "transcript", "words.json"))
    cutlist = vslib.read_json(os.path.join(a.job_dir, "cut", "cutlist.json"))

    if words_doc["source"]["sha256"] != cutlist["source"]["sha256"]:
        vslib.die("words.json and cutlist.json were built from different raw bytes")

    src_words = words_doc["words"]

    # ---- corrections ------------------------------------------------------
    corr_paths = [
        os.path.join(a.root, "workflows", "corrections.txt"),
        os.path.join(a.job_dir, "transcript", "corrections.txt"),
    ]
    table, rejected = vslib.load_corrections(corr_paths)
    for path, lineno, line, why in rejected:
        vslib.warn("%s:%d ignored (%s): %s" % (os.path.relpath(path, a.root), lineno, why, line))

    # ---- remap ------------------------------------------------------------
    out_words = []
    applied = 0
    for seg in cutlist["segments"]:
        offset = seg["out_in"] - seg["src_in"]
        for wi in seg["words"]:
            w = src_words[wi]
            text, changed = vslib.apply_correction(w["w"], table)
            applied += 1 if changed else 0
            s = max(seg["out_in"], round(w["s"] + offset, 3))
            e = min(seg["out_out"], round(w["e"] + offset, 3))
            if e < s:
                e = s
            out_words.append({
                "i": len(out_words),
                "w": text,
                "s": s,
                "e": e,
                "src_s": w["s"],
                "src_e": w["e"],
                "seg": seg["i"],
                "p": w.get("p"),
            })

    if not out_words:
        vslib.die("the cut list kept no words")

    sentences = group_sentences(out_words)
    paragraphs = group_paragraphs(sentences)

    duration = cutlist["segments"][-1]["out_out"]
    payload = {
        "schema": SCHEMA,
        "created": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "job": name,
        "title": job.get("title"),
        "duration": duration,
        "fps": cutlist["source"]["fps"],
        "language": words_doc.get("language"),
        "derived_from": {
            "words": "transcript/words.json",
            "cutlist": "cut/cutlist.json",
            "raw_sha256": cutlist["source"]["sha256"],
        },
        "corrections": {"file": "transcript/corrections.txt", "rules": len(table),
                        "applied": applied},
        "note": "Canonical. Captions, graphics and the editing-app handoff read this. "
                "Nothing downstream re-transcribes.",
        "segments": [
            {
                "i": i,
                "s": sent[0]["s"],
                "e": sent[-1]["e"],
                "text": " ".join(w["w"] for w in sent),
                "words": [w["i"] for w in sent],
            }
            for i, sent in enumerate(sentences)
        ],
        "words": out_words,
        "text": " ".join(w["w"] for w in out_words),
    }

    out_path = os.path.join(a.job_dir, "outputs", "%s.transcript.json" % name)
    vslib.write_json(out_path, payload)

    # ---- the finished script ---------------------------------------------
    lines = [
        "# %s" % (job.get("title") or name),
        "",
        "_Finished script - generated from the cut. %s, %d words, %d paragraphs._"
        % (vslib.tc(duration), len(out_words), len(paragraphs)),
        "",
        "> Derived from `transcript/words.json` remapped through `cut/cutlist.json`.",
        "> Edit `transcript/corrections.txt` for spelling, never this file.",
        "",
    ]
    for para in paragraphs:
        start = para[0][0]["s"]
        lines.append("**[%s]**  %s" % (vslib.tc(start),
                                       " ".join(" ".join(w["w"] for w in s) for s in para)))
        lines.append("")
    script_path = os.path.join(a.job_dir, "outputs", "%s.script.md" % name)
    with open(script_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))

    job["stage"] = "transcript"
    job["outputs"] = job.get("outputs", {})
    job["outputs"]["transcript"] = "outputs/%s.transcript.json" % name
    job["outputs"]["script"] = "outputs/%s.script.md" % name
    vslib.write_json(os.path.join(a.job_dir, "job.json"), job)

    vslib.ok("outputs/%s.transcript.json  %d words, %d sentences"
             % (name, len(out_words), len(sentences)))
    if table:
        vslib.ok("corrections: %d rule(s), %d word(s) swapped" % (len(table), applied))
    vslib.ok("outputs/%s.script.md  %d paragraphs" % (name, len(paragraphs)))


if __name__ == "__main__":
    main()
