import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { press } from "../anim";
import { Cursor } from "../components/Cursor";
import { Dashboard } from "../components/Dashboard";
import { Screen } from "../components/Stage";
import { FONT } from "../theme";

// 0:00–0:03 — intentionally plain: static capture, linear cursor, no polish.
export const RAW_CURSOR_END = { x: 1150, y: 398 };
export const RAW_SCALE = 1.2; // 1440x900 → 1728x1080, pillarboxed like a raw capture

export const S1Raw: React.FC = () => {
  const f = useCurrentFrame();
  // Linear (un-eased) cursor drift — on purpose.
  const x = interpolate(f, [0, 50], [760, RAW_CURSOR_END.x], { extrapolateRight: "clamp" });
  const y = interpolate(f, [0, 50], [620, RAW_CURSOR_END.y], { extrapolateRight: "clamp" });
  const tag = interpolate(f, [6, 14], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{ background: "#111" }}>
      <Screen scale={RAW_SCALE} radius={0} shadow={0}>
        <Dashboard>
          <Cursor x={x} y={y} press={press(f, 55)} />
        </Dashboard>
      </Screen>
      <div style={{ position: "absolute", left: 120, bottom: 60, opacity: tag, fontFamily: FONT }}>
        <div style={{ display: "inline-block", background: "rgba(20,20,20,0.85)", color: "#fff", fontWeight: 800, fontSize: 44, padding: "10px 22px", borderRadius: 10 }}>RAW DEMO</div>
        <div style={{ marginTop: 10, background: "rgba(20,20,20,0.85)", color: "#ddd", fontSize: 22, padding: "8px 16px", borderRadius: 8 }}>
          No zoom • No graphics • No narration guidance
        </div>
      </div>
    </AbsoluteFill>
  );
};
