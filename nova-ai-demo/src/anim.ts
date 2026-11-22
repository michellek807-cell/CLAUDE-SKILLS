import { interpolate, spring } from "remotion";
import { EASE, EASE_IN_OUT, FPS } from "./theme";

const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

/** Eased tween from `a` to `b` between frames f0..f1. */
export const tween = (f: number, f0: number, f1: number, a = 0, b = 1, easing = EASE) =>
  interpolate(f, [f0, f1], [a, b], { ...clamp, easing });

export const tweenIO = (f: number, f0: number, f1: number, a = 0, b = 1) => tween(f, f0, f1, a, b, EASE_IN_OUT);

/** Gentle spring starting at `delay`. */
export const pop = (f: number, delay = 0, damping = 14) =>
  spring({ frame: f - delay, fps: FPS, config: { damping, stiffness: 120, mass: 0.8 } });

/** Click press curve: 0 → 1 → 0 around frame `at`. */
export const press = (f: number, at: number) => interpolate(f, [at - 3, at, at + 5], [0, 1, 0], clamp);
export const ripple = (f: number, at: number) => interpolate(f, [at, at + 16], [0, 1], clamp);
