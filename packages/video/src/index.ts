export interface VideoSpec {
  id: string;
  fps: number;
  width: number;
  height: number;
  durationInFrames: number;
}

export const HERO_LOOP_SPEC: VideoSpec = {
  id: "hero-loop",
  fps: 60,
  width: 1920,
  height: 1080,
  durationInFrames: 480,
};

export const EXPLAINER_SPEC: VideoSpec = {
  id: "product-explainer",
  fps: 60,
  width: 1920,
  height: 1080,
  durationInFrames: 1500,
};

export interface FrameKeyframe {
  frame: number;
  peopleCount: number;
  activeTrackIds: number[];
  caption: string;
}

/**
 * Deterministic keyframe generator for Remotion / programmatic video rendering.
 */
export function buildHeroLoopTimeline(spec: VideoSpec = HERO_LOOP_SPEC): FrameKeyframe[] {
  const steps = 8;
  const stride = Math.floor(spec.durationInFrames / steps);
  return Array.from({ length: steps }, (_, i) => ({
    frame: i * stride,
    peopleCount: 4 + (i % 3),
    activeTrackIds: [1, 2, 4, 5],
    caption:
      i < 2
        ? "Frame ingest & Apache-2.0 RT-DETRv2 detection"
        : i < 5
          ? "ByteTrack + 26-d re-ID trajectory association"
          : "Foreground CIELAB + CIEDE2000 attire colour classification",
  }));
}
