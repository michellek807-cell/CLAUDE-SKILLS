import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { pop, tween, tweenIO } from "../anim";
import { Cursor } from "../components/Cursor";
import { Dashboard, RECTS } from "../components/Dashboard";
import { Icon } from "../components/Icon";
import { NovaMark } from "../components/Logo";
import { BrandBackground, Callout, Screen } from "../components/Stage";
import { C, FONT } from "../theme";

// 0:05–0:10 — logo-to-dashboard reveal, deliberate cursor move toward Connect Workspace.
export const S3Reveal: React.FC = () => {
  const f = useCurrentFrame();

  // Logo phase
  const draw = tween(f, 4, 30);
  const word = tween(f, 14, 34);
  const sub = tween(f, 24, 38);
  // Move logo to left column
  const move = tweenIO(f, 44, 70);
  const gx = 960 + (470 - 960) * move;
  const gy = 500 + (290 - 500) * move;
  const gs = 1 - 0.42 * move;

  // Dashboard enters
  const enter = tween(f, 56, 86);
  const cx = 2500 + (1300 - 2500) * enter;
  const rotY = -16 + 7 * enter;

  // Left column copy
  const head = tween(f, 64, 80);
  const checks = ["Organize", "Automate", "Grow"].map((_, i) => tween(f, 74 + i * 6, 86 + i * 6));

  // Cursor + callout
  const b = RECTS.connectBtn;
  const target = { x: b.x + b.w * 0.55, y: b.y + b.h * 0.6 };
  const cm = tweenIO(f, 92, 130);
  const cur = { x: 860 + (target.x - 860) * cm, y: 640 + (target.y - 640) * cm };
  const call = pop(f, 96);
  const line = tween(f, 104, 120);
  const hover = tween(f, 126, 138);

  return (
    <AbsoluteFill>
      <BrandBackground />

      {/* Logo group */}
      <div style={{ position: "absolute", left: gx, top: gy, transform: `translate(-50%, -50%) scale(${gs})`, fontFamily: FONT, color: "#fff", textAlign: "left" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 36 }}>
          <NovaMark size={170} draw={draw} />
          <div style={{ fontSize: 150, fontWeight: 800, letterSpacing: 2, clipPath: `inset(0 ${100 - word * 100}% 0 0)` }}>NOVA AI</div>
        </div>
        <div style={{ fontSize: 50, fontWeight: 500, color: "#C9D0F0", marginTop: 14, opacity: sub, transform: `translateY(${(1 - sub) * 14}px)` }}>AI Business Workspace</div>
      </div>

      <div style={{ position: "absolute", left: 120, top: 430, width: 620, fontFamily: FONT, color: "#fff" }}>
        <div style={{ fontSize: 54, fontWeight: 700, lineHeight: 1.15, opacity: head, transform: `translateY(${(1 - head) * 20}px)` }}>
          One workspace for a more productive business.
        </div>
        <div style={{ marginTop: 40, display: "flex", flexDirection: "column", gap: 18 }}>
          {["Organize", "Automate", "Grow"].map((t, i) => (
            <div key={t} style={{ display: "flex", alignItems: "center", gap: 16, fontSize: 34, fontWeight: 500, opacity: checks[i], transform: `translateX(${(1 - checks[i]) * -20}px)` }}>
              <div style={{ width: 40, height: 40, borderRadius: 20, background: C.blue, display: "flex", alignItems: "center", justifyContent: "center" }}>
                <Icon name="check" size={24} stroke={3} color="#fff" />
              </div>
              {t}
            </div>
          ))}
        </div>
      </div>

      {enter > 0 && (
        <Screen cx={cx} cy={540} scale={0.72} rotateY={rotY} rotateX={2 * enter}>
          <Dashboard hoverConnect={hover}>
            {/* connector line from callout to button */}
            <div style={{ position: "absolute", left: target.x - 2, top: b.y + b.h + 6, width: 4, height: 90 * line, background: C.cyan, borderRadius: 2, boxShadow: `0 0 12px ${C.cyan}`, zIndex: 39 }} />
            <Callout text="ONE WORKSPACE" x={target.x - 40} y={b.y + b.h + 130} progress={call} size={40} />
            {f >= 88 && <Cursor x={cur.x} y={cur.y} scale={1.3} opacity={tween(f, 88, 94)} />}
          </Dashboard>
        </Screen>
      )}
    </AbsoluteFill>
  );
};
