import { defineConfig } from "@playwright/test";

process.env.PLAYWRIGHT_GATEWAY_URL ??= "ws://127.0.0.1:9300";
process.env.OPERATOR_TOKEN ??= "secret";

const reuse = false;

export default defineConfig({
  testDir: "tests/e2e",
  timeout: 30_000,
  use: {
    baseURL: process.env.PLAYWRIGHT_BASE_URL ?? "http://127.0.0.1:4173"
  },
  webServer: [
    {
      command: "node scripts/mock-gateway.js",
      port: Number(process.env.GATEWAY_PORT ?? 9300),
      reuseExistingServer: reuse,
      env: {
        GATEWAY_PORT: process.env.GATEWAY_PORT ?? "9300",
        OPERATOR_TOKEN: process.env.OPERATOR_TOKEN
      }
    },
    {
      command: "npm run dev -- --host 127.0.0.1 --port 4173",
      port: 4173,
      reuseExistingServer: reuse,
      env: {
        VITE_GATEWAY_URL: process.env.PLAYWRIGHT_GATEWAY_URL
      }
    }
  ]
});
