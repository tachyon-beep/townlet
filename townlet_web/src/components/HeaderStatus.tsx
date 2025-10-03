import { tokens } from "../theme/tokens";

interface HeaderStatusProps {
  schemaVersion: string | null;
  tick: number | null;
  transportConnected: boolean | null;
}

export function HeaderStatus({ schemaVersion, tick, transportConnected }: HeaderStatusProps) {
  return (
    <header
      style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        padding: `${tokens.spacing.sm}px ${tokens.spacing.lg}px`,
        backgroundColor: tokens.color.surface,
        color: tokens.color.textPrimary,
        fontFamily: tokens.typography.fontFamily,
        height: tokens.metrics.navHeight
      }}
    >
      <span>Schema {schemaVersion ?? "?"}</span>
      <span>Tick {tick ?? "–"}</span>
      <span
        style={{
          color: transportConnected ? tokens.color.accent : tokens.color.accentDanger
        }}
      >
        {transportConnected ? "Connected" : "Disconnected"}
      </span>
    </header>
  );
}
