import { useState } from "react";
import type { Meta, StoryObj } from "@storybook/react-vite";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/tabs";
import { Slider, Switch } from "../components/controls";
import { Field } from "../components/field";
import { ColourChip, Confidence, Panel, Readout } from "../components/readout";
import { Button } from "../components/button";

const meta: Meta = { title: "System/Instrument panel" };
export default meta;

/**
 * Composition check: every primitive on one analysis-settings panel.
 * Values here are interactive controls only; no detection results are implied.
 */
export const Composition: StoryObj = {
  render: () => {
    const [conf, setConf] = useState(0.35);
    const [blur, setBlur] = useState(true);
    const [tiled, setTiled] = useState(false);
    const [n, setN] = useState(7);
    return (
      <div className="grid max-w-5xl grid-cols-1 gap-6 md:grid-cols-[1.4fr_1fr]">
        <Panel title="Readouts" meta="Click to step the counter">
          <div className="flex flex-wrap items-end gap-10">
            <Readout value={n} label="People in frame" size="xl" />
            <Readout value={n * 3 + 4} label="Unique tracks" unit="ids" />
          </div>
          <div className="mt-6 flex gap-2">
            <Button variant="secondary" size="sm" onClick={() => setN((v) => Math.max(0, v - 1))}>Decrease</Button>
            <Button variant="secondary" size="sm" onClick={() => setN((v) => v + 1)}>Increase</Button>
          </div>
        </Panel>
        <Panel title="Analysis settings">
          <div className="grid gap-5">
            <Slider label="Minimum confidence" value={conf} onValueChange={setConf} />
            <Switch label="Privacy mode" description="Blur faces and number plates before storage" checked={blur} onCheckedChange={setBlur} />
            <Switch label="Small-object mode" description="Tiled inference; slower, finds distant objects" checked={tiled} onCheckedChange={setTiled} />
          </div>
        </Panel>
        <Panel title="Tabs">
          <Tabs defaultValue="objects">
            <TabsList label="Result views">
              <TabsTrigger value="objects" count={12}>Objects</TabsTrigger>
              <TabsTrigger value="people" count={4}>People</TabsTrigger>
              <TabsTrigger value="events">Events</TabsTrigger>
            </TabsList>
            <TabsContent value="objects">
              <p className="text-sm text-muted">Objects view</p>
            </TabsContent>
            <TabsContent value="people">
              <p className="text-sm text-muted">People view</p>
            </TabsContent>
            <TabsContent value="events">
              <p className="text-sm text-muted">Events view</p>
            </TabsContent>
          </Tabs>
        </Panel>
        <Panel title="Labels">
          <div className="grid gap-3">
            <div className="flex gap-2"><Confidence score={0.91} /><Confidence score={0.38} /></div>
            <div className="flex flex-wrap gap-4">
              <ColourChip name="Navy" hex="#1f2a4a" share={0.62} />
              <ColourChip name="Off-white" hex="#e9e4d8" share={0.27} />
              <ColourChip name="Rust" hex="#a2472a" share={0.11} />
            </div>
            <Field label="Project name" placeholder="Loading dock, north gate" />
            <Field label="RTSP URL" defaultValue="rtsp://" error="Enter a full URL, for example rtsp://10.0.0.4:554/stream1" />
          </div>
        </Panel>
      </div>
    );
  },
};
