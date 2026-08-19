#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""edl_export.py - replay the cut list against the raw footage as EDIT POINTS.

LOCK: on the editing-app path, skip the flat render entirely. A flattened mp4
throws away every boundary the cut list knows about; what you want on the
timeline is N trimmable clips off the ORIGINAL file, so you can nudge any cut
by two frames without going back to a script. Time to timeline is the metric.

Writes, all from cut/cutlist.json + the canonical transcript:

  <job>.fcp7.xml   FCP7 / xmeml v5 - Premiere Pro, Resolve, FCP, Media Composer
  <job>.edl        CMX3600 - the universal fallback
  <job>.capcut/    CapCut draft folder (draft_content.json)
  <job>.cuts.md    the razor list, for cutting by hand in anything else
  <job>.srt        the canonical transcript, cut-relative
"""
import argparse
import datetime
import json
import os
import sys
import uuid
from fractions import Fraction
from xml.sax.saxutils import escape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vslib  # noqa: E402

# CapCut's draft schema moves between releases. This is the version these files
# were written against; if CapCut refuses the draft, check this first.
CAPCUT_SCHEMA = "13.0.0"


def ntsc_timebase(fps):
    """FCP7 XML wants an integer timebase plus an ntsc flag."""
    f = float(fps)
    for base, is_ntsc in ((24, True), (24, False), (25, False), (30, True), (30, False),
                          (50, False), (60, True), (60, False)):
        target = base * 1000.0 / 1001.0 if is_ntsc else float(base)
        if abs(f - target) < 0.01:
            return base, is_ntsc
    return int(round(f)), False


# ------------------------------------------------------------- FCP7 / xmeml --
def write_fcp7(path, cutlist, job, raw_abs):
    grid = vslib.FrameGrid(cutlist["source"]["fps"])
    timebase, is_ntsc = ntsc_timebase(float(grid.fps))
    ntsc = "TRUE" if is_ntsc else "FALSE"
    raw = job["raw"]
    w = raw.get("width") or 1920
    h = raw.get("height") or 1080
    src_frames = max(1, grid.frame_of(raw["duration"]))
    name = job["name"]
    segs = cutlist["segments"]
    total = sum(s["frames"] for s in segs)
    file_url = "file://" + raw_abs.replace(" ", "%20")

    def rate():
        return "<rate><timebase>%d</timebase><ntsc>%s</ntsc></rate>" % (timebase, ntsc)

    def file_el(first):
        if not first:
            return '<file id="file-1"/>'
        return (
            '<file id="file-1">'
            "<name>%s</name>"
            "<pathurl>%s</pathurl>"
            "%s"
            "<duration>%d</duration>"
            "<timecode>%s<string>00:00:00:00</string><frame>0</frame>"
            "<displayformat>NDF</displayformat></timecode>"
            "<media>"
            "<video><samplecharacteristics>%s<width>%d</width><height>%d</height>"
            "<pixelaspectratio>square</pixelaspectratio></samplecharacteristics></video>"
            "<audio><samplecharacteristics><depth>16</depth><samplerate>48000</samplerate>"
            "</samplecharacteristics><channelcount>2</channelcount></audio>"
            "</media></file>"
        ) % (escape(os.path.basename(raw_abs)), escape(file_url), rate(),
             src_frames, rate(), rate(), w, h)

    v_items, a_items = [], []
    t = 0
    for s in segs:
        i = s["i"]
        vid, aid = "clip-v%d" % i, "clip-a%d" % i
        start, end = t, t + s["frames"]
        links = (
            '<link><linkclipref>%s</linkclipref><mediatype>video</mediatype>'
            "<trackindex>1</trackindex><clipindex>%d</clipindex></link>"
            '<link><linkclipref>%s</linkclipref><mediatype>audio</mediatype>'
            "<trackindex>1</trackindex><clipindex>%d</clipindex><groupindex>1</groupindex></link>"
        ) % (vid, i + 1, aid, i + 1)
        common = ("<name>%s</name><duration>%d</duration>%s"
                  "<start>%d</start><end>%d</end><in>%d</in><out>%d</out>"
                  "<enabled>TRUE</enabled>"
                  % (escape("%s %03d" % (name, i + 1)), src_frames, rate(),
                     start, end, s["src_in_frame"], s["src_out_frame"]))
        v_items.append('<clipitem id="%s">%s%s%s</clipitem>'
                       % (vid, common, file_el(i == 0), links))
        a_items.append('<clipitem id="%s">%s%s'
                       "<sourcetrack><mediatype>audio</mediatype><trackindex>1</trackindex>"
                       "</sourcetrack>%s</clipitem>"
                       % (aid, common, '<file id="file-1"/>', links))
        t = end

    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        "<!DOCTYPE xmeml>\n"
        '<xmeml version="5">\n'
        '<sequence id="sequence-1"><uuid>%s</uuid>'
        "<name>%s</name><duration>%d</duration>%s"
        "<timecode>%s<string>00:00:00:00</string><frame>0</frame>"
        "<displayformat>NDF</displayformat></timecode>"
        "<media>"
        "<video><format><samplecharacteristics>%s<width>%d</width><height>%d</height>"
        "<pixelaspectratio>square</pixelaspectratio></samplecharacteristics></format>"
        "<track>%s</track></video>"
        "<audio><format><samplecharacteristics><depth>16</depth><samplerate>48000</samplerate>"
        "</samplecharacteristics></format>"
        '<track currentExplodedTrackIndex="0" premiereTrackType="Stereo">%s</track></audio>'
        "</media></sequence>\n"
        "</xmeml>\n"
    ) % (uuid.uuid4(), escape(job.get("title") or name), total, rate(), rate(),
         rate(), w, h, "".join(v_items), "".join(a_items))

    with open(path, "w", encoding="utf-8") as fh:
        fh.write(xml)
    return total


# ------------------------------------------------------------------- CMX3600 --
def write_edl(path, cutlist, job):
    grid = vslib.FrameGrid(cutlist["source"]["fps"])
    fps = float(grid.fps)
    reel = "AX"
    src_name = os.path.basename(job["raw"]["file"])
    lines = ["TITLE: %s" % (job.get("title") or job["name"]), "FCM: NON-DROP FRAME", ""]
    for s in cutlist["segments"]:
        lines.append("%03d  %-8s V     C        %s %s %s %s"
                     % (s["i"] + 1, reel,
                        vslib.smpte(s["src_in"], fps), vslib.smpte(s["src_out"], fps),
                        vslib.smpte(s["out_in"], fps), vslib.smpte(s["out_out"], fps)))
        lines.append("%03d  %-8s AA    C        %s %s %s %s"
                     % (s["i"] + 1, reel,
                        vslib.smpte(s["src_in"], fps), vslib.smpte(s["src_out"], fps),
                        vslib.smpte(s["out_in"], fps), vslib.smpte(s["out_out"], fps)))
        lines.append("* FROM CLIP NAME: %s" % src_name)
        lines.append("")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


# -------------------------------------------------------------- CapCut draft --
def write_capcut(dirpath, cutlist, job, raw_abs):
    """A CapCut draft folder: drop it in CapCut's Drafts directory and open it.

    Times are microseconds. Written against draft schema %s - if CapCut rejects
    it after an update, that constant is the thing to revisit. The XML above is
    the path that does not rot.
    """
    os.makedirs(dirpath, exist_ok=True)
    us = lambda t: int(round(float(t) * 1_000_000))  # noqa: E731
    raw = job["raw"]
    grid = vslib.FrameGrid(cutlist["source"]["fps"])
    segs = cutlist["segments"]
    total = us(segs[-1]["out_out"])
    vid_mat = str(uuid.uuid4()).upper()
    aud_mat = str(uuid.uuid4()).upper()

    def seg_entry(material_id, s):
        return {
            "id": str(uuid.uuid4()).upper(),
            "material_id": material_id,
            "source_timerange": {"start": us(s["src_in"]), "duration": us(s["dur"])},
            "target_timerange": {"start": us(s["out_in"]), "duration": us(s["dur"])},
            "speed": 1.0,
            "volume": 1.0,
            "visible": True,
            "enable_adjust": True,
            "extra_material_refs": [],
        }

    draft = {
        "id": str(uuid.uuid4()).upper(),
        "version": CAPCUT_SCHEMA,
        "duration": total,
        "fps": float(grid.fps),
        "canvas_config": {"width": raw.get("width") or 1920,
                          "height": raw.get("height") or 1080, "ratio": "original"},
        "materials": {
            "videos": [{
                "id": vid_mat,
                "type": "video",
                "path": raw_abs,
                "material_name": os.path.basename(raw_abs),
                "duration": us(raw["duration"]),
                "width": raw.get("width") or 1920,
                "height": raw.get("height") or 1080,
                "has_audio": True,
            }],
            "audios": [{
                "id": aud_mat,
                "type": "extract_music",
                "path": raw_abs,
                "name": os.path.basename(raw_abs),
                "duration": us(raw["duration"]),
            }],
        },
        "tracks": [
            {"id": str(uuid.uuid4()).upper(), "type": "video", "attribute": 0,
             "segments": [seg_entry(vid_mat, s) for s in segs]},
            {"id": str(uuid.uuid4()).upper(), "type": "audio", "attribute": 0,
             "segments": [seg_entry(aud_mat, s) for s in segs]},
        ],
    }
    with open(os.path.join(dirpath, "draft_content.json"), "w", encoding="utf-8") as fh:
        json.dump(draft, fh, indent=1, ensure_ascii=False)

    meta = {
        "draft_id": draft["id"],
        "draft_name": job.get("title") or job["name"],
        "draft_fold_path": os.path.abspath(dirpath),
        "draft_timeline_materials_size": 0,
        "tm_draft_create": int(datetime.datetime.now().timestamp() * 1000),
        "tm_draft_modified": int(datetime.datetime.now().timestamp() * 1000),
        "draft_removable_storage_device": "",
        "draft_materials": [{"type": 0, "value": [{"file_Path": raw_abs,
                                                   "metetype": "video"}]}],
    }
    with open(os.path.join(dirpath, "draft_meta_info.json"), "w", encoding="utf-8") as fh:
        json.dump(meta, fh, indent=1, ensure_ascii=False)


# ------------------------------------------------------------- razor list ----
def write_cuts_md(path, cutlist, job):
    grid = vslib.FrameGrid(cutlist["source"]["fps"])
    fps = float(grid.fps)
    st = cutlist["stats"]
    L = [
        "# %s - cut list" % (job.get("title") or job["name"]),
        "",
        "%d segments off `%s`. %s of source becomes %s (%.1f%% removed)."
        % (st["segments"], os.path.basename(job["raw"]["file"]),
           vslib.tc(st["source_duration"]), vslib.tc(st["output_duration"]), st["removed_pct"]),
        "",
        "Every row is a KEEP. Everything between rows is thrown away.",
        "Source timecode is %s fps non-drop." % ("%.3f" % fps),
        "",
        "| # | src in | src out | length | timeline in | first words |",
        "|--:|---|---|---:|---|---|",
    ]
    words = None
    wpath = os.path.join(os.path.dirname(os.path.dirname(path)), "transcript", "words.json")
    if os.path.exists(wpath):
        words = vslib.read_json(wpath)["words"]
    for s in cutlist["segments"]:
        head = ""
        if words and s["words"]:
            head = " ".join(words[i]["w"] for i in s["words"][:7])
            if len(s["words"]) > 7:
                head += " ..."
        L.append("| %d | `%s` | `%s` | %.2fs | `%s` | %s |"
                 % (s["i"] + 1, vslib.smpte(s["src_in"], fps), vslib.smpte(s["src_out"], fps),
                    s["dur"], vslib.smpte(s["out_in"], fps), head))
    L += ["", "## What was removed", "",
          "| src in | src out | length | why |", "|---|---|---:|---|"]
    for r in cutlist.get("removed", []):
        L.append("| `%s` | `%s` | %.2fs | %s |"
                 % (vslib.smpte(r["src_in"], fps), vslib.smpte(r["src_out"], fps),
                    r["dur"], r["reason"]))
    L.append("")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L))


# -------------------------------------------------------------------- SRT ----
def srt_time(t):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return "%02d:%02d:%02d,%03d" % (h, m, s, ms)


def write_srt(path, transcript):
    L = []
    for i, seg in enumerate(transcript["segments"], 1):
        L += [str(i), "%s --> %s" % (srt_time(seg["s"]), srt_time(seg["e"])), seg["text"], ""]
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--job-dir", required=True)
    ap.add_argument("--targets", default="fcp7,edl,capcut,cuts,srt")
    a = ap.parse_args()

    job_dir = os.path.abspath(a.job_dir)
    job = vslib.read_json(os.path.join(job_dir, "job.json"))
    cutlist = vslib.read_json(os.path.join(job_dir, "cut", "cutlist.json"))
    name = job["name"]
    raw_abs = os.path.abspath(os.path.join(job_dir, job["raw"]["file"]))
    cut_dir = os.path.join(job_dir, "cut")
    targets = set(t.strip() for t in a.targets.split(",") if t.strip())

    vslib.step("handoff: %d cuts as edit points on the original file" % len(cutlist["segments"]))

    if "fcp7" in targets:
        p = os.path.join(cut_dir, "%s.fcp7.xml" % name)
        frames = write_fcp7(p, cutlist, job, raw_abs)
        vslib.ok("cut/%s.fcp7.xml  %d frames, %d clips - Premiere / Resolve / FCP"
                 % (name, frames, len(cutlist["segments"])))
    if "edl" in targets:
        p = os.path.join(cut_dir, "%s.edl" % name)
        write_edl(p, cutlist, job)
        vslib.ok("cut/%s.edl  CMX3600" % name)
    if "capcut" in targets:
        p = os.path.join(cut_dir, "%s.capcut" % name)
        write_capcut(p, cutlist, job, raw_abs)
        vslib.ok("cut/%s.capcut/  draft schema %s" % (name, CAPCUT_SCHEMA))
    if "cuts" in targets:
        p = os.path.join(cut_dir, "%s.cuts.md" % name)
        write_cuts_md(p, cutlist, job)
        vslib.ok("cut/%s.cuts.md  razor list" % name)
    if "srt" in targets:
        tp = os.path.join(job_dir, "outputs", "%s.transcript.json" % name)
        if os.path.exists(tp):
            p = os.path.join(job_dir, "outputs", "%s.srt" % name)
            write_srt(p, vslib.read_json(tp))
            vslib.ok("outputs/%s.srt  from the canonical transcript, never re-transcribed" % name)
        else:
            vslib.warn("no canonical transcript yet - run make_transcript.py for the srt")


if __name__ == "__main__":
    main()
