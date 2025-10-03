import { useEffect, useMemo, useRef, useState } from "react";
import type {
  TelemetrySnapshotPayload,
  TelemetryState,
  TelemetryStreamFactory
} from "../utils/telemetryTypes";

export function applyTelemetryDiff(
  baseline: TelemetrySnapshotPayload,
  incoming: TelemetrySnapshotPayload
): TelemetrySnapshotPayload {
  const baseCopy: TelemetrySnapshotPayload = JSON.parse(JSON.stringify(baseline));
  const payloadType = incoming.payload_type ?? "snapshot";

  if (payloadType === "snapshot") {
    return { ...incoming, payload_type: "snapshot" };
  }

  const merged: TelemetrySnapshotPayload = { ...baseCopy };
  if (typeof incoming.schema_version === "string") {
    merged.schema_version = incoming.schema_version;
  }
  if (incoming.tick !== undefined) {
    merged.tick = incoming.tick;
  }
  for (const [key, value] of Object.entries(incoming.changes ?? {})) {
    merged[key] = value as unknown;
  }
  for (const key of incoming.removed ?? []) {
    delete merged[key];
  }
  merged.payload_type = "snapshot";
  return merged;
}

const DEFAULT_STREAM_FACTORY: TelemetryStreamFactory = () =>
  new WebSocket("ws://localhost:8000/ws/telemetry");

export interface UseTelemetryOptions {
  streamFactory?: TelemetryStreamFactory;
  autoConnect?: boolean;
  initialSnapshot?: TelemetrySnapshotPayload | null;
}

export function useTelemetryClient(options: UseTelemetryOptions = {}): TelemetryState {
  const { streamFactory = DEFAULT_STREAM_FACTORY, autoConnect = true, initialSnapshot = null } = options;
  const [state, setState] = useState<TelemetryState>({
    snapshot: initialSnapshot,
    tick: typeof initialSnapshot?.tick === "number" ? initialSnapshot.tick : null,
    schemaVersion: initialSnapshot?.schema_version ?? null
  });
  const snapshotRef = useRef<TelemetrySnapshotPayload | null>(initialSnapshot);
  const socketRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (!autoConnect || typeof window === "undefined") {
      return;
    }
    const ws = streamFactory();
    socketRef.current = ws;

    ws.onmessage = (event) => {
      const payload: TelemetrySnapshotPayload = JSON.parse(event.data);
      const payloadType = payload.payload_type ?? "snapshot";
      const nextSnapshot = snapshotRef.current
        ? payloadType === "diff"
          ? applyTelemetryDiff(snapshotRef.current, payload)
          : { ...payload, payload_type: "snapshot" }
        : { ...payload, payload_type: "snapshot" };
      snapshotRef.current = nextSnapshot;
      setState({
        snapshot: nextSnapshot,
        tick: typeof nextSnapshot.tick === "number" ? nextSnapshot.tick : null,
        schemaVersion: nextSnapshot.schema_version ?? null
      });
    };

    ws.onerror = () => {
      setState((prev) => ({ ...prev }));
    };

    ws.onclose = () => {
      socketRef.current = null;
    };

    return () => {
      ws.close();
    };
  }, [autoConnect, streamFactory]);

  return state;
}

export function useTelemetrySnapshot(): TelemetrySnapshotPayload | null {
  const { snapshot } = useTelemetryClient({ autoConnect: false });
  return useMemo(() => snapshot, [snapshot]);
}
