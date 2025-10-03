import type { Meta, StoryObj } from "@storybook/react";
import { App } from "./App";
import { tokens } from "./theme/tokens";
import { sampleSnapshot } from "./mocks/sampleSnapshot";

const meta: Meta<typeof App> = {
  title: "Spectator/App",
  component: App,
  parameters: {
    backgrounds: {
      default: "surface",
      values: [{ name: "surface", value: tokens.color.background }]
    }
  }
};

export default meta;

type Story = StoryObj<typeof App>;

export const Empty: Story = {
  render: () => <App />
};

export const WithSnapshot: Story = {
  render: () => <App initialSnapshot={sampleSnapshot} />
};
