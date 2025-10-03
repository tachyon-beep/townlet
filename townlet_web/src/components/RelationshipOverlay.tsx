import { tokens } from "../theme/tokens";

type RelationshipOverlayProps = {
  overlays: Array<{ owner: string; ties: unknown[] }>;
};

export function RelationshipOverlay({ overlays }: RelationshipOverlayProps) {
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
      <h2 style={{ marginTop: 0 }}>Relationship Overlay</h2>
      {overlays.length === 0 ? (
        <p style={{ color: tokens.color.textMuted, fontSize: 13 }}>No relationship overlays.</p>
      ) : (
        overlays.map(({ owner, ties }) => (
          <div key={owner} style={{ marginBottom: tokens.spacing.sm, fontSize: 13 }}>
            <strong>{owner}</strong>
            <ul>
              {ties.map((tie, index) => (
                <li key={index}>{JSON.stringify(tie)}</li>
              ))}
            </ul>
          </div>
        ))
      )}
    </section>
  );
}
