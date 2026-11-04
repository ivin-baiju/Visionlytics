import type { Preview } from "@storybook/react-vite";
import "../src/styles/storybook.css";

const preview: Preview = {
  globalTypes: {
    theme: {
      description: "Theme",
      toolbar: { icon: "contrast", items: ["dark", "light"], dynamicTitle: true },
    },
  },
  initialGlobals: { theme: "dark" },
  decorators: [
    (Story, ctx) => {
      document.documentElement.dataset.theme = ctx.globals.theme as string;
      return (
        <div className="min-h-screen bg-bg p-8 text-fg">
          <Story />
        </div>
      );
    },
  ],
  parameters: { layout: "fullscreen", a11y: { test: "error" } },
};
export default preview;
