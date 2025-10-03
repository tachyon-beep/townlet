import { tokens } from "../theme/tokens";

type EmploymentSummaryProps = {
  pending: string[];
  pendingCount: number;
  exitsToday: number;
  queueLimit: number;
  reviewWindow: number;
};

export function EmploymentSummary({ pending, pendingCount, exitsToday, queueLimit, reviewWindow }: EmploymentSummaryProps) {
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
      <h2 style={{ marginTop: 0 }}>Employment Queue</h2>
      <p style={{ fontSize: 13 }}>
        Pending exits: <strong>{pendingCount}</strong> / Limit {queueLimit} • Exits today: {exitsToday}
      </p>
      <p style={{ fontSize: 13 }}>Review window: {reviewWindow} ticks</p>
      <p style={{ fontSize: 13 }}>Pending agents: {pending.length ? pending.join(", ") : "(none)"}</p>
    </section>
  );
}
