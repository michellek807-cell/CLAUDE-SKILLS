import React from "react";
import { interpolate, useCurrentFrame } from "remotion";
import { FONT } from "../theme";

// Narration lines from the storyboard, timed in absolute frames (30fps).
export const CAPTIONS = [
  { from: 4, to: 88, text: "Software demos can show the product…" },
  { from: 92, to: 148, text: "…but good product videos show people where to look—and why it matters." },
  { from: 155, to: 298, text: "Meet Nova, an AI workspace designed to bring your daily operations into one clear view." },
  { from: 305, to: 448, text: "Connect your workspace, and the information your team already uses becomes easier to organize and navigate." },
  { from: 455, to: 598, text: "Then let AI surface what needs attention and suggest the next step." },
  { from: 605, to: 718, text: "Less searching. Fewer manual steps. More clarity." },
  { from: 725, to: 806, text: "That’s the difference between recording software—and explaining its value." },
];

export const Captions: React.FC<{ startFrame?: number }> = ({ startFrame = 90 }) => {
  const f = useCurrentFrame();
  const line = CAPTIONS.find((c) => f >= c.from && f <= c.to && c.to > startFrame);
  if (!line || f < startFrame) return null;
  const o = interpolate(f, [line.from, line.from + 6, line.to - 6, line.to], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return (
    <div style={{ position: "absolute", left: 0, right: 0, bottom: 34, display: "flex", justifyContent: "center", opacity: o, zIndex: 100 }}>
      <div
        style={{
          maxWidth: 1400,
          padding: "12px 28px",
          borderRadius: 14,
          background: "rgba(5,8,23,0.72)",
          color: "#fff",
          fontFamily: FONT,
          fontSize: 32,
          fontWeight: 500,
          textAlign: "center",
          lineHeight: 1.3,
        }}
      >
        {line.text}
      </div>
    </div>
  );
};
