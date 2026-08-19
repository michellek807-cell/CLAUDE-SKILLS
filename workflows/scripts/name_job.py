#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""name_job.py - propose a kebab-case job name from what the video is ABOUT.

Job names are content titles. C0042.MP4 tells you nothing in three weeks, and
neither does 2024-11-03-final-v2. This reads the opening of the transcript,
throws away the throat-clearing, and keeps the first content-bearing phrase.

Prints the slug on stdout and nothing else, so callers can use it directly.
"""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vslib  # noqa: E402

# Openers that carry no information about the video.
THROAT = {
    "um", "uh", "so", "okay", "ok", "alright", "right", "hey", "hi", "hello",
    "yeah", "yes", "well", "now", "look", "listen", "guys", "everyone", "everybody",
    "welcome", "back", "today", "i'm", "im", "we're", "were", "gonna", "going",
    "to", "talk", "about", "wanted", "want", "let's", "lets", "this", "video",
    "quick", "just", "and", "the", "a", "an", "of", "in", "is", "it", "you",
}
STOP_TAIL = {"the", "a", "an", "of", "to", "and", "in", "on", "for", "with", "is", "that"}
MAX_WORDS = 6


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--job-dir", required=True)
    a = ap.parse_args()

    path = os.path.join(a.job_dir, "transcript", "words.json")
    if not os.path.exists(path):
        return
    words = vslib.read_json(path)["words"]

    toks = []
    for w in words[:80]:
        t = vslib.normalize_token(w["w"])
        if t:
            toks.append(t)

    # Skip the opener, then take a short run of real words.
    i = 0
    while i < len(toks) and toks[i] in THROAT:
        i += 1
    picked = []
    for t in toks[i:]:
        if len(picked) >= MAX_WORDS:
            break
        if not picked and t in THROAT:
            continue
        picked.append(t)
    while picked and picked[-1] in STOP_TAIL:
        picked.pop()

    slug = re.sub(r"[^a-z0-9]+", "-", "-".join(picked)).strip("-")
    if len(slug) < 4:
        return
    print(slug[:60].rstrip("-"))


if __name__ == "__main__":
    main()
