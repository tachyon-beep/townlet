import { tokens } from "../theme/tokens";

type SocialPanelProps = {
  events: Array<Record<string, unknown>>;
};

export function SocialPanel({ events }: SocialPanelProps) {
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
      <h2 style={{ marginTop: 0 }}>Social Events</h2>
      <ul style={{ listStyle: "none", padding: 0, margin: 0, fontSize: 13 }}>
        {events.slice(0, 10).map((event, idx) => (
          <li key={idx}>
            {event.type}: {JSON.stringify(event.payload)}
          </li>
        ))}
        {events.length === 0 && <li style={{ color: tokens.color.textMuted }}>No events.</li>}
      </ul>
    </section>
  );
}
