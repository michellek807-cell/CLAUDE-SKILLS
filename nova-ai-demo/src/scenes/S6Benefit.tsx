import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { pop, tween } from "../anim";
import { Dashboard } from "../components/Dashboard";
import { Icon } from "../components/Icon";
import { BrandBackground, Screen } from "../components/Stage";
import { C, FONT } from "../theme";

// 0:20–0:24 — pull back to the full dashboard; three benefits appear in sequence.
const BENEFITS = [
  { a: "Less", b: "searching", icon: "search", color: C.cyan },
  { a: "Fewer", b: "manual steps", icon: "zap", color: "#A78BFA" },
  { a: "More", b: "clarity", icon: "chart", color: "#60A5FA" },
];

export const S6Benefit: React.FC = () => {
  const f = useCurrentFrame();
  const pull = tween(f, 0, 40, 1.04, 0.82);
  const cy = 540 + (450 - 540) * tween(f, 0, 40);

  return (
    <AbsoluteFill>
      <BrandBackground />
      <Screen cx={960} cy={cy} scale={pull}>
        <Dashboard chartProgress={tween(f, 8, 70)} />
      </Screen>
      <div style={{ position: "absolute", left: 0, right: 0, top: 800, display: "flex", justifyContent: "center", gap: 30, fontFamily: FONT }}>
        {BENEFITS.map((b, i) => {
          const a = pop(f, 26 + i * 16, 15);
          return (
            <div
              key={b.b}
              style={{
                width: 480,
                height: 150,
                borderRadius: 24,
                background: "rgba(10,16,48,0.92)",
                border: `2px solid ${b.color}`,
                boxShadow: `0 0 40px ${b.color}55`,
                display: "flex",
                alignItems: "center",
                gap: 28,
                paddingLeft: 36,
                boxSizing: "border-box",
                color: "#fff",
                opacity: a,
                transform: `translateY(${(1 - a) * 40}px)`,
              }}
            >
              <Icon name={b.icon} size={64} color={b.color} stroke={2.4} />
              <div style={{ lineHeight: 1.1 }}>
                <div style={{ fontSize: 40, fontWeight: 800 }}>{b.a}</div>
                <div style={{ fontSize: 34, fontWeight: 600, color: "#D6DBF5" }}>{b.b}</div>
              </div>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
