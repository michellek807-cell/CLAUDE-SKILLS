#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""parts_ids.py - list graphics/caption part ids, one per line.

  --missing   only the parts that have no render yet (empty output = all done)
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vslib  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--job-dir", required=True)
ap.add_argument("--kind", default="graphics", choices=["graphics", "captions"])
ap.add_argument("--missing", action="store_true")
a = ap.parse_args()

base = os.path.join(a.job_dir, "hf-graphics")
if a.kind == "captions":
    base = os.path.join(base, "captions")
manifest = os.path.join(base, "parts.json")
if not os.path.exists(manifest):
    sys.exit(0)

for p in vslib.read_json(manifest)["parts"]:
    if a.missing and os.path.exists(os.path.join(base, "renders", p["id"] + ".mov")):
        continue
    print(p["id"])
