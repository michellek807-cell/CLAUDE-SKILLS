import React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { C, FONT, GRADIENT } from "../theme";
import { SCREEN_H, SCREEN_W } from "./Dashboard";

// Deep navy studio background with slow-drifting brand glows.
export const BrandBackground: React.FC<{ opacity?: number }> = ({ opacity = 1 }) => {
  const f = useCurrentFrame();
  const dx = Math.sin(f / 60) * 60;
  const dy = Math.cos(f / 75) * 40;
  return (
    <AbsoluteFill style={{ opacity, background: `radial-gradient(ellipse at 50% 40%, ${C.bgNavy} 0%, ${C.bgDeep} 70%)` }}>
      <div style={{ position: "absolute", left: 150 + dx, top: 120 + dy, width: 900, height: 900, borderRadius: "50%", background: "rgba(109,74,255,0.22)", filter: "blur(160px)" }} />
      <div style={{ position: "absolute", right: 80 - dx, bottom: 40 - dy, width: 800, height: 800, borderRadius: "50%", background: "rgba(34,211,238,0.14)", filter: "blur(160px)" }} />
      {/* fine grid */}
      <AbsoluteFill
        style={{
          backgroundImage: "linear-gradient(rgba(255,255,255,0.035) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.035) 1px, transparent 1px)",
          backgroundSize: "64px 64px",
          maskImage: "radial-gradient(ellipse at center, black 30%, transparent 75%)",
          WebkitMaskImage: "radial-gradient(ellipse at center, black 30%, transparent 75%)",
        }}
      />
    </AbsoluteFill>
  );
};

// Places the 1440x900 app screen on the 1920x1080 canvas.
export const Screen: React.FC<{
  cx?: number;
  cy?: number;
  scale?: number;
  rotateY?: number;
  rotateX?: number;
  radius?: number;
  shadow?: number; // 0..1
  originX?: number; // transform origin inside the screen (px)
  originY?: number;
  children: React.ReactNode;
}> = ({ cx = 960, cy = 540, scale = 1, rotateY = 0, rotateX = 0, radius = 18, shadow = 1, originX = SCREEN_W / 2, originY = SCREEN_H / 2, children }) => (
  <div
    style={{
      position: "absolute",
      left: cx - originX,
      top: cy - originY,
      width: SCREEN_W,
      height: SCREEN_H,
      transformOrigin: `${originX}px ${originY}px`,
      transform: `perspective(2600px) rotateY(${rotateY}deg) rotateX(${rotateX}deg) scale(${scale})`,
      borderRadius: radius,
      overflow: "hidden",
      boxShadow: shadow ? `0 40px 120px rgba(0,0,0,${0.55 * shadow}), 0 0 0 1px rgba(255,255,255,${0.08 * shadow})` : "none",
    }}
  >
    {children}
  </div>
);

// Glowing brand label ("ONE WORKSPACE", "AI INSIGHT").
export const Callout: React.FC<{ text: string; x: number; y: number; progress: number; size?: number; icon?: React.ReactNode }> = ({ text, x, y, progress, size = 30, icon }) => (
  <div
    style={{
      position: "absolute",
      left: x,
      top: y,
      transform: `translate(-50%, -50%) scale(${0.85 + 0.15 * progress})`,
      opacity: progress,
      padding: `${size * 0.45}px ${size * 0.9}px`,
      borderRadius: 999,
      background: "rgba(10,16,48,0.92)",
      border: "2px solid rgba(96,165,250,0.9)",
      boxShadow: "0 0 30px rgba(59,107,255,0.55), inset 0 0 18px rgba(59,107,255,0.25)",
      color: "#fff",
      fontFamily: FONT,
      fontWeight: 800,
      fontSize: size,
      letterSpacing: 1,
      whiteSpace: "nowrap",
      display: "flex",
      alignItems: "center",
      gap: 12,
      zIndex: 40,
    }}
  >
    {icon}
    {text}
  </div>
);

export const GradientText: React.FC<{ children: React.ReactNode; style?: React.CSSProperties }> = ({ children, style }) => (
  <span style={{ background: GRADIENT, WebkitBackgroundClip: "text", backgroundClip: "text", color: "transparent", ...style }}>{children}</span>
);

// Fade helper for scene edges.
export const useFade = (duration: number, inF = 8, outF = 8) => {
  const f = useCurrentFrame();
  return interpolate(f, [0, inF, duration - outF, duration], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
};
