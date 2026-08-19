#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""hf_lock.py - maintain skills-lock.json.

One entry per skill: where it came from, its path in this repo, and the sha256
of its SKILL.md bytes. The hash is the tripwire: if a SKILL.md changes without
going through `hf_pin.sh`, `verify` says so.

Entries belonging to other packs (higgsfield, hand-written local skills) are
read, preserved, and re-verified, never clobbered.
"""
import argparse
import hashlib
import json
import os
import sys

LOCK_VERSION = 1


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def load_lock(path):
    if not os.path.exists(path):
        return {"version": LOCK_VERSION, "skills": {}}
    with open(path) as fh:
        data = json.load(fh)
    data.setdefault("version", LOCK_VERSION)
    data.setdefault("skills", {})
    return data


def write_lock(path, data):
    data["skills"] = dict(sorted(data["skills"].items()))
    with open(path, "w") as fh:
        json.dump(data, fh, indent=2, sort_keys=False)
        fh.write("\n")


def skill_md(root, name):
    return os.path.join(root, ".claude", "skills", name, "SKILL.md")


def resolve(root, name, entry):
    """Repo-root-relative path to a locked skill's SKILL.md.

    Older lock entries recorded the path relative to .claude/skills/ instead of
    the repo root; accept both and normalise on write.
    """
    rel = (entry or {}).get("skillPath")
    candidates = []
    if rel:
        candidates.append(rel)
        candidates.append(os.path.join(".claude", "skills", rel))
    candidates.append(os.path.join(".claude", "skills", name, "SKILL.md"))
    for cand in candidates:
        if os.path.exists(os.path.join(root, cand)):
            return cand
    return candidates[0]


def cmd_update(args):
    lock = load_lock(args.lock)
    with open(args.roster) as fh:
        roster = [ln.strip() for ln in fh if ln.strip()]

    updated, added, missing = [], [], []
    for name in roster:
        path = skill_md(args.root, name)
        if not os.path.exists(path):
            missing.append(name)
            continue
        rel = os.path.relpath(path, args.root)
        digest = sha256_file(path)
        prev = lock["skills"].get(name)
        entry = {
            "source": args.source,
            "sourceType": "npm",
            "package": "hyperframes",
            "version": args.version,
            "skillPath": rel,
            "computedHash": digest,
        }
        if prev is None:
            added.append(name)
        elif prev.get("computedHash") != digest or prev.get("version") != args.version:
            updated.append(name)
        lock["skills"][name] = entry

    # Re-hash everything else already in the lock so the file is always true.
    restated = []
    for name, entry in lock["skills"].items():
        if name in roster:
            continue
        rel = resolve(args.root, name, entry)
        path = os.path.join(args.root, rel)
        if os.path.exists(path):
            digest = sha256_file(path)
            if entry.get("skillPath") != rel or entry.get("computedHash") != digest:
                entry["skillPath"] = rel
                entry["computedHash"] = digest
                restated.append(name)
        else:
            entry["computedHash"] = None
            restated.append(name + " (file absent)")

    write_lock(args.lock, lock)

    print("  ok   skills-lock.json: %d entries (%d hyperframes @ %s)"
          % (len(lock["skills"]), len([n for n in roster if n in lock["skills"]]), args.version))
    for label, items in (("added", added), ("updated", updated), ("re-hashed", restated)):
        if items:
            print("       %-9s %s" % (label + ":", ", ".join(sorted(items))))
    if missing:
        print("  warn missing from .claude/skills: %s" % ", ".join(missing))
        return 1
    return 0


def cmd_verify(args):
    lock = load_lock(args.lock)
    if not lock["skills"]:
        print("  warn skills-lock.json has no entries - run: hf_pin.sh install")
        return 1
    bad, gone, ok = [], [], 0
    for name, entry in sorted(lock["skills"].items()):
        rel = resolve(args.root, name, entry)
        path = os.path.join(args.root, rel)
        if not os.path.exists(path):
            gone.append(name)
            continue
        if sha256_file(path) != entry.get("computedHash"):
            bad.append(name)
        else:
            ok += 1
    print("  ok   %d skill(s) match skills-lock.json" % ok)
    for name in gone:
        print("  warn %s: listed in the lock but not on disk" % name)
    for name in bad:
        print("  FAIL %s: SKILL.md bytes differ from the lock" % name)
    if bad:
        print("")
        print("  A skill was hand-edited, or the pin moved without re-locking.")
        print("  Re-install through the CLI instead of editing:")
        print("      workflows/scripts/hf_pin.sh install")
        return 1
    return 1 if gone else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--lock", required=True)
    ap.add_argument("--roster")
    ap.add_argument("--source")
    ap.add_argument("--version")
    ap.add_argument("--verify", action="store_true")
    args = ap.parse_args()
    sys.exit(cmd_verify(args) if args.verify else cmd_update(args))


if __name__ == "__main__":
    main()
