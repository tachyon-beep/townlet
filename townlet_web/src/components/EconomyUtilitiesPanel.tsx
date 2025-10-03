import { tokens } from "../theme/tokens";

type EconomyUtilitiesPanelProps = {
  settings: Record<string, number>;
  utilities: Record<string, boolean>;
};

export function EconomyUtilitiesPanel({ settings, utilities }: EconomyUtilitiesPanelProps) {
  const utilityEntries = Object.entries(utilities);
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
      <h2 style={{ marginTop: 0 }}>Economy & Utilities</h2>
      <div style={{ display: "flex", gap: tokens.spacing.lg, flexWrap: "wrap" }}>
        <div>
          <h3 style={{ marginBottom: tokens.spacing.xs }}>Settings</h3>
          <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
            {Object.entries(settings).map(([key, value]) => (
              <li key={key} style={{ fontSize: 13 }}>
                <strong>{key}:</strong> {value.toFixed(2)}
              </li>
            ))}
            {Object.keys(settings).length === 0 && (
              <li style={{ color: tokens.color.textMuted }}>No economy settings reported.</li>
            )}
          </ul>
        </div>
        <div>
          <h3 style={{ marginBottom: tokens.spacing.xs }}>Utilities</h3>
          <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
            {utilityEntries.map(([name, online]) => (
              <li key={name} style={{ fontSize: 13 }}>
                {name}: <span style={{ color: online ? tokens.color.accent : tokens.color.accentDanger }}>{online ? "ONLINE" : "OFFLINE"}</span>
              </li>
            ))}
            {utilityEntries.length === 0 && (
              <li style={{ color: tokens.color.textMuted }}>No utility telemetry.</li>
            )}
          </ul>
        </div>
      </div>
    </section>
  );
}
