import React from "react";

// macOS-style pointer. (x, y) is the tip. `press` 0..1 squeezes it; `ripple` 0..1 draws a click ring.
export const Cursor: React.FC<{ x: number; y: number; press?: number; ripple?: number; scale?: number; opacity?: number }> = ({
  x,
  y,
  press = 0,
  ripple = 0,
  scale = 1,
  opacity = 1,
}) => (
  <div style={{ position: "absolute", left: x, top: y, width: 0, height: 0, opacity, zIndex: 50, pointerEvents: "none" }}>
    {ripple > 0 && ripple < 1 && (
      <div
        style={{
          position: "absolute",
          left: -40 * ripple,
          top: -40 * ripple,
          width: 80 * ripple,
          height: 80 * ripple,
          borderRadius: "50%",
          border: `3px solid rgba(109,74,255,${1 - ripple})`,
          background: `rgba(109,74,255,${0.18 * (1 - ripple)})`,
        }}
      />
    )}
    <svg
      width={30 * scale}
      height={30 * scale}
      viewBox="0 0 24 24"
      style={{ position: "absolute", left: -3 * scale, top: -2 * scale, transform: `scale(${1 - press * 0.15})`, transformOrigin: "3px 2px", filter: "drop-shadow(0 3px 4px rgba(0,0,0,0.35))" }}
    >
      <path d="M3 2 L3 19 L7.5 14.8 L10.4 21.5 L13.4 20.2 L10.5 13.6 L16.8 13.6 Z" fill="#111" stroke="#fff" strokeWidth={1.4} strokeLinejoin="round" />
    </svg>
  </div>
);
