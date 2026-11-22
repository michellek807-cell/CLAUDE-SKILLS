import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { tween } from "../anim";
import { Cursor } from "../components/Cursor";
import { Dashboard, RECTS, Spotlight } from "../components/Dashboard";
import { Icon } from "../components/Icon";
import { GradientText, Screen } from "../components/Stage";
import { FONT } from "../theme";
import { RAW_CURSOR_END, RAW_SCALE } from "./S1Raw";

// 0:03–0:05 — freeze → slight darkening → 100%→106% push → spotlight active UI.
export const S2Transform: React.FC = () => {
  const f = useCurrentFrame();
  const darken = tween(f, 0, 10, 0, 0.25);
  const push = tween(f, 4, 50, 1, 1.06);
  const spot = tween(f, 12, 26, 0, 0.55);
  const glow = tween(f, 16, 30);
  const from = tween(f, 14, 26);
  const arrow = tween(f, 22, 32);
  const to = tween(f, 28, 40);
  const r = RECTS.recentItem0;

  return (
    <AbsoluteFill style={{ background: "#111" }}>
      <Screen scale={RAW_SCALE * push} radius={0} shadow={0} originX={r.x + r.w / 2} originY={r.y + r.h / 2} cx={960 + (r.x + r.w / 2 - 720) * RAW_SCALE} cy={540 + (r.y + r.h / 2 - 450) * RAW_SCALE}>
        <Dashboard>
          <Spotlight r={r} amount={spot} glow={glow} radius={12} />
          <Cursor x={RAW_CURSOR_END.x} y={RAW_CURSOR_END.y} />
        </Dashboard>
      </Screen>
      <AbsoluteFill style={{ background: `rgba(5,8,23,${darken})` }} />

      {/* dark band so the title reads over the UI */}
      <AbsoluteFill style={{ background: `linear-gradient(180deg, rgba(5,8,23,${0.92 * from}) 0%, rgba(5,8,23,${0.75 * from}) 30%, rgba(5,8,23,0) 45%)` }} />
      {/* FROM → TO title */}
      <div
        style={{
          position: "absolute",
          left: 0,
          right: 0,
          top: 90,
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          gap: 36,
          fontFamily: FONT,
          color: "#fff",
        }}
      >
        <div style={{ opacity: from, transform: `translateY(${(1 - from) * 20}px)`, textAlign: "right" }}>
          <div style={{ fontSize: 26, fontWeight: 600, letterSpacing: 4, color: "#B9C0E0" }}>FROM</div>
          <div style={{ fontSize: 60, fontWeight: 800 }}>Raw Recording</div>
        </div>
        <div style={{ opacity: arrow, transform: `translateX(${(1 - arrow) * -30}px)`, color: "#7C5CFF" }}>
          <Icon name="arrowRight" size={80} stroke={3} />
        </div>
        <div style={{ opacity: to, transform: `translateY(${(1 - to) * 20}px)` }}>
          <div style={{ fontSize: 26, fontWeight: 600, letterSpacing: 4, color: "#B9C0E0" }}>TO</div>
          <div style={{ fontSize: 60, fontWeight: 800 }}>
            <GradientText>Guided Product Story</GradientText>
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};
