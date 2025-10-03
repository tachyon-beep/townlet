import { tokens } from "../theme/tokens";

type KpiPanelProps = {
  kpis: Array<{ key: string; latest: number; trend: "up" | "down" | "flat" }>;
};

const trendColor: Record<"up" | "down" | "flat", string> = {
  up: tokens.color.accentDanger,
  down: tokens.color.accent,
  flat: tokens.color.textMuted
};

export function KpiPanel({ kpis }: KpiPanelProps) {
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
      <h2 style={{ marginTop: 0 }}>KPIs</h2>
      <ul style={{ listStyle: "none", padding: 0, margin: 0, fontSize: 13 }}>
        {kpis.map((kpi) => (
          <li key={kpi.key} style={{ marginBottom: tokens.spacing.xs }}>
            <strong>{kpi.key}</strong>: {kpi.latest.toFixed(2)} {" "}
            <span style={{ color: trendColor[kpi.trend] }}>
              {kpi.trend === "flat" ? "→" : kpi.trend === "up" ? "↑" : "↓"}
            </span>
          </li>
        ))}
        {kpis.length === 0 && <li style={{ color: tokens.color.textMuted }}>No KPI history.</li>}
      </ul>
    </section>
  );
}
