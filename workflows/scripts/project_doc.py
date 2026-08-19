#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""project_doc.py - regenerate projects/<job>/PROJECT.md.

The resume doc. Open it cold in three weeks and it tells you where the job got
to, what the numbers were, and the exact next command. Everything above the
NOTES marker is generated and gets overwritten; everything below it is yours
and is carried through untouched.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vslib  # noqa: E402

MARKER = "<!-- NOTES: everything below this line is hand-written and preserved -->"

STAGES = [
    ("created",     "1  intake",        "workflows/scripts/intake.sh %s <file>"),
    ("intake",      "2  transcribe",    "workflows/scripts/rough_cut.sh %s"),
    ("transcribed", "2  plan cut",      "workflows/scripts/rough_cut.sh %s"),
    ("planned",     "2  splice",        "workflows/scripts/rough_cut.sh %s"),
    ("cut",         "2  transcript",    "workflows/scripts/rough_cut.sh %s"),
    ("transcript",  "3  graphics plan", "workflows/scripts/graphics_plan.sh %s"),
    ("graphics",    "4  second pass",   "review, then workflows/scripts/hf_render.sh %s <part>"),
    ("reviewed",    "5  captions",      "workflows/scripts/captions.sh %s"),
    ("captioned",   "6  music",         "workflows/scripts/music_bed.sh %s <track>"),
    ("music",       "7  export",        "./finalize.sh %s"),
    ("final",       "-  done",          "./prune.sh %s"),
]


def human_size(n):
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return "%.0f %s" % (n, unit) if unit != "B" else "%d B" % n
        n /= 1024.0


def dir_report(job_dir):
    rows = []
    for name in ("raw", "audio", "assets", "broll", "outputs", "hf-graphics",
                 "transcript", "cut", "cache"):
        path = os.path.join(job_dir, name)
        if not os.path.isdir(path):
            continue
        total, count = 0, 0
        for root, _dirs, files in os.walk(path):
            for f in files:
                try:
                    total += os.path.getsize(os.path.join(root, f))
                    count += 1
                except OSError:
                    pass
        rows.append((name + "/", count, total))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--job-dir", required=True)
    a = ap.parse_args()

    job_dir = os.path.abspath(a.job_dir)
    job = vslib.read_json(os.path.join(job_dir, "job.json"))
    name = job["name"]
    stage = job.get("stage", "created")
    doc_path = os.path.join(job_dir, "PROJECT.md")

    notes = ""
    if os.path.exists(doc_path):
        with open(doc_path, encoding="utf-8") as fh:
            existing = fh.read()
        if MARKER in existing:
            notes = existing.split(MARKER, 1)[1]

    stage_names = [s[0] for s in STAGES]
    cur = stage_names.index(stage) if stage in stage_names else 0

    L = []
    L.append("# %s" % (job.get("title") or name))
    L.append("")
    L.append("`projects/%s` &middot; **%s** &middot; stage: **%s** &middot; created %s"
             % (name, "9:16 short-form" if job.get("format") == "short" else "16:9 long-form",
                stage, job.get("created", "?")))
    L.append("")

    raw = job.get("raw")
    if raw:
        L.append("## Source")
        L.append("")
        L.append("| | |")
        L.append("|---|---|")
        L.append("| file | `raw/%s` |" % os.path.basename(raw["file"]))
        L.append("| duration | %s |" % vslib.tc(raw["duration"]))
        L.append("| frame | %sx%s @ %s fps |" % (raw.get("width"), raw.get("height"), raw.get("fps")))
        L.append("| codec | %s / %s |" % (raw.get("vcodec"), raw.get("acodec")))
        L.append("| sha256 | `%s` |" % raw["sha256"][:16])
        L.append("| ingested from | `%s` |" % raw.get("ingested_from", "?"))
        L.append("")
        L.append("Copied in, never moved. `raw/` is immutable - every step reads it and nothing writes it.")
        L.append("")

    cut = job.get("cut")
    if cut and cut.get("segments"):
        cl_path = os.path.join(job_dir, "cut", "cutlist.json")
        L.append("## Cut")
        L.append("")
        if os.path.exists(cl_path):
            cl = vslib.read_json(cl_path)
            st = cl["stats"]
            L.append("| | |")
            L.append("|---|---|")
            L.append("| segments | %d (%d joints) |" % (st["segments"], st["joints"]))
            L.append("| length | %s -> %s |" % (vslib.tc(st["source_duration"]),
                                                vslib.tc(st["output_duration"])))
            L.append("| removed | %s (%.1f%%) |" % (vslib.tc(st["removed"]), st["removed_pct"]))
            L.append("| words dropped | %d of %d |" % (st["words_dropped"], st["words_in"]))
            L.append("| noise floor | %.1f dBFS, threshold %.1f dBFS |"
                     % (cl["measurement"]["noise_floor_db"], cl["measurement"]["threshold_db"]))
            L.append("")
            counts = {}
            for r in cl.get("removed", []):
                counts[r["reason"]] = counts.get(r["reason"], 0) + r["dur"]
            if counts:
                L.append("Removed by reason: " + ", ".join(
                    "%s %.1fs" % (k, v) for k, v in sorted(counts.items(), key=lambda kv: -kv[1])))
                L.append("")

    outs = job.get("outputs") or {}
    if outs:
        L.append("## Outputs")
        L.append("")
        for k in sorted(outs):
            p = os.path.join(job_dir, outs[k])
            mark = "" if os.path.exists(p) else "  _(missing)_"
            L.append("- **%s** &mdash; `%s`%s" % (k, outs[k], mark))
        L.append("")

    L.append("## Pipeline")
    L.append("")
    L.append("| | step | state |")
    L.append("|---|---|---|")
    for i, (key, label, _cmd) in enumerate(STAGES[:-1]):
        state = "done" if i < cur else ("**next**" if i == cur else "-")
        L.append("| %s | %s | %s |" % ("x" if i < cur else " ", label, state))
    L.append("")
    nxt = STAGES[min(cur, len(STAGES) - 1)]
    L.append("Next: `%s`" % (nxt[2] % name))
    L.append("")

    rows = dir_report(job_dir)
    if rows:
        L.append("## Folder")
        L.append("")
        L.append("| dir | files | size | |")
        L.append("|---|---:|---:|---|")
        keepers = {"raw/": "never pruned", "outputs/": "never pruned",
                   "assets/": "never pruned", "broll/": "never pruned",
                   "audio/": "never pruned", "transcript/": "never pruned",
                   "cut/": "regenerable", "cache/": "regenerable",
                   "hf-graphics/": "renders regenerable"}
        for d, count, total in rows:
            L.append("| `%s` | %d | %s | %s |" % (d, count, human_size(total), keepers.get(d, "")))
        L.append("")

    L.append(MARKER)
    if notes.strip():
        L.append(notes.rstrip("\n"))
    else:
        L.append("")
        L.append("## Notes")
        L.append("")
        L.append("_Second-pass calls, what got rejected and why, anything the next run should know._")
    L.append("")

    with open(doc_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L))
    print(doc_path)


if __name__ == "__main__":
    main()
