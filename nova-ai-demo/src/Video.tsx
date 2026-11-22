import React from "react";
import { AbsoluteFill, Audio, interpolate, Sequence, staticFile, useCurrentFrame } from "remotion";
import { MUSIC, SFX, VOICEOVER } from "./audio";
import { Captions } from "./components/Captions";
import { S1Raw } from "./scenes/S1Raw";
import { S2Transform } from "./scenes/S2Transform";
import { S3Reveal } from "./scenes/S3Reveal";
import { S4Connect } from "./scenes/S4Connect";
import { S5AI } from "./scenes/S5AI";
import { S6Benefit } from "./scenes/S6Benefit";
import { S7CTA } from "./scenes/S7CTA";
import { SCENES } from "./theme";

const XFADE = 8; // frames of cross-dissolve into each scene (except the hard freeze cut into scene 2)

const FadeIn: React.FC<{ frames: number; children: React.ReactNode }> = ({ frames, children }) => {
  const f = useCurrentFrame();
  const o = frames ? interpolate(f, [0, frames], [0, 1], { extrapolateRight: "clamp" }) : 1;
  return <AbsoluteFill style={{ opacity: o }}>{children}</AbsoluteFill>;
};

const SCENE_LIST: { key: keyof typeof SCENES; C: React.FC; xfade: number }[] = [
  { key: "raw", C: S1Raw, xfade: 0 },
  { key: "transform", C: S2Transform, xfade: 0 },
  { key: "reveal", C: S3Reveal, xfade: XFADE },
  { key: "connect", C: S4Connect, xfade: XFADE },
  { key: "ai", C: S5AI, xfade: XFADE },
  { key: "benefit", C: S6Benefit, xfade: XFADE },
  { key: "cta", C: S7CTA, xfade: XFADE },
];

export type NovaDemoProps = { showCaptions: boolean };

export const NovaDemo: React.FC<NovaDemoProps> = ({ showCaptions }) => (
  <AbsoluteFill style={{ background: "#050817" }}>
    {SCENE_LIST.map(({ key, C, xfade }) => {
      const s = SCENES[key];
      // Each scene starts `xfade` frames early and dissolves in over the previous one.
      return (
        <Sequence key={key} from={s.from - xfade} durationInFrames={s.duration + xfade} name={key}>
          <FadeIn frames={xfade}>
            <C />
          </FadeIn>
        </Sequence>
      );
    })}

    {showCaptions && <Captions />}

    {VOICEOVER && <Audio src={staticFile(VOICEOVER)} />}
    {MUSIC && (
      <Sequence from={SCENES.transform.from}>
        <Audio src={staticFile(MUSIC)} volume={(f) => interpolate(f, [0, 20, 600, 630, 690, 720], [0, 0.18, 0.18, 0.26, 0.26, 0], { extrapolateRight: "clamp" })} />
      </Sequence>
    )}
    {SFX.filter((s) => s.file).map((s) => (
      <Sequence key={s.frame} from={s.frame}>
        <Audio src={staticFile(s.file as string)} volume={s.volume} />
      </Sequence>
    ))}
  </AbsoluteFill>
);
