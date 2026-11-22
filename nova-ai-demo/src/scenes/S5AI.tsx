import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { pop, press, tween } from "../anim";
import { Cursor } from "../components/Cursor";
import { Dashboard, Spotlight } from "../components/Dashboard";
import { Icon } from "../components/Icon";
import { NovaMark } from "../components/Logo";
import { BrandBackground, Callout, Screen } from "../components/Stage";
import { C, FONT } from "../theme";

// 0:15–0:20 — slow push into the AI result; thin animated data lines feed the AI panel.
const DRAWER = { x: 780, y: 92, w: 630, h: 790 };
const PROMPT = "Summarize priorities for today.";
const SEND = 46;
const ITEMS = [
  { text: "Follow up with 3 high-value leads", badge: "check", color: C.green },
  { text: "Review and approve project proposal", badge: "2", color: C.blue },
  { text: "Prepare for client meeting at 2 PM", badge: "3", color: C.violet },
];

export const S5AI: React.FC = () => {
  const f = useCurrentFrame();
  const slide = tween(f, 0, 18);
  const spot = tween(f, 4, 18, 0, 0.32);
  const push = tween(f, 0, 150, 0.9, 1.04);
  const chars = Math.round(tween(f, 12, 40, 0, PROMPT.length, (t) => t));
  const caret = Math.floor(f / 8) % 2 === 0 && f < SEND;
  const thinking = tween(f, SEND + 2, SEND + 8) * (1 - tween(f, 78, 84));
  const data = tween(f, SEND + 4, SEND + 34);
  const summary = tween(f, 80, 90);
  const insight = pop(f, 104);

  const dx = DRAWER.x + (1 - slide) * 680;

  // Data lines (screen coords) from the stats and chart into the AI panel.
  const lines = [
    "M 420 230 C 560 230, 640 330, 812 330",
    "M 600 560 C 680 560, 700 430, 812 400",
    "M 1000 230 C 960 260, 860 300, 812 340",
  ];

  return (
    <AbsoluteFill>
      <BrandBackground />
      <Screen cx={960 + (1090 - 720) * 0.9} cy={530} originX={1090} originY={460} scale={push}>
        <Dashboard>
          <Spotlight r={{ ...DRAWER, x: dx }} amount={spot} radius={22} pad={0} />
          {/* data lines */}
          <svg width={1440} height={900} style={{ position: "absolute", left: 0, top: 0, zIndex: 25, opacity: data > 0 ? 1 - tween(f, 84, 96) : 0 }}>
            <defs>
              <linearGradient id="dl" x1="0" y1="0" x2="1" y2="0">
                <stop offset="0%" stopColor={C.cyan} stopOpacity={0.2} />
                <stop offset="100%" stopColor={C.violet} />
              </linearGradient>
            </defs>
            {lines.map((d, i) => (
              <g key={i}>
                <path d={d} fill="none" stroke="url(#dl)" strokeWidth={3} pathLength={100} strokeDasharray={100} strokeDashoffset={100 * (1 - data)} strokeLinecap="round" />
                <circle r={6} fill={C.cyan} style={{ filter: `drop-shadow(0 0 8px ${C.cyan})`, offsetPath: `path("${d}")`, offsetDistance: `${data * 100}%` } as React.CSSProperties} />
              </g>
            ))}
          </svg>
          {/* AI drawer */}
          <div style={{ position: "absolute", left: dx, top: DRAWER.y, width: DRAWER.w, height: DRAWER.h, background: "#fff", borderRadius: 22, boxShadow: "0 30px 80px rgba(5,8,23,0.3)", zIndex: 30, fontFamily: FONT, color: C.text }}>
            <div style={{ position: "absolute", left: 36, top: 34, display: "flex", alignItems: "center", gap: 14, fontSize: 30, fontWeight: 800 }}>
              <NovaMark size={34} /> Ask Nova AI
            </div>
            <div style={{ position: "absolute", left: 36, top: 104, width: DRAWER.w - 72, height: 72, borderRadius: 16, border: `2px solid ${f > 10 && f < SEND + 4 ? C.violet : C.border}`, display: "flex", alignItems: "center", paddingLeft: 22, boxSizing: "border-box", fontSize: 22 }}>
              {PROMPT.slice(0, chars)}
              {caret && <span style={{ width: 2, height: 28, background: C.violet, marginLeft: 2 }} />}
              <div style={{ position: "absolute", right: 10, top: 10, width: 52, height: 52, borderRadius: 12, background: `linear-gradient(135deg, ${C.violet}, ${C.blue})`, display: "flex", alignItems: "center", justifyContent: "center", transform: `scale(${1 - press(f, SEND) * 0.1})` }}>
                <Icon name="send" size={26} color="#fff" stroke={2.6} />
              </div>
            </div>
            {/* thinking */}
            <div style={{ position: "absolute", left: 36, top: 214, opacity: thinking, display: "flex", alignItems: "center", gap: 14, fontSize: 20, color: C.textMuted }}>
              <Icon name="sparkle" size={24} color={C.violet} />
              Analyzing projects, clients and tasks
              {[0, 1, 2].map((i) => (
                <span key={i} style={{ width: 8, height: 8, borderRadius: 4, background: C.violet, opacity: 0.3 + 0.7 * Math.abs(Math.sin((f + i * 6) / 6)) }} />
              ))}
            </div>
            {/* summary */}
            <div style={{ position: "absolute", left: 24, top: 204, width: DRAWER.w - 48, height: 420, borderRadius: 18, background: "linear-gradient(180deg,#F6F4FF,#FFFFFF)", border: `1px solid #E6E0FF`, opacity: summary }}>
              <div style={{ position: "absolute", left: 28, top: 26, display: "flex", alignItems: "center", gap: 12, fontSize: 26, fontWeight: 800 }}>
                <Icon name="sparkle" size={28} color={C.violet} fill={C.violet} stroke={1} /> AI Summary
              </div>
              {ITEMS.map((it, i) => {
                const a = pop(f, 84 + i * 10);
                return (
                  <div key={it.text} style={{ position: "absolute", left: 28, top: 96 + i * 96, width: DRAWER.w - 104, height: 76, borderRadius: 14, background: "#fff", border: `1px solid ${C.border}`, display: "flex", alignItems: "center", gap: 18, paddingLeft: 18, boxSizing: "border-box", fontSize: 22, fontWeight: 600, opacity: a, transform: `translateY(${(1 - a) * 16}px)` }}>
                    <div style={{ width: 40, height: 40, borderRadius: 20, background: it.color, color: "#fff", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 20, fontWeight: 800 }}>
                      {it.badge === "check" ? <Icon name="check" size={22} stroke={3.2} color="#fff" /> : it.badge}
                    </div>
                    {it.text}
                  </div>
                );
              })}
            </div>
          </div>
          <Callout text="AI INSIGHT" x={560} y={420} progress={insight} size={38} icon={<Icon name="sparkle" size={34} color={C.cyan} />} />
          <svg width={1440} height={900} style={{ position: "absolute", left: 0, top: 0, zIndex: 39, opacity: insight }}>
            <path d="M 690 440 Q 760 470 820 500" fill="none" stroke={C.cyan} strokeWidth={4} strokeLinecap="round" pathLength={100} strokeDasharray={100} strokeDashoffset={100 * (1 - tween(f, 108, 122))} />
          </svg>
          {f < 60 && <Cursor x={dx + DRAWER.w - 58} y={DRAWER.y + 150} press={press(f, SEND)} scale={1.2} opacity={tween(f, 30, 36) * (1 - tween(f, 54, 60))} />}
        </Dashboard>
      </Screen>
    </AbsoluteFill>
  );
};
