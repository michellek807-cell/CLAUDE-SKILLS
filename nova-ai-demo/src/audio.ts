// ─── AUDIO SETUP ────────────────────────────────────────────────
// Drop your files into /public and set the file names below.
// Leave a value as null to skip that track.
export const VOICEOVER: string | null = null; // e.g. "voiceover.mp3" (ElevenLabs, full 27s read)
export const MUSIC: string | null = null; //     e.g. "music.mp3"     (starts at 0:03)

// Sound-effect cues (frame @30fps → file in /public). Set file to enable.
export const SFX: { frame: number; file: string | null; label: string; volume: number }[] = [
  { frame: 55, file: null, label: "Quiet mouse click (raw demo)", volume: 0.5 },
  { frame: 92, file: null, label: "Subtle UI whoosh (transformation)", volume: 0.6 },
  { frame: 160, file: null, label: "Soft brand reveal", volume: 0.6 },
  { frame: 360, file: null, label: "Mouse click (Connect Accounts)", volume: 0.6 },
  { frame: 400, file: null, label: "Soft confirmation chime", volume: 0.5 },
  { frame: 500, file: null, label: "Low processing texture", volume: 0.4 },
  { frame: 535, file: null, label: "Completion tone", volume: 0.5 },
  { frame: 730, file: null, label: "Final CTA swell", volume: 0.5 },
];
