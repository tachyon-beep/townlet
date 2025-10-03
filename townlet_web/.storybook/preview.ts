import type { Preview } from "@storybook/react";
import { tokens } from "../src/theme/tokens";

import "../src/index.css";

const preview: Preview = {
  parameters: {
    backgrounds: {
      default: "surface",
      values: [
        { name: "surface", value: tokens.color.background },
        { name: "light", value: "#ffffff" }
      ]
    }
  }
};

export default preview;
