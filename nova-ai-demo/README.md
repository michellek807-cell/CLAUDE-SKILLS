# Nova AI — 25-Second SaaS Demo (Remotion)

A motion-graphics product demo built from the **NOVA AI SaaS Application Sample Storyboard**.
Everything (the Nova app UI, logo, cursor, callouts, captions) is drawn in code, so every word,
color, and timing can be changed and re-rendered in minutes.

- **Format:** 1920×1080, 30 fps, 27 seconds (810 frames)
- **Compositions:** `NovaDemo` (with burned-in captions) and `NovaDemoClean` (no captions)
- **Product:** fictional ("Nova AI") — sample interface for demonstration only

---

## 1. Quick start

```bash
cd nova-ai-demo
npm install
npm run studio      # opens Remotion Studio in your browser — scrub, preview, tweak
npm run render      # → out/nova-demo.mp4
npx remotion render NovaDemoClean out/nova-demo-clean.mp4   # caption-free version
```

---

## 2. Scene map (matches the storyboard slides)

| # | Time | Frames | Scene | File | What happens on screen |
|---|------|--------|-------|------|------------------------|
| 1 | 0:00–0:03 | 0–90 | Raw recording (before) | `src/scenes/S1Raw.tsx` | Flat capture, linear cursor, “RAW DEMO” tag. No polish on purpose. |
| 2 | 0:03–0:05 | 90–150 | Transformation | `src/scenes/S2Transform.tsx` | Freeze → darken → 100%→106% push → spotlight on active row. “FROM Raw Recording → TO Guided Product Story”. |
| 3 | 0:05–0:10 | 150–300 | Product reveal | `src/scenes/S3Reveal.tsx` | Logo draws on, slides left; dashboard swings in; “ONE WORKSPACE” callout; cursor glides to **Connect Workspace**. |
| 4 | 0:10–0:15 | 300–450 | Connect & organize | `src/scenes/S4Connect.tsx` | UI dims ~28%, connect modal pops, eased click with ripple, tools check off, CONNECT → SYNC → ORGANIZE. |
| 5 | 0:15–0:20 | 450–600 | AI wow moment | `src/scenes/S5AI.tsx` | “Ask Nova AI” drawer, prompt types in, data lines flow into the panel, AI Summary builds, “AI INSIGHT” callout, slow push. |
| 6 | 0:20–0:24 | 600–720 | Business benefit | `src/scenes/S6Benefit.tsx` | Pull back to full dashboard, chart redraws, three benefit cards land in sequence. |
| 7 | 0:24–0:27 | 720–810 | Final frame / CTA | `src/scenes/S7CTA.tsx` | Nova logo, tagline, **Book a Demo**, product shot, “FROM RAW SCREEN RECORDING ↓ TO PRODUCT STORY”. |

Scene timing lives in `src/theme.ts` (`SCENES`). Brand colors and font are there too.

---

## 3. Voiceover (ElevenLabs) — copy & paste

Generate as **one continuous read**, aiming for ~25–26 seconds. Suggested settings: a calm, confident
narrator voice · Stability ~45% · Similarity ~75% · Style ~15%.

```
Software demos can show the product…
but good product videos show people where to look — and why it matters.
Meet Nova, an AI workspace designed to bring your daily operations into one clear view.
Connect your workspace, and the information your team already uses becomes easier to organize and navigate.
Then let AI surface what needs attention and suggest the next step.
Less searching. Fewer manual steps. More clarity.
That's the difference between recording software — and explaining its value.
```

**To add it:** save the file as `public/voiceover.mp3`, then in `src/audio.ts` set
`VOICEOVER = "voiceover.mp3"`. If a line runs long or short, adjust that line’s `from`/`to`
in `src/components/Captions.tsx` and, if needed, the scene lengths in `src/theme.ts`.

---

## 4. Sound design cue sheet

Put files in `public/` and set the `file` name for each cue in `src/audio.ts`.

| Frame | Time | Cue | Notes |
|-------|------|-----|-------|
| 55 | 0:01.8 | Quiet mouse click | Raw demo — keep it dry, no reverb |
| 92 | 0:03.1 | Subtle UI whoosh | Transformation starts |
| 90+ | 0:03 → end | Music bed | `MUSIC = "music.mp3"` — fades in, lifts slightly at 0:20, fades out by 0:24 under the CTA |
| 160 | 0:05.3 | Soft brand reveal | Logo draw-on |
| 360 | 0:12.0 | Mouse click | “Connect Accounts” |
| 400 | 0:13.3 | Soft confirmation chime | Tools connected |
| 500 | 0:16.7 | Low processing texture | AI thinking |
| 535 | 0:17.8 | Completion tone | AI Summary appears |
| 730 | 0:24.3 | Final CTA swell | End card |

Mix target: narration always dominant; music around −20 to −24 dB under voice.

---

## 5. Easy edits

| Want to change… | Edit |
|---|---|
| Brand colors / font | `src/theme.ts` → `C`, `GRADIENT`, `FONT` |
| Product name / logo | `src/components/Logo.tsx` |
| Dashboard numbers, activity list, nav | `src/components/Dashboard.tsx` (`STATS`, `ACTIVITY`, `NAV`) |
| Tools in the connect modal | `src/scenes/S4Connect.tsx` (`TOOLS`) |
| AI prompt and summary items | `src/scenes/S5AI.tsx` (`PROMPT`, `ITEMS`) |
| Benefit cards | `src/scenes/S6Benefit.tsx` (`BENEFITS`) |
| CTA copy | `src/scenes/S7CTA.tsx` |
| Captions | `src/components/Captions.tsx` |

**Using a real client screen recording instead of the built-in UI:** replace `<Dashboard />` in a scene with
`<OffthreadVideo src={staticFile("client-recording.mp4")} />` (from `remotion`) inside the same `<Screen>`
wrapper. Spotlights, callouts, and cursor overlays keep working on top.

---

## 6. Rendering tips

- If Remotion can’t download its own headless browser, pass your Chrome path:
  `npx remotion render NovaDemo out/nova-demo.mp4 --browser-executable="/path/to/chrome"`
- The UI uses the **Inter** font. Install it locally (free from Google Fonts) for an exact match;
  otherwise it falls back to Helvetica/Arial.
- For LinkedIn/website: use `NovaDemo`. For paid ads where platforms add their own captions: use `NovaDemoClean`.
