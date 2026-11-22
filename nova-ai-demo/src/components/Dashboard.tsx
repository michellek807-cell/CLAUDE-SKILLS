import React from "react";
import { C, FONT } from "../theme";
import { Icon } from "./Icon";
import { NovaWordmark } from "./Logo";

// The fictional Nova AI app, drawn at a fixed 1440x900 "screen" size.
// Scenes scale/position this screen and use RECTS to aim cursors, spotlights and callouts.
export const SCREEN_W = 1440;
export const SCREEN_H = 900;

export type Rect = { x: number; y: number; w: number; h: number };

const CONTENT_X = 272;
export const RECTS = {
  connectBtn: { x: 1118, y: 16, w: 222, h: 42 } as Rect,
  stats: { x: CONTENT_X, y: 168, w: 1136, h: 112 } as Rect,
  chart: { x: CONTENT_X, y: 304, w: 648, h: 564 } as Rect,
  recent: { x: 944, y: 304, w: 464, h: 564 } as Rect,
  recentItem0: { x: 960, y: 366, w: 432, h: 60 } as Rect,
  content: { x: 240, y: 72, w: 1200, h: 828 } as Rect,
};

const NAV = [
  { icon: "home", label: "Dashboard" },
  { icon: "folder", label: "Projects" },
  { icon: "users", label: "Customers" },
  { icon: "tasks", label: "Tasks" },
  { icon: "chart", label: "Analytics" },
  { icon: "settings", label: "Settings" },
];

const STATS = [
  { value: "12", label: "Active Projects", color: C.text },
  { value: "8", label: "Clients", color: C.text },
  { value: "24", label: "Tasks", color: C.text },
  { value: "2", label: "Overdue", color: C.red },
];

const ACTIVITY = [
  { label: "Client proposal updated", time: "2 hours ago", color: C.blue },
  { label: "New lead added", time: "3 hours ago", color: C.green },
  { label: "Task completed", time: "5 hours ago", color: C.green },
  { label: "Meeting scheduled", time: "1 day ago", color: C.violet },
  { label: "Invoice sent to Acme Co.", time: "2 days ago", color: C.blue },
  { label: "Weekly report generated", time: "3 days ago", color: C.violet },
  { label: "New client onboarded", time: "4 days ago", color: C.green },
];

const CHART_POINTS = [12, 30, 22, 46, 38, 62, 55, 78, 70, 92];
const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"];

const Card: React.FC<{ r: Rect; children?: React.ReactNode; style?: React.CSSProperties }> = ({ r, children, style }) => (
  <div
    style={{
      position: "absolute",
      left: r.x,
      top: r.y,
      width: r.w,
      height: r.h,
      background: C.panel,
      borderRadius: 16,
      border: `1px solid ${C.border}`,
      boxShadow: "0 1px 2px rgba(15,21,48,0.04)",
      ...style,
    }}
  >
    {children}
  </div>
);

const Chart: React.FC<{ progress: number }> = ({ progress }) => {
  const w = 584;
  const h = 380;
  const pts = CHART_POINTS.map((v, i) => [(i / (CHART_POINTS.length - 1)) * w, h - (v / 100) * h]);
  const d = pts.map((p, i) => `${i ? "L" : "M"}${p[0].toFixed(1)} ${p[1].toFixed(1)}`).join(" ");
  const area = `${d} L${w} ${h} L0 ${h} Z`;
  return (
    <svg width={w} height={h + 40} style={{ position: "absolute", left: 32, top: 110, overflow: "visible" }}>
      <defs>
        <linearGradient id="areaG" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={C.violet} stopOpacity={0.22} />
          <stop offset="100%" stopColor={C.violet} stopOpacity={0} />
        </linearGradient>
        <clipPath id="chartClip">
          <rect x={0} y={-20} width={w * progress} height={h + 40} />
        </clipPath>
      </defs>
      {[0, 0.25, 0.5, 0.75, 1].map((t) => (
        <line key={t} x1={0} x2={w} y1={h * t} y2={h * t} stroke={C.border} strokeWidth={1} />
      ))}
      <g clipPath="url(#chartClip)">
        <path d={area} fill="url(#areaG)" />
        <path d={d} fill="none" stroke={C.violet} strokeWidth={4} strokeLinejoin="round" strokeLinecap="round" />
        {pts.map((p, i) => (
          <circle key={i} cx={p[0]} cy={p[1]} r={5} fill="#fff" stroke={C.violet} strokeWidth={3} />
        ))}
      </g>
      {MONTHS.map((m, i) => (
        <text key={m} x={(i / (MONTHS.length - 1)) * w} y={h + 32} fill={C.textMuted} fontSize={15} fontFamily={FONT} textAnchor="middle">
          {m}
        </text>
      ))}
    </svg>
  );
};

export type DashboardProps = {
  chartProgress?: number;
  hoverConnect?: number; // 0..1 glow on the Connect Workspace button
  children?: React.ReactNode; // overlays drawn in screen coordinates (cursor, modals, spotlights)
};

export const Dashboard: React.FC<DashboardProps> = ({ chartProgress = 1, hoverConnect = 0, children }) => {
  const b = RECTS.connectBtn;
  return (
    <div
      style={{
        position: "relative",
        width: SCREEN_W,
        height: SCREEN_H,
        background: C.appBg,
        fontFamily: FONT,
        color: C.text,
        overflow: "hidden",
      }}
    >
      {/* Sidebar */}
      <div style={{ position: "absolute", left: 0, top: 0, width: 240, height: SCREEN_H, background: C.sidebar }}>
        <div style={{ position: "absolute", left: 28, top: 24 }}>
          <NovaWordmark size={20} />
        </div>
        {NAV.map((n, i) => (
          <div
            key={n.label}
            style={{
              position: "absolute",
              left: 16,
              top: 96 + i * 54,
              width: 208,
              height: 44,
              borderRadius: 10,
              display: "flex",
              alignItems: "center",
              gap: 14,
              paddingLeft: 16,
              boxSizing: "border-box",
              background: i === 0 ? C.sidebarActive : "transparent",
              color: i === 0 ? "#fff" : "#A9B1D6",
              fontSize: 17,
              fontWeight: i === 0 ? 600 : 500,
            }}
          >
            <Icon name={n.icon} size={20} />
            {n.label}
          </div>
        ))}
      </div>

      {/* Top bar */}
      <div style={{ position: "absolute", left: 240, top: 0, width: SCREEN_W - 240, height: 72, background: "#fff", borderBottom: `1px solid ${C.border}` }}>
        <div
          style={{
            position: "absolute",
            left: 32,
            top: 16,
            width: 380,
            height: 40,
            borderRadius: 10,
            background: C.appBg,
            display: "flex",
            alignItems: "center",
            gap: 10,
            paddingLeft: 14,
            color: C.textMuted,
            fontSize: 16,
          }}
        >
          <Icon name="search" size={18} />
          Search projects, clients, tasks…
        </div>
        <div style={{ position: "absolute", left: 800, top: 24, color: C.textMuted }}>
          <Icon name="bell" size={22} />
        </div>
      </div>
      {/* Connect Workspace button (screen coords) */}
      <div
        style={{
          position: "absolute",
          left: b.x,
          top: b.y,
          width: b.w,
          height: b.h,
          borderRadius: 10,
          background: `linear-gradient(90deg, ${C.violet}, ${C.blue})`,
          color: "#fff",
          fontSize: 16,
          fontWeight: 600,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          gap: 8,
          transform: `scale(${1 + hoverConnect * 0.04})`,
          boxShadow: `0 0 ${hoverConnect * 28}px rgba(109,74,255,${0.7 * hoverConnect})`,
        }}
      >
        <Icon name="link" size={18} />
        Connect Workspace
      </div>
      <div style={{ position: "absolute", left: 1360 + 18, top: 18, width: 38, height: 38, borderRadius: 19, background: "linear-gradient(135deg,#F59E0B,#EF4444)" }} />

      {/* Content */}
      <div style={{ position: "absolute", left: CONTENT_X, top: 98, fontSize: 30, fontWeight: 700 }}>Dashboard</div>
      <div style={{ position: "absolute", left: CONTENT_X + 170, top: 110, fontSize: 16, color: C.textMuted }}>Good morning, Sarah</div>

      {STATS.map((s, i) => {
        const w = (RECTS.stats.w - 3 * 20) / 4;
        return (
          <Card key={s.label} r={{ x: RECTS.stats.x + i * (w + 20), y: RECTS.stats.y, w, h: RECTS.stats.h }}>
            <div style={{ position: "absolute", left: 24, top: 18, fontSize: 38, fontWeight: 700, color: s.color }}>{s.value}</div>
            <div style={{ position: "absolute", left: 24, top: 70, fontSize: 16, color: C.textMuted }}>{s.label}</div>
          </Card>
        );
      })}

      <Card r={RECTS.chart}>
        <div style={{ position: "absolute", left: 32, top: 26, fontSize: 20, fontWeight: 700 }}>Project Activity</div>
        <div style={{ position: "absolute", left: 32, top: 58, fontSize: 15, color: C.textMuted }}>Completed tasks per month</div>
        <Chart progress={chartProgress} />
      </Card>

      <Card r={RECTS.recent}>
        <div style={{ position: "absolute", left: 24, top: 22, fontSize: 20, fontWeight: 700 }}>Recent Activity</div>
        <div style={{ position: "absolute", right: 24, top: 26, fontSize: 14, color: C.blue, fontWeight: 600 }}>View all</div>
        {ACTIVITY.map((a, i) => (
          <div
            key={a.label}
            style={{
              position: "absolute",
              left: 16,
              top: 62 + i * 70,
              width: RECTS.recent.w - 32,
              height: 60,
              display: "flex",
              alignItems: "center",
              gap: 14,
              paddingLeft: 10,
              boxSizing: "border-box",
              borderBottom: i < ACTIVITY.length - 1 ? `1px solid ${C.border}` : "none",
            }}
          >
            <div style={{ width: 30, height: 30, borderRadius: 15, background: a.color, display: "flex", alignItems: "center", justifyContent: "center", color: "#fff" }}>
              <Icon name="check" size={16} stroke={3} />
            </div>
            <div style={{ flex: 1, fontSize: 16, fontWeight: 500 }}>{a.label}</div>
            <div style={{ fontSize: 14, color: C.textMuted, paddingRight: 12 }}>{a.time}</div>
          </div>
        ))}
      </Card>

      {children}
    </div>
  );
};

// Dims everything except `r` inside the screen. amount 0..1.
export const Spotlight: React.FC<{ r: Rect; amount: number; radius?: number; glow?: number; pad?: number }> = ({ r, amount, radius = 16, glow = 0, pad = 8 }) => (
  <div
    style={{
      position: "absolute",
      left: r.x - pad,
      top: r.y - pad,
      width: r.w + pad * 2,
      height: r.h + pad * 2,
      borderRadius: radius,
      boxShadow: `0 0 0 4000px rgba(5,8,23,${amount}), 0 0 ${40 * glow}px ${6 * glow}px rgba(109,74,255,${0.55 * glow})`,
      border: glow > 0 ? `3px solid rgba(124,92,255,${glow})` : "none",
      zIndex: 20,
      pointerEvents: "none",
    }}
  />
);
