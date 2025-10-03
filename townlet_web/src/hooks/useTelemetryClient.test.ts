import { describe, expect, it } from "vitest";

import { applyTelemetryDiff } from "./useTelemetryClient";

describe("applyTelemetryDiff", () => {
  const baseline = {
    schema_version: "0.9.7",
    payload_type: "snapshot" as const,
    tick: 100,
    transport: { connected: true }
  };

  const diff = {
    schema_version: "0.9.7",
    payload_type: "diff" as const,
    tick: 101,
    changes: {
      transport: { connected: false },
      employment: { pending_count: 0 }
    },
    removed: ["narrations"]
  };

  it("returns snapshot when baseline missing", () => {
    const result = applyTelemetryDiff(baseline, { ...baseline, payload_type: "snapshot" });
    expect(result.payload_type).toBe("snapshot");
    expect(result.schema_version).toBe("0.9.7");
  });

  it("merges diff payloads", () => {
    const merged = applyTelemetryDiff(baseline, diff);
    expect(merged.payload_type).toBe("snapshot");
    expect(merged.tick).toBe(101);
    expect(merged.transport).toEqual({ connected: false });
    expect(merged.employment).toEqual({ pending_count: 0 });
  });
});
