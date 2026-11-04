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
