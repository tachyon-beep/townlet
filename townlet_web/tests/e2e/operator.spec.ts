import { test, expect } from "@playwright/test";
import WebSocket from "ws";

const GATEWAY_URL = process.env.PLAYWRIGHT_GATEWAY_URL ?? "ws://127.0.0.1:9300";
const OPERATOR_TOKEN = process.env.OPERATOR_TOKEN ?? "secret";

test("operator websocket dispatches command", async () => {
  const ws = new WebSocket(`${GATEWAY_URL}/ws/operator?token=${OPERATOR_TOKEN}`);
  const ack = await new Promise<Record<string, unknown>>((resolve, reject) => {
    ws.on("message", (data) => {
      const message = JSON.parse(data.toString());
      if (message.type === "status") {
        ws.send(JSON.stringify({ type: "command", payload: { name: "relationship_summary" } }));
      } else if (message.type === "command_ack") {
        resolve(message);
        ws.close();
      }
    });
    ws.on("error", reject);
  });
  expect(ack).toMatchObject({ status: "ok" });
});
