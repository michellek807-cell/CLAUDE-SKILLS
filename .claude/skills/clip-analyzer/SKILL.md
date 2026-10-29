---
name: clip-analyzer
description: |
  Analyze a short-form clip (Reel, TikTok, Short, or a screen-recorded demo of a clipping tool) and break it down so Michelle can reproduce it in her clipping career. Two modes: TOOL BREAKDOWN when the clip shows or was made by a clipping tool (identify the tool, list every feature visible, map it to a repeatable workflow) and CLIP BREAKDOWN when the clip is a finished short (hook, cut points, captions, pacing, retention mechanics, and a rebuild recipe). Use when the user says "analyze this clip", "break down this tool", "what tool made this", "how do I recreate this clip", "clipping tool", "clipping career", or shares a video / link and asks what makes it work. NOT for generating new video (use higgsfield-generate or seedance skills) and NOT for thumbnails (use higgsfield-youtube-thumbnail).
argument-hint: "<clip file or URL> [--mode tool|clip|both] [--for mamacarrie|hmam|client]"
allowed-tools: Bash, Read, WebSearch, WebFetch
---

# Clip Analyzer

Turn one clip into (1) a tool breakdown you can act on and (2) a rebuild recipe you can run tonight.

## Step 0. Get the clip into a readable form

The clip must be a file, a URL, or a described screenshot sequence. If none is present, ask once for one of these and stop:

- Upload the MP4 or MOV directly in the chat.
- Paste the public link (TikTok, Instagram, YouTube, X, Drive link set to "anyone with link").
- Or paste the tool name plus 3 to 5 screenshots of its screens.

Never guess the tool or the content from an empty message.

When a file is available, pull the facts with ffmpeg before watching:

```bash
# Duration, resolution, fps, audio presence
ffprobe -v error -show_entries format=duration -show_entries stream=codec_type,width,height,r_frame_rate -of default=nw=1 "$CLIP"

# One frame per second for a visual skim (into the scratchpad, never into the repo)
mkdir -p "$OUT/frames" && ffmpeg -v error -i "$CLIP" -vf fps=1 "$OUT/frames/f_%03d.jpg"

# Scene-change timestamps = candidate cut points
ffmpeg -v error -i "$CLIP" -vf "select='gt(scene,0.3)',showinfo" -f null - 2>&1 | grep -o 'pts_time:[0-9.]*' | cut -d: -f2

# Audio only, for transcription (16 kHz mono WAV)
ffmpeg -v error -i "$CLIP" -vn -ac 1 -ar 16000 "$OUT/audio.wav"
```

Read the frames with the Read tool (they are images). Transcribe audio if a speech-to-text tool is available; otherwise read the burned-in captions from frames.

## Step 1. Decide the mode

| What the clip is | Mode | Deliverable |
|---|---|---|
| Screen recording or ad showing a clipping / captioning app | **tool** | Tool breakdown (Section A) |
| A finished short from a podcast, interview, or talking-head | **clip** | Clip breakdown + rebuild recipe (Section B) |
| A finished short that visibly carries a tool watermark or template | **both** | A then B |

Default to **both** when unsure. Say which mode you chose in one line.

## Section A. Tool breakdown (for a clipping tool)

Identify the tool from the UI. Check `references/clipping-tools.md` for the fingerprints (caption styles, layout, watermarks, export screens). If identification is uncertain, say so and give the top two candidates with the distinguishing clue to look for.

Then produce this exact structure:

1. **What the tool is.** One sentence. Category: auto-clipper, caption tool, editor, scheduler, or clipping marketplace.
2. **Every feature visible in the clip.** Bullet per feature, with the timestamp where it appears. Include anything implied by the UI even if not clicked.
3. **The workflow it implies.** Numbered, input to export. Where does the long video come from, what does the AI decide, what does the human decide, what gets exported, where does it post.
4. **What it does well and where it breaks.** Be honest. Auto-clippers miss context, over-crop faces, and produce bland hooks. Name the specific weakness this clip hides.
5. **Fit for Michelle.** Map to her three lanes:
   - **MamaCarrie** (talking-head wisdom clips, burgundy / gold / cream captions, warm pacing).
   - **How Medications Are Made** (documentary B-roll, factual captions, no sensationalism).
   - **Client clipping** (podcasters and creators paying per clip or per view).
   Say which lane the tool serves, and which it does not.
6. **Cost reality.** Do not quote prices from memory. Run one WebSearch for the current plan page and quote the plan names and limits with the date checked. If search is unavailable, write "verify current pricing at <official URL>" instead of a number.
7. **Day-one setup checklist.** What to connect, what to upload, what defaults to change, and the first test to run.

## Section B. Clip breakdown (for a finished short)

Produce a timed table first, then the analysis.

**Timed table.** One row per beat. Columns: `time`, `visual`, `audio / spoken line`, `caption text`, `what it does for retention`. Beats are typically 0 to 1 s (hook), 1 to 3 s (promise), body (cuts every 2 to 4 s), and the last 2 s (loop or CTA).

**Then analyze seven things:**

1. **Hook.** Quote the first spoken line and first on-screen text. Classify it: curiosity gap, bold claim, direct address, pattern interrupt, or mid-sentence start. Say why it stops the scroll.
2. **Cut rhythm.** Average seconds per cut from the ffmpeg scene list. Jump cuts, zoom punches, B-roll inserts, or a single take.
3. **Captions.** Style (word-by-word, phrase, karaoke highlight), font family guess, color, position, animation, emoji use. Whether the caption is readable with sound off.
4. **Framing.** 9:16 from a 16:9 source? Auto-reframe on a face, split screen, or a static center crop? Headroom and safe zones.
5. **Audio.** Music under speech, SFX on cuts, silence removed, loudness. Note any trending sound.
6. **Ending.** Hard stop, loop to the hook, verbal CTA, or on-screen CTA. What the viewer is told to do.
7. **Why it got views.** One paragraph. Emotion, specificity, and the single idea the clip carries. Say plainly if it is the creator's fame doing the work rather than the edit.

**Rebuild recipe.** A numbered list Michelle can follow in CapCut or the identified tool, ending with export settings (1080x1920, 30 fps, H.264, under 60 s for Reels and Shorts unless the platform target says otherwise). Include three alternative hooks written in the MamaCarrie voice when the lane is MamaCarrie, or three factual hooks when the lane is How Medications Are Made.

## Rules

- Describe only what is in the frames and audio. Mark inferences with "likely".
- Never claim a view count, revenue, or payout you did not read from the clip or a cited page.
- Keep the breakdown under 700 words plus the two tables. Michelle learns from checklists and tables, not essays.
- Write all extracted frames and audio to the scratchpad directory. Do not commit media to this repo.
- Match MamaCarrie brand rules when writing captions or hooks: warm, direct, never judgmental, burgundy #6B1F2A, gold #C9A24A, cream #F3E9D8.
- For medication content, factual framing only. Never include manufacturing steps that could be followed.
- If the clip contains another creator's content, note that reposting without a clipping agreement or permission is a copyright and platform-policy risk. See `references/clipping-career.md`.

## References

- `references/clipping-tools.md`: fingerprints and feature maps for the common clipping and captioning tools.
- `references/clipping-career.md`: how paid clipping works, intake questions for clients, and a per-clip quality checklist.
