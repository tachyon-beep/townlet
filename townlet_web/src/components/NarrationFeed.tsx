import { tokens } from "../theme/tokens";

type NarrationEntry = {
  tick: number;
  category: string;
  message: string;
  priority?: boolean;
};

interface NarrationFeedProps {
  entries: NarrationEntry[];
}

export function NarrationFeed({ entries }: NarrationFeedProps) {
  return (
    <section
      style={{
        backgroundColor: tokens.color.surface,
        borderRadius: 8,
        padding: tokens.spacing.md,
        color: tokens.color.textPrimary,
        fontFamily: tokens.typography.fontFamily,
        display: "flex",
        flexDirection: "column",
        gap: tokens.spacing.xs,
        minHeight: 120
      }}
    >
      <h2 style={{ margin: 0, fontSize: 16 }}>Narrations</h2>
      <div
        role="log"
        aria-live="polite"
        style={{
          display: "flex",
          flexDirection: "column",
          gap: tokens.spacing.xs,
          maxHeight: 200,
          overflowY: "auto"
        }}
      >
        {entries.length === 0 && (
          <span style={{ color: tokens.color.textMuted }}>No recent narrations.</span>
        )}
        {entries.map((entry) => (
          <div key={`${entry.tick}-${entry.message}`} style={{ fontSize: 13 }}>
            <span style={{ color: tokens.color.textMuted }}>[{entry.tick}] </span>
            {entry.priority && <span style={{ color: tokens.color.accentDanger }}>! </span>}
            <span>{entry.message}</span>
          </div>
        ))}
      </div>
    </section>
  );
}
