import { tokens } from "../theme/tokens";

export function LegendPanel() {
  const items = [
    "Agent cards highlight active shifts and attendance ratios.",
    "Perturbation banner shows active/pending events.",
    "KPIs use arrows to denote trend direction.",
    "Command palette requires operator authentication.",
    "Narrations feed shows priority events with red markers."
  ];
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
      <h2 style={{ marginTop: 0 }}>Legend</h2>
      <ul style={{ fontSize: 13 }}>
        {items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </section>
  );
}
