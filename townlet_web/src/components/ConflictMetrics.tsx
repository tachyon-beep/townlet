import { tokens } from "../theme/tokens";

type ConflictMetricsProps = {
  cooldownEvents: number;
  ghostStepEvents: number;
  rotationEvents: number;
  rivalryEvents: Array<Record<string, unknown>>;
};

export function ConflictMetrics({ cooldownEvents, ghostStepEvents, rotationEvents, rivalryEvents }: ConflictMetricsProps) {
  const rivalryCount = rivalryEvents.length;
  return (
    <section
      style={{
        backgroundColor: tokens.color.surface,
        borderRadius: 8,
        padding: tokens.spacing.md,
        color: tokens.color.textPrimary,
        fontFamily: tokens.typography.fontFamily
      }}
    >
      <h2 style={{ marginTop: 0 }}>Conflict Metrics</h2>
      <ul style={{ listStyle: "none", padding: 0, fontSize: 13 }}>
        <li>Cooldown events: {cooldownEvents}</li>
        <li>Ghost step events: {ghostStepEvents}</li>
        <li>Rotation events: {rotationEvents}</li>
        <li>Recent rivalry events: {rivalryCount}</li>
      </ul>
    </section>
  );
}
