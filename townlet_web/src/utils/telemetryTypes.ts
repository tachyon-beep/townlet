export interface PersonalitySnapshotEntry {
  profile: string;
  traits: {
    extroversion: number;
    forgiveness: number;
    ambition: number;
  };
  multipliers?: {
    needs?: Record<string, number>;
    rewards?: Record<string, number>;
    behaviour?: Record<string, number>;
  };
}

export interface TelemetrySnapshotPayload {
  schema_version: string;
  schema_warning: string | null;
  tick?: number | null;
  payload_type?: "snapshot" | "diff" | string;
  changes?: Record<string, unknown>;
  removed?: string[];
  personalities?: Record<string, PersonalitySnapshotEntry>;
  [key: string]: unknown;
}

export interface TelemetryState {
  snapshot: Record<string, unknown> | null;
  tick: number | null;
  schemaVersion: string | null;
}

export interface TelemetryMessageEvent {
  data: string;
}

export type TelemetryStreamFactory = () => WebSocket;
