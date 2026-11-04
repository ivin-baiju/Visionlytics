import { useState } from "react";
import type { Meta, StoryObj } from "@storybook/react-vite";
import { Button, type ButtonStatus } from "../components/button";

const meta: Meta<typeof Button> = {
  title: "Controls/Button",
  component: Button,
  args: { children: "Analyse video" },
};
export default meta;
type S = StoryObj<typeof Button>;

export const Primary: S = {};
export const Secondary: S = { args: { variant: "secondary", children: "Add zone" } };
export const Ghost: S = { args: { variant: "ghost", children: "Cancel" } };
export const Danger: S = { args: { variant: "danger", children: "Delete analysis" } };
export const Disabled: S = { args: { disabled: true } };
export const Loading: S = { args: { status: "loading", loadingLabel: "Uploading" } };
export const LoadingWithProgress: S = { args: { status: "loading", progress: 0.42 } };
export const Success: S = { args: { status: "success", children: "Saved" } };
export const Error: S = { args: { status: "error", children: "Upload failed" } };

/** Full lifecycle: click to run idle → loading (determinate) → success, or alt-click for error. */
export const Lifecycle: S = {
  render: () => {
    const [status, setStatus] = useState<ButtonStatus>("idle");
    const [p, setP] = useState(0);
    const run = (fail: boolean) => {
      setStatus("loading");
      setP(0);
      let v = 0;
      const t = setInterval(() => {
        v += 0.1;
        setP(Math.min(v, 1));
        if (v >= 1) {
          clearInterval(t);
          setStatus(fail ? "error" : "success");
          setTimeout(() => setStatus("idle"), 1400);
        }
      }, 120);
    };
    return (
      <div className="flex gap-4">
        <Button size="lg" status={status} progress={p} onClick={(e) => run(e.altKey)}>
          {status === "success" ? "Uploaded" : status === "error" ? "Upload failed" : "Upload video"}
        </Button>
      </div>
    );
  },
};

export const Sizes: S = {
  render: () => (
    <div className="flex items-center gap-4">
      <Button size="sm">Small</Button>
      <Button size="md">Medium</Button>
      <Button size="lg">Large</Button>
    </div>
  ),
};
