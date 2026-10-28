# Aura — 90-second SaaS ad (HyperFrames)

Portfolio piece built from the 13-panel "90-Second AI SaaS Product Demo Storyboard".
1920×1080, 30 fps, 90 s. Aura is a fictional product; every screen is rebuilt in HTML.

## Creative calls

- **Look:** a deep navy stage (`#050816`) with slowly orbiting blue/violet/cyan light and a perspective grid that scrolls the whole film. All UI is frosted glass (`.glass`, `.glass-dark` in `index.html`). Type is Outfit 800 for headlines and Inter for the UI. Accent gradient is `#4F7BFF → #9B5CFF`.
- **Glass folders are the motif:** they're the hero of scene 4, where records arc out of the four connected sources into Contacts / Projects / Files / Messages and the counters fill. They come back as the glass tabs in scene 10 ("Less searching / Fewer manual steps / More clarity") and as the three value folders in scene 12, which merge into the light that becomes the logo.
- **Transitions with a cause:** the hook's tool windows get sucked into one point that becomes the logo. The camera zooms through the dashboard into the app. The connect tiles lift and drop into the folders. It zooms through the Projects folder into the dashboard. The overdue row morphs into its project panel. Whip cuts left and right. The AI orb grows into the light that reveals the insights card. The folders converge into the end-card mark.
- **Cursor clicks cause the next thing:** Connect Account fills the progress bar, then the sources get green checks. Assign to Team checks the box, lights up the team and turns the status green. Send starts the AI. Book a Demo is the final click.
- **Presenter clip** (`assets/presenter.mp4`, 5 s, 9:16): it plays at 0.5× inside a tall glass frame in scene 11 ("Work from anywhere"). It's muted, because the clip has no audio and the voiceover carries the line.
- **Voiceover:** Kokoro TTS, voice `af_heart` at 0.95 speed, one file per storyboard line in `assets/vo/`. Swap in an ElevenLabs take by replacing the files with the same names. If a new take is longer, nudge its `data-start` in `index.html`.
- **SFX:** these are from the bundled Pixabay library (`assets/sfx/CREDITS.md`). Whooshes play on seams, clicks on real clicks, a pop on the badges, chime and notification sounds on state changes, a sparkle on the AI result, and a riser into a bass impact on the end-card logo.
- **No music bed:** there was no HeyGen sign-in for the music catalog. To add one, drop a track into `assets/` and add this to `index.html`: `<audio id="bgm" class="clip" src="assets/bgm.mp3" data-start="0" data-duration="90" data-track-index="13" data-volume="0.14">`.
- Timing follows the storyboard. The only change: scene 10 is 55–65 s and scenes 11–13 move up, so the CTA holds for 5 s instead of 3 s.

## What was measured vs. only looked at

- `npx hyperframes check` passes (0 errors). The audio was placed by measured file durations, but nobody has listened to it.
- I looked at the beat, seam and phone review sheets plus targeted frames. I fixed four problems: the scene 2 headline overlapped the dashboard, the scene 6 alert ring was on the wrong column, the scene 12 headline went past title-safe, and a hook subline showed early.

## Warnings kept on purpose

- `text_below_floor` stays on a few UI labels (sidebar, KPI captions, table headers). They are product chrome, not reading text.
- `dead_stretch` stays around 80–84 s: the scene 12 headline holds still while the voice reads it.

## Weakest shot / next steps

- Scene 11 uses a talking presenter with someone else's voice over her. A clip where she's looking at a phone or laptop, or a lip-synced HeyGen take, would land better.
- Scene 4 (folders) could get a slow 3D orbit of the folder row for even more depth.
