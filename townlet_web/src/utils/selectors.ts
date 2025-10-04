import type {
  PersonalitySnapshotEntry,
  TelemetrySnapshotPayload
} from "./telemetryTypes";

export function selectTransport(snapshot: TelemetrySnapshotPayload | null) {
  const transport = snapshot?.transport as Record<string, unknown> | undefined;
  return {
    connected: Boolean(transport?.connected),
    droppedMessages: typeof transport?.dropped_messages === "number" ? transport?.dropped_messages : null,
    queueLength: typeof transport?.queue_length === "number" ? transport?.queue_length : null,
    lastError: (transport?.last_error as string) ?? null
  };
}

export function selectPerturbations(snapshot: TelemetrySnapshotPayload | null) {
  const perturbations = snapshot?.perturbations as Record<string, unknown> | undefined;
  const active = perturbations?.active as Record<string, unknown> | undefined;
  const pending = perturbations?.pending as unknown[] | undefined;
  const cooldowns = perturbations?.cooldowns as Record<string, unknown> | undefined;
  return {
    active: active ? Object.entries(active).map(([id, data]) => ({ id, data })) : [],
    pending: pending ?? [],
    cooldowns: cooldowns ?? {}
  };
}

export function selectEconomy(snapshot: TelemetrySnapshotPayload | null) {
  const economySettings = snapshot?.economy_settings as Record<string, number> | undefined;
  const utilities = snapshot?.utilities as Record<string, boolean> | undefined;
  return {
    settings: economySettings ?? {},
    utilities: utilities ?? {}
  };
}

export function selectEmployment(snapshot: TelemetrySnapshotPayload | null) {
  const employment = snapshot?.employment as Record<string, unknown> | undefined;
  if (!employment) {
    return {
      pending: [],
      pendingCount: 0,
      exitsToday: 0,
      queueLimit: 0,
      reviewWindow: 0
    };
  }
  return {
    pending: (employment.pending as string[]) ?? [],
    pendingCount: (employment.pending_count as number) ?? 0,
    exitsToday: (employment.exits_today as number) ?? 0,
    queueLimit: (employment.queue_limit as number) ?? 0,
    reviewWindow: (employment.review_window as number) ?? 0
  };
}

export function selectConflict(snapshot: TelemetrySnapshotPayload | null) {
  const conflict = snapshot?.conflict as Record<string, unknown> | undefined;
  const queues = conflict?.queues as Record<string, number> | undefined;
  const rivalryEvents = conflict?.rivalry_events as Array<Record<string, unknown>> | undefined;
  return {
    cooldownEvents: queues?.cooldown_events ?? 0,
    ghostStepEvents: queues?.ghost_step_events ?? 0,
    rotationEvents: queues?.rotation_events ?? 0,
    rivalryEvents: rivalryEvents ?? []
  };
}

export function selectKpis(snapshot: TelemetrySnapshotPayload | null) {
  const kpis = snapshot?.kpis as Record<string, number[]> | undefined;
  if (!kpis) {
    return [] as { key: string; latest: number; trend: "up" | "down" | "flat" }[];
  }
  return Object.entries(kpis).map(([key, series]) => {
    const latest = series.at(-1) ?? 0;
    const previous = series.at(-2) ?? latest;
    const delta = latest - previous;
    let trend: "up" | "down" | "flat" = "flat";
    if (Math.abs(delta) > 0.05) {
      trend = delta > 0 ? "up" : "down";
    }
    return { key, latest, trend };
  });
}

export function selectRelationshipOverlays(snapshot: TelemetrySnapshotPayload | null) {
  const overlay = snapshot?.relationship_overlay as Record<string, unknown[]> | undefined;
  if (!overlay) return [] as { owner: string; ties: unknown[] }[];
  return Object.entries(overlay).map(([owner, ties]) => ({ owner, ties }));
}

export function selectRelationshipSummary(snapshot: TelemetrySnapshotPayload | null) {
  const summary = snapshot?.relationship_summary as Record<string, unknown> | undefined;
  return summary ?? {};
}

export function selectSocialEvents(snapshot: TelemetrySnapshotPayload | null) {
  const events = snapshot?.social_events as Array<Record<string, unknown>> | undefined;
  return events ?? [];
}

export function selectNarrations(snapshot: TelemetrySnapshotPayload | null) {
  const narrations = snapshot?.narrations as Array<Record<string, unknown>> | undefined;
  return narrations ?? [];
}

export function selectPersonalities(
  snapshot: TelemetrySnapshotPayload | null
): Record<string, PersonalitySnapshotEntry> {
  const personalities = snapshot?.personalities as
    | Record<string, PersonalitySnapshotEntry>
    | undefined;
  if (!personalities) {
    return {};
  }
  return personalities;
}
