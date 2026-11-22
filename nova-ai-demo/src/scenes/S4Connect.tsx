import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { pop, press, ripple, tween, tweenIO } from "../anim";
import { Cursor } from "../components/Cursor";
import { Dashboard } from "../components/Dashboard";
import { Icon } from "../components/Icon";
import { BrandBackground, Screen } from "../components/Stage";
import { C, FONT } from "../theme";

// 0:10–0:15 — cursor click with easing; inactive UI dimmed ~25%; CONNECT → SYNC → ORGANIZE.
const TOOLS = [
  { name: "Cloud Drive", icon: "drive", color: "#F4B400" },
  { name: "Email", icon: "mail", color: "#EA4335" },
  { name: "Team Chat", icon: "chat", color: "#7C3AED" },
  { name: "Notes", icon: "file", color: C.text },
];

const MODAL = { x: 380, y: 200, w: 880, h: 540 };
const BTN = { x: MODAL.x + MODAL.w / 2 - 160, y: MODAL.y + 420, w: 320, h: 64 };
const CLICK = 60;

export const S4Connect: React.FC = () => {
  const f = useCurrentFrame();
  const modal = pop(f, 2, 16);
  const dim = tween(f, 0, 12, 0, 0.28);
  const push = tween(f, 0, 150, 0.86, 0.9);

  const target = { x: BTN.x + BTN.w * 0.6, y: BTN.y + BTN.h * 0.6 };
  const cm = tweenIO(f, 16, 54);
  const cur = { x: 1150 + (target.x - 1150) * cm, y: 820 + (target.y - 820) * cm };
  const p = press(f, CLICK);
  const done = f > 104;

  const steps = [
    { label: "CONNECT", icon: "link", at: CLICK },
    { label: "SYNC", icon: "cloud", at: CLICK + 22 },
    { label: "ORGANIZE", icon: "database", at: CLICK + 44 },
  ];

  return (
    <AbsoluteFill>
      <BrandBackground />
      <Screen cx={780} cy={520} scale={push}>
        <Dashboard>
          <div style={{ position: "absolute", inset: 0, background: `rgba(5,8,23,${dim})`, zIndex: 10 }} />
          <div
            style={{
              position: "absolute",
              left: MODAL.x,
              top: MODAL.y,
              width: MODAL.w,
              height: MODAL.h,
              background: "#fff",
              borderRadius: 24,
              boxShadow: "0 30px 80px rgba(5,8,23,0.35)",
              transform: `translateY(${(1 - modal) * 40}px) scale(${0.94 + 0.06 * modal})`,
              opacity: modal,
              zIndex: 20,
              fontFamily: FONT,
            }}
          >
            <div style={{ position: "absolute", left: 48, top: 44, fontSize: 36, fontWeight: 800, color: C.text }}>Connect Your Workspace</div>
            <div style={{ position: "absolute", left: 48, top: 96, fontSize: 20, color: C.textMuted }}>Bring your tools and data together in one place.</div>
            {TOOLS.map((t, i) => {
              const ok = tween(f, CLICK + 8 + i * 9, CLICK + 16 + i * 9);
              return (
                <div
                  key={t.name}
                  style={{
                    position: "absolute",
                    left: 48 + i * 200,
                    top: 160,
                    width: 180,
                    height: 190,
                    borderRadius: 18,
                    border: `2px solid ${ok > 0.5 ? C.green : C.border}`,
                    background: ok > 0.5 ? "#F0FDF4" : "#fff",
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    justifyContent: "center",
                    gap: 16,
                  }}
                >
                  <div style={{ width: 76, height: 76, borderRadius: 18, background: `${t.color}1A`, display: "flex", alignItems: "center", justifyContent: "center" }}>
                    <Icon name={t.icon} size={44} color={t.color} stroke={2.2} />
                  </div>
                  <div style={{ fontSize: 19, fontWeight: 600, color: C.text }}>{t.name}</div>
                  <div style={{ position: "absolute", right: -10, top: -10, width: 34, height: 34, borderRadius: 17, background: C.green, display: "flex", alignItems: "center", justifyContent: "center", transform: `scale(${ok})` }}>
                    <Icon name="check" size={20} stroke={3.2} color="#fff" />
                  </div>
                </div>
              );
            })}
            <div
              style={{
                position: "absolute",
                left: BTN.x - MODAL.x,
                top: BTN.y - MODAL.y,
                width: BTN.w,
                height: BTN.h,
                borderRadius: 14,
                background: done ? C.green : `linear-gradient(90deg, ${C.violet}, ${C.blue})`,
                color: "#fff",
                fontSize: 22,
                fontWeight: 700,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                gap: 10,
                transform: `scale(${1 - p * 0.05 + tween(f, 40, 54) * 0.03})`,
                boxShadow: "0 12px 30px rgba(109,74,255,0.35)",
              }}
            >
              {done ? (
                <>
                  <Icon name="check" size={24} stroke={3} color="#fff" /> Workspace Connected
                </>
              ) : (
                "Connect Accounts"
              )}
            </div>
          </div>
          <Cursor x={cur.x} y={cur.y} press={p} ripple={ripple(f, CLICK)} scale={1.25} />
        </Dashboard>
      </Screen>

      {/* Step pills */}
      <div style={{ position: "absolute", left: 1490, top: 250, width: 360, display: "flex", flexDirection: "column", alignItems: "center", gap: 14, fontFamily: FONT }}>
        {steps.map((s, i) => {
          const a = pop(f, s.at);
          const active = f >= s.at && (i === steps.length - 1 || f < steps[i + 1].at);
          return (
            <React.Fragment key={s.label}>
              {i > 0 && (
                <div style={{ opacity: a, color: "#7C8BD9" }}>
                  <Icon name="arrowDown" size={34} stroke={2.5} />
                </div>
              )}
              <div
                style={{
                  width: 340,
                  height: 96,
                  borderRadius: 20,
                  background: "rgba(10,16,48,0.9)",
                  border: `2px solid ${active ? "#60A5FA" : "rgba(96,165,250,0.35)"}`,
                  boxShadow: active ? "0 0 36px rgba(59,107,255,0.6)" : "none",
                  display: "flex",
                  alignItems: "center",
                  gap: 22,
                  paddingLeft: 32,
                  boxSizing: "border-box",
                  color: "#fff",
                  fontSize: 36,
                  fontWeight: 800,
                  letterSpacing: 1,
                  opacity: a,
                  transform: `translateX(${(1 - a) * 40}px)`,
                }}
              >
                <Icon name={s.icon} size={40} color={active ? C.cyan : "#93A3E8"} stroke={2.4} />
                {s.label}
              </div>
            </React.Fragment>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
