import { Easing } from "remotion";

export const FPS = 30;
export const WIDTH = 1920;
export const HEIGHT = 1080;

// Scene timing in frames (30 fps). Matches the storyboard deck.
export const SCENES = {
  raw: { from: 0, duration: 90 }, //        0:00–0:03 Raw screen recording
  transform: { from: 90, duration: 60 }, // 0:03–0:05 Transformation
  reveal: { from: 150, duration: 150 }, //  0:05–0:10 Product reveal
  connect: { from: 300, duration: 150 }, // 0:10–0:15 Connect & organize
  ai: { from: 450, duration: 150 }, //      0:15–0:20 AI wow moment
  benefit: { from: 600, duration: 120 }, // 0:20–0:24 Business benefit
  cta: { from: 720, duration: 90 }, //      0:24–0:27 Final frame / CTA
} as const;

export const TOTAL_FRAMES = 810;

export const C = {
  bgDeep: "#050817",
  bgNavy: "#0A1030",
  sidebar: "#0E1433",
  sidebarActive: "#1D2657",
  panel: "#FFFFFF",
  appBg: "#F3F5FB",
  border: "#E4E8F2",
  text: "#0F1530",
  textMuted: "#6B7391",
  violet: "#6D4AFF",
  blue: "#3B6BFF",
  cyan: "#22D3EE",
  green: "#22C55E",
  red: "#EF4444",
  white: "#FFFFFF",
};

export const GRADIENT = `linear-gradient(90deg, ${C.violet} 0%, ${C.blue} 55%, ${C.cyan} 100%)`;
export const FONT = `Inter, "Inter Display", "Helvetica Neue", Arial, sans-serif`;

// Smooth "product video" easing
export const EASE = Easing.bezier(0.22, 1, 0.36, 1);
export const EASE_IN_OUT = Easing.bezier(0.65, 0, 0.35, 1);
