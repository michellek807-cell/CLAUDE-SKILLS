import React from "react";
import { AbsoluteFill, useCurrentFrame } from "remotion";
import { pop, tween } from "../anim";
import { Dashboard } from "../components/Dashboard";
import { Icon } from "../components/Icon";
import { NovaMark } from "../components/Logo";
import { BrandBackground, GradientText, Screen } from "../components/Stage";
import { FONT, GRADIENT } from "../theme";

// 0:24–0:27 — end card: product CTA + "From raw screen recording → to product story".
export const S7CTA: React.FC = () => {
  const f = useCurrentFrame();
  const logo = pop(f, 0);
  const tag = tween(f, 8, 22);
  const btn = pop(f, 16);
  const shot = tween(f, 4, 26);
  const fromT = tween(f, 18, 30);
  const toT = tween(f, 28, 42);
  const meta = tween(f, 38, 52);
  const pulse = 1 + 0.025 * Math.sin(f / 5) * tween(f, 30, 40);

  return (
    <AbsoluteFill style={{ fontFamily: FONT, color: "#fff" }}>
      <BrandBackground />

      {/* Left: product CTA */}
      <div style={{ position: "absolute", left: 130, top: 300, width: 800 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 28, transform: `scale(${0.9 + 0.1 * logo})`, transformOrigin: "left center", opacity: logo }}>
          <NovaMark size={130} />
          <div style={{ fontSize: 130, fontWeight: 800, letterSpacing: 2 }}>NOVA AI</div>
        </div>
        <div style={{ fontSize: 46, fontWeight: 500, color: "#D6DBF5", marginTop: 26, opacity: tag, transform: `translateY(${(1 - tag) * 16}px)` }}>
          A simpler way to run your business.
        </div>
        <div
          style={{
            marginTop: 54,
            width: 380,
            height: 92,
            borderRadius: 18,
            background: GRADIENT,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: 16,
            fontSize: 36,
            fontWeight: 700,
            opacity: btn,
            transform: `scale(${(0.9 + 0.1 * btn) * pulse})`,
            transformOrigin: "left center",
            boxShadow: "0 18px 50px rgba(109,74,255,0.5)",
          }}
        >
          Book a Demo <Icon name="arrowRight" size={34} stroke={3} color="#fff" />
        </div>
      </div>

      {/* Right: product shot + positioning */}
      <div style={{ opacity: shot, transform: `translateY(${(1 - shot) * 30}px)` }}>
        <Screen cx={1440} cy={300} scale={0.5} rotateY={-12} rotateX={3}>
          <Dashboard />
        </Screen>
      </div>
      <div style={{ position: "absolute", left: 1040, width: 800, top: 600, textAlign: "center" }}>
        <div style={{ fontSize: 36, fontWeight: 700, letterSpacing: 1, opacity: fromT }}>FROM RAW SCREEN RECORDING</div>
        <div style={{ display: "flex", justifyContent: "center", margin: "8px 0", opacity: toT, color: "#A78BFA" }}>
          <Icon name="arrowDown" size={44} stroke={3} />
        </div>
        <div style={{ fontSize: 66, fontWeight: 800, letterSpacing: 1, opacity: toT, transform: `scale(${0.92 + 0.08 * toT})` }}>
          <GradientText>TO PRODUCT STORY</GradientText>
        </div>
        <div style={{ fontSize: 24, color: "#C9D0F0", marginTop: 18, opacity: meta }}>SaaS Demo Editing &nbsp;|&nbsp; Motion Graphics &nbsp;|&nbsp; AI Voiceover</div>
        <div style={{ fontSize: 17, color: "#8E97BF", marginTop: 12, opacity: meta }}>Spec sample · Fictional product and interface shown for demonstration purposes only.</div>
      </div>
    </AbsoluteFill>
  );
};
