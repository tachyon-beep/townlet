import { tokens } from "../theme/tokens";

type PerturbationBannerProps = {
  active: Array<{ id: string; data: Record<string, unknown> }>;
  pending: unknown[];
  cooldowns: Record<string, unknown>;
};

export function PerturbationBanner({ active, pending, cooldowns }: PerturbationBannerProps) {
  const hasActivity = active.length > 0 || pending.length > 0;
  const border = active.length > 0 ? tokens.color.accentDanger : tokens.color.accentWarning;
  return (
    <section
      aria-live="polite"
      style={{
        border: `1px solid ${hasActivity ? border : tokens.color.textMuted}`,
        padding: tokens.spacing.sm,
        borderRadius: 6,
        fontFamily: tokens.typography.fontFamily,
        backgroundColor: tokens.color.surface,
        color: tokens.color.textPrimary
      }}
    >
      <strong>Perturbations</strong>
      {hasActivity ? (
        <div style={{ marginTop: tokens.spacing.xs }}>
          {active.length > 0 && (
            <div>
              Active: {active.map((item) => item.id).join(", ") || "unknown"}
            </div>
          )}
          {pending.length > 0 && <div>Pending: {pending.length}</div>}
          {Object.keys(cooldowns).length > 0 && <div>Cooldowns in effect</div>}
        </div>
      ) : (
        <div style={{ color: tokens.color.textMuted }}>No active perturbations.</div>
      )}
    </section>
  );
}
