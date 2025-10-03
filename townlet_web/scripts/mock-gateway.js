#!/usr/bin/env node
import http from "http";
import { WebSocketServer } from "ws";
import fs from "fs";
import path from "path";

const port = Number(process.env.GATEWAY_PORT ?? 9300);
const operatorToken = process.env.OPERATOR_TOKEN ?? "secret";

const __dirname = path.dirname(new URL(import.meta.url).pathname);
const snapshotPath = path.join(__dirname, "../tests/fixtures/snapshot.json");
const diffPath = path.join(__dirname, "../tests/fixtures/diff.json");
const snapshot = JSON.parse(fs.readFileSync(snapshotPath, "utf-8"));
const diff = JSON.parse(fs.readFileSync(diffPath, "utf-8"));

const server = http.createServer();

const telemetryWss = new WebSocketServer({ noServer: true });
const operatorWss = new WebSocketServer({ noServer: true });

telemetryWss.on("connection", (ws) => {
  ws.send(JSON.stringify(snapshot));
  const timeout = setTimeout(() => {
    ws.send(JSON.stringify(diff));
  }, 100);
  ws.on("close", () => clearTimeout(timeout));
});

operatorWss.on("connection", (ws, request) => {
  ws.send(
    JSON.stringify({
      type: "status",
      history: [],
      commands: ["relationship_summary"],
    })
  );
  ws.on("message", (data) => {
    try {
      const message = JSON.parse(data.toString());
      if (message.type === "command") {
        ws.send(
          JSON.stringify({
            type: "command_ack",
            status: "ok",
            result: { name: message.payload?.name ?? "unknown" }
          })
        );
        ws.send(
          JSON.stringify({
            type: "status",
            history: [
              { name: message.payload?.name ?? "unknown", status: "ok" }
            ],
            commands: ["relationship_summary"],
          })
        );
      }
    } catch (error) {
      ws.send(
        JSON.stringify({
          type: "command_ack",
          status: "error",
          error: String(error)
        })
      );
    }
  });
});

server.on("upgrade", (request, socket, head) => {
  const url = new URL(request.url ?? "", "http://localhost");
  if (url.pathname === "/ws/telemetry") {
    telemetryWss.handleUpgrade(request, socket, head, (ws) => {
      telemetryWss.emit("connection", ws, request);
    });
  } else if (url.pathname === "/ws/operator") {
    operatorWss.handleUpgrade(request, socket, head, (ws) => {
      operatorWss.emit("connection", ws, request);
    });
  } else {
    socket.destroy();
  }
});

server.listen(port, () => {
  console.log(`[mock-gateway] listening on ws://127.0.0.1:${port}`);
});

const close = () => {
  telemetryWss.close();
  operatorWss.close();
  server.close(() => process.exit(0));
};

process.on("SIGINT", close);
process.on("SIGTERM", close);
