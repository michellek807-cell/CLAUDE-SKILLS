import React from "react";
import { C, FONT } from "../theme";

// Fictional "Nova AI" mark: a gradient N built from three strokes.
export const NovaMark: React.FC<{ size?: number; draw?: number }> = ({ size = 64, draw = 1 }) => {
  const len = 100;
  return (
    <svg width={size} height={size} viewBox="0 0 64 64" style={{ display: "block", overflow: "visible" }}>
      <defs>
        <linearGradient id="novaG" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor={C.violet} />
          <stop offset="55%" stopColor={C.blue} />
          <stop offset="100%" stopColor={C.cyan} />
        </linearGradient>
      </defs>
      <path
        d="M12 54 V12 L52 54 V12"
        fill="none"
        stroke="url(#novaG)"
        strokeWidth={11}
        strokeLinecap="round"
        strokeLinejoin="round"
        pathLength={len}
        strokeDasharray={len}
        strokeDashoffset={len * (1 - draw)}
      />
    </svg>
  );
};

export const NovaWordmark: React.FC<{ size?: number; color?: string }> = ({ size = 18, color = C.white }) => (
  <div style={{ display: "flex", alignItems: "center", gap: size * 0.5 }}>
    <NovaMark size={size * 1.3} />
    <span style={{ fontFamily: FONT, fontWeight: 800, fontSize: size, color, letterSpacing: 0.5 }}>NOVA AI</span>
  </div>
);
