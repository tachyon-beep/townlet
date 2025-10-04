import { tokens } from "../theme/tokens";

type NarrationEntry = {
  tick: number;
  category: string;
  message: string;
  priority?: boolean;
};

interface NarrationFeedProps {
  entries: NarrationEntry[];
  personalityToggleAvailable?: boolean;
  personalityNarrationEnabled?: boolean;
  onPersonalityNarrationChange?: (enabled: boolean) => void;
}

const CATEGORY_META: Record<string, { label: string; color: string }> = {
  queue_conflict: { label: "Queue Conflict", color: tokens.color.accentWarning },
  relationship_friendship: { label: "Friendship", color: "#38bdf8" },
  relationship_rivalry: { label: "Rivalry", color: tokens.color.accentDanger },
  relationship_social_alert: { label: "Social Alert", color: "#f97316" },
  personality_event: { label: "Personality", color: "#d946ef" }
};

export function NarrationFeed({
  entries,
  personalityToggleAvailable = false,
  personalityNarrationEnabled = true,
  onPersonalityNarrationChange
}: NarrationFeedProps) {
  const showToggle = personalityToggleAvailable && Boolean(onPersonalityNarrationChange);

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
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          gap: tokens.spacing.md
        }}
      >
        <h2 style={{ margin: 0, fontSize: 16 }}>Narrations</h2>
        {showToggle && (
          <label style={{ fontSize: 13, color: tokens.color.textPrimary }}>
            <input
              type="checkbox"
              checked={personalityNarrationEnabled}
              onChange={(event) => onPersonalityNarrationChange?.(event.target.checked)}
            />
            {' '}Show personality stories
          </label>
        )}
      </div>
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
            {(() => {
              const meta = CATEGORY_META[entry.category] ?? {
                label: entry.category.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase()),
                color: tokens.color.accent,
              };
              return (
                <span style={{ color: meta.color, fontWeight: 600, marginRight: tokens.spacing.xs }}>
                  {meta.label}
                </span>
              );
            })()}
            <span>{entry.message}</span>
          </div>
        ))}
      </div>
    </section>
  );
}
