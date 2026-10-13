# Animated Shoe-Lift Spec Explainer — Higgsfield Package

Version 1 · October 13, 2026 · **Independent spec concept** for @MamaCarrieOfficial (not a commissioned American Heelers ad)

Built for Higgsfield's **video explainer** workflow:
- One style key, six 10-second blocks
- One voice take and one clip per block, assembled server-side

## Settings (recommended defaults, change any you like)

| Setting | Choice |
|---|---|
| Length | **60 seconds = 6 blocks.** Explainer only runs in whole minutes, so the 75s plan was tightened. |
| Aspect | 16:9 master (1280×720). Make a 9:16 version later as a separate run, not a crop. |
| Character | MamaCarrie host. Greets in Block 1 with mouth closed, cameo in Block 5, waves goodbye in Block 6. No lip-sync. |
| Style | Warm flat 2D editorial illustration (descriptor below) |
| Language | English |
| Subtitles | Off in Higgsfield. Add captions in CapCut using your Signature Captions style. |
| Voice | Your established MamaCarrie voice. ElevenLabs is fine; record the six lines separately. |

## Why animation fixes the old problems

- Walking is clearly illustrative, so it can't be mistaken for a clinical result.
- A cartoon walk avoids the AI gait errors: sliding feet, swapping feet, extra legs.
- The shoe is simplified, but its construction stays accurate to REF_C: original midsole, a black lift layer between midsole and outsole, original tread underneath.

**Continuity rules still apply:**
- The lift is always on the **LEFT** shoe.
- Rear view: screen-left. Front view: screen-right. Side view: nearest the camera, walking toward screen-left.
- Never mirror a clip.

## STYLE descriptor (paste identically into every block)

```
clean flat 2D editorial illustration, soft warm cream backgrounds, smooth charcoal outlines of even weight, solid flat fills with one gentle shadow tone, muted burgundy and warm gold accents, matte finish, calm uncluttered composition, non-photorealistic, illustrated, not a photo, no live-action, no realism
```

## Style key — mascot image (Nano Banana Pro / `nano_banana_2`, 16:9, 2k)

Attach your best MamaCarrie still as a reference for likeness only.

```
Make an Animated Explainer. Take only the visual render style and color grading of the input image(s); mix the styles if there is more than one image. Never use the characters, inscriptions, etc. from the input image(s) unless the instructions below ask you to. Use only the render style, and follow the user's instructions below:
clean flat 2D editorial illustration, soft warm cream backgrounds, smooth charcoal outlines of even weight, solid flat fills with one gentle shadow tone, muted burgundy and warm gold accents, matte finish, non-photorealistic, illustrated, not a photo, no live-action, no realism. Full-body character: MamaCarrie, a warm, confident, mature Black woman narrator modeled on the reference likeness, short natural hair as in the reference, wearing a tailored black blazer over a black top, small gold hoop earrings and a delicate gold cross necklace, calm knowing smile with mouth closed, looking at camera, centered, simple cream background. Recurring-character design. No text, no logos, no watermark.
```
Approve this image before anything else. Every clip uses it.

**Before you run it:** match her hair and features to your established MamaCarrie look. "Short natural hair" is only a placeholder.

---

## Narration (6 blocks, about 8–9 seconds each)

```
Block 1
Need a lift? Keep the shoes you already love. American Heelers adds an external lift to your own shoe, built to your specifications.
Block 2
Start at orthopedic shoe lift dot com. Fill out the order form with the correct side and the lift height your clinician recommends.
Block 3
Pack only the shoe that needs the lift, along with your printed form. Then follow the site's link to print a shipping label.
Block 4
At the workshop, the lift layer is built in between the midsole and the outsole, and the edges are finished to match.
Block 5
Your shoe comes back looking like yours, the same upper and the same laces, now with the lift built right into the sole.
Block 6
Every body is different, so confirm your lift with a qualified clinician. Learn more at orthopedic shoe lift dot com.
```
Pronunciation: "American **Heelers**", "orthopedic shoe lift dot com".

---

## Video prompts (Gemini Omni / `gemini_omni`, 10s, 720p, 16:9, attach the style key to every block)

For Blocks 1, 4 and 5, also attach `refs/REF_C_left_shoe_AFTER_lift.jpg` as a shape-only reference for the shoe.

```
Block 1
STYLE REFERENCE: Match the attached reference image EXACTLY. Replicate its look precisely: clean flat 2D editorial illustration, soft warm cream backgrounds, smooth charcoal outlines of even weight, solid flat fills with one gentle shadow tone, muted burgundy and warm gold accents, matte finish, calm uncluttered composition, non-photorealistic, illustrated, not a photo, no live-action, no realism. Every element below rendered in that identical style.
SCENE: MamaCarrie stands beside a small cream pedestal holding a single black running shoe, the LEFT shoe shown from its outer side with the toe pointing left. She greets the viewer with a warm open-hand gesture, mouth closed, then gestures toward the shoe.
MOTION: Gentle slow push-in from medium shot toward the shoe; soft easing; subtle idle breathing motion on the character.
AUDIO: Soft warm piano and light room tone only, no voice, dialogue, or narration.
NEGATIVE: color drift, photorealism, 3D render, lip-sync, talking mouth, captions, on-screen text, logos, watermark, second shoe, extra fingers.
```

```
Block 2
STYLE REFERENCE: Match the attached reference image EXACTLY. Replicate its look precisely: clean flat 2D editorial illustration, soft warm cream backgrounds, smooth charcoal outlines of even weight, solid flat fills with one gentle shadow tone, muted burgundy and warm gold accents, matte finish, calm uncluttered composition, non-photorealistic, illustrated, not a photo, no live-action, no realism. Every element below rendered in that identical style.
SCENE: A simplified illustrated smartphone held in one hand, its screen showing a plain blank form made of empty gray rectangles. A thumb taps the first box, then the form gently scrolls. The screen stays blank of words so real website footage can be placed over it in editing.
MOTION: Locked framing with a slight slow drift; smooth screen scroll; one tap ripple.
AUDIO: Soft piano continues, a gentle UI tap sound, no voice.
NEGATIVE: color drift, photorealism, 3D render, lip-sync, captions, readable text, letters, numbers, logos, watermark, extra fingers.
```

```
Block 3
STYLE REFERENCE: Match the attached reference image EXACTLY. Replicate its look precisely: clean flat 2D editorial illustration, soft warm cream backgrounds, smooth charcoal outlines of even weight, solid flat fills with one gentle shadow tone, muted burgundy and warm gold accents, matte finish, calm uncluttered composition, non-photorealistic, illustrated, not a photo, no live-action, no realism. Every element below rendered in that identical style.
SCENE: Overhead view of a kitchen table. Two hands place ONE black running shoe, the LEFT shoe with a normal unmodified sole, into a plain kraft shipping box next to a folded blank white sheet of paper, then fold the box flaps closed.
MOTION: Locked overhead camera; smooth, deliberate hand movements; box flaps close with a soft settle.
AUDIO: Soft piano, cardboard rustle and a gentle box-flap thump, no voice.
NEGATIVE: color drift, photorealism, 3D render, captions, readable text, labels, logos, watermark, second shoe, extra fingers.
```

```
Block 4
STYLE REFERENCE: Match the attached reference image EXACTLY. Replicate its look precisely: clean flat 2D editorial illustration, soft warm cream backgrounds, smooth charcoal outlines of even weight, solid flat fills with one gentle shadow tone, muted burgundy and warm gold accents, matte finish, calm uncluttered composition, non-photorealistic, illustrated, not a photo, no live-action, no realism. Every element below rendered in that identical style.
SCENE: Clean side-view diagram of the same black LEFT running shoe on a warm wooden workbench, toe pointing left. The sole gently separates into layers: the black midsole on top and the tread outsole below. A matte black lift layer, fullest under the heel and tapering slightly toward the toe, slides in between them, the layers close together, and a soft gold line traces along the finished edge.
MOTION: Locked side view; smooth exploded-diagram animation with soft easing; the upper never changes.
AUDIO: Soft piano, quiet workshop ambience, a gentle click as the layers join, no voice.
NEGATIVE: color drift, photorealism, 3D render, captions, on-screen text, numbers, measurements, logos, watermark, changing upper, mirrored shoe.
```

```
Block 5
STYLE REFERENCE: Match the attached reference image EXACTLY. Replicate its look precisely: clean flat 2D editorial illustration, soft warm cream backgrounds, smooth charcoal outlines of even weight, solid flat fills with one gentle shadow tone, muted burgundy and warm gold accents, matte finish, calm uncluttered composition, non-photorealistic, illustrated, not a photo, no live-action, no realism. Every element below rendered in that identical style.
SCENE: Side view, waist down, of an adult woman in ceil-blue scrub pants and black socks. Her LEFT side faces the viewer and she walks toward the left of frame with relaxed, even steps on a plain cream floor. Her LEFT shoe, nearest the viewer, has the black lift layer built into the sole; her RIGHT shoe is the same black running shoe with a normal sole. MamaCarrie watches warmly from the right edge of the frame, mouth closed.
MOTION: Locked camera; smooth, natural, simplified walk cycle with clear heel contact and toe-off; no speed changes.
AUDIO: Soft piano and light footsteps on a smooth floor, no voice.
NEGATIVE: color drift, photorealism, 3D render, lip-sync, captions, on-screen text, logos, watermark, limping, sliding feet, extra legs, lift on the wrong foot, mirrored shot.
```

```
Block 6
STYLE REFERENCE: Match the attached reference image EXACTLY. Replicate its look precisely: clean flat 2D editorial illustration, soft warm cream backgrounds, smooth charcoal outlines of even weight, solid flat fills with one gentle shadow tone, muted burgundy and warm gold accents, matte finish, calm uncluttered composition, non-photorealistic, illustrated, not a photo, no live-action, no realism. Every element below rendered in that identical style.
SCENE: MamaCarrie stands centered on a cream background with clear empty space on the left side of the frame for a title card. She places a hand over her heart, then gives a warm goodbye wave, mouth closed.
MOTION: Slow gentle pull-back; soft easing; subtle idle breathing.
AUDIO: Soft piano resolves to a warm final chord, no voice.
NEGATIVE: color drift, photorealism, 3D render, lip-sync, talking mouth, captions, on-screen text, logos, watermark, extra fingers.
```

---

## Add in CapCut after assembly

| Time | Overlay |
|---|---|
| 0:00–0:03 and 0:55–1:00 | "Independent spec concept • AI-generated animation" |
| 0:10–0:20 (Block 2) | Your real screen recording of the online order form, empty fields, status bar cropped, placed on the phone screen |
| 0:20–0:30 (Block 3) | Optional quick insert of the real USPS returns-label page |
| 0:40–0:50 (Block 5) | "Illustration only, not a clinical outcome" |
| 0:50–1:00 (Block 6) | Title card on the left: **orthopedicshoelift.com** · @MamaCarrieOfficial |
| Throughout | Captions from the final voice track, cream text on burgundy/charcoal panels |

## QC before calling it portfolio-ready

- [ ] Lift is on the LEFT shoe in Blocks 4 and 5; no mirrored clips
- [ ] Only one shoe in the box in Block 3
- [ ] MamaCarrie looks the same in Blocks 1, 5 and 6 and never lip-syncs
- [ ] No garbled text or invented logos in any clip
- [ ] No prices, delivery times or medical promises anywhere
- [ ] Each voice line fits inside its 10-second block; brand and URL pronounced correctly
- [ ] Exactly 60 seconds; watched start to finish with sound on a phone
