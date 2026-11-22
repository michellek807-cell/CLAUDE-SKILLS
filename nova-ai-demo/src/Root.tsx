import React from "react";
import { Composition } from "remotion";
import { NovaDemo } from "./Video";
import { FPS, HEIGHT, TOTAL_FRAMES, WIDTH } from "./theme";

export const RemotionRoot: React.FC = () => (
  <>
    <Composition id="NovaDemo" component={NovaDemo} durationInFrames={TOTAL_FRAMES} fps={FPS} width={WIDTH} height={HEIGHT} defaultProps={{ showCaptions: true }} />
    <Composition id="NovaDemoClean" component={NovaDemo} durationInFrames={TOTAL_FRAMES} fps={FPS} width={WIDTH} height={HEIGHT} defaultProps={{ showCaptions: false }} />
  </>
);
