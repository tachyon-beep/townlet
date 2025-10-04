import { tokens } from "../theme/tokens";
import type { PersonalitySnapshotEntry } from "../utils/telemetryTypes";

type AgentSummary = {
  agent_id: string;
  wallet?: number;
  attendance_ratio?: number;
  shift_state?: string;
};

const personalityColors: Record<string, string> = {
  socialite: "#d946ef",
  industrious: "#facc15",
  stoic: "#22d3ee",
  balanced: "#f5f5f5"
};

interface AgentSummaryGridProps {
  agents: AgentSummary[];
  personalities: Record<string, PersonalitySnapshotEntry>;
  personalityEnabled: boolean;
  filterActive: boolean;
}

function renderTraits(entry: PersonalitySnapshotEntry | undefined) {
  if (!entry) {
    return null;
  }
  const { extroversion, forgiveness, ambition } = entry.traits;
  const traitStyle = {
    margin: `${tokens.spacing.xs}px 0 0 0`,
    fontSize: 12,
    color: tokens.color.textMuted
  } as const;
  return (
    <p style={traitStyle} aria-hidden>
      {`Traits ext ${extroversion >= 0 ? "+" : ""}${extroversion.toFixed(2)} · forg ${
        forgiveness >= 0 ? "+" : ""
      }${forgiveness.toFixed(2)} · amb ${ambition >= 0 ? "+" : ""}${ambition.toFixed(2)}`}
    </p>
  );
}

function renderBadge(entry: PersonalitySnapshotEntry | undefined) {
  if (!entry) {
    return null;
  }
  const profileKey = entry.profile.toLowerCase();
  const color = personalityColors[profileKey] ?? tokens.color.accent;
  const badgeStyle = {
    display: "inline-flex",
    alignItems: "center",
    alignSelf: "flex-start",
    padding: `0 ${tokens.spacing.sm}px`,
    borderRadius: 999,
    fontSize: 12,
    fontWeight: 600,
    color: "#0f172a",
    backgroundColor: color,
    marginTop: tokens.spacing.sm
  } as const;
  const tooltip = `Profile ${entry.profile}; ext ${entry.traits.extroversion.toFixed(2)}, ` +
    `forg ${entry.traits.forgiveness.toFixed(2)}, amb ${entry.traits.ambition.toFixed(2)}`;
  return (
    <span style={badgeStyle} title={tooltip} aria-label={tooltip} data-testid="personality-badge">
      {entry.profile}
    </span>
  );
}

export function AgentSummaryGrid({
  agents,
  personalities,
  personalityEnabled,
  filterActive
}: AgentSummaryGridProps) {
  if (!agents.length) {
    const message = filterActive
      ? "No agents match the current personality filters."
      : "No agents in snapshot yet.";
    return (
      <div style={{ color: tokens.color.textMuted, fontFamily: tokens.typography.fontFamily }}>
        {message}
      </div>
    );
  }

  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fill, minmax(220px, 1fr))",
        gap: tokens.spacing.md
      }}
    >
      {agents.map((agent) => {
        const personalityEntry = personalityEnabled
          ? personalities[agent.agent_id]
          : undefined;

        return (
        <article
          key={agent.agent_id}
          style={{
            backgroundColor: tokens.color.surface,
            borderRadius: 8,
            padding: tokens.spacing.md,
            color: tokens.color.textPrimary,
            fontFamily: tokens.typography.fontFamily,
            minWidth: tokens.metrics.cardMinWidth
          }}
        >
          <h3 style={{ margin: 0, fontSize: 16 }}>{agent.agent_id}</h3>
          <dl style={{ margin: `${tokens.spacing.sm}px 0 0 0`, fontSize: 13 }}>
            <div>
              <dt style={{ display: "inline", color: tokens.color.textMuted }}>Wallet: </dt>
              <dd style={{ display: "inline", margin: 0 }}>{agent.wallet?.toFixed(2) ?? "–"}</dd>
            </div>
            <div>
              <dt style={{ display: "inline", color: tokens.color.textMuted }}>Attendance: </dt>
              <dd style={{ display: "inline", margin: 0 }}>
                {agent.attendance_ratio !== undefined
                  ? `${Math.round(agent.attendance_ratio * 100)}%`
                  : "–"}
              </dd>
            </div>
            <div>
              <dt style={{ display: "inline", color: tokens.color.textMuted }}>Shift: </dt>
              <dd style={{ display: "inline", margin: 0 }}>{agent.shift_state ?? "–"}</dd>
            </div>
          </dl>
          {personalityEnabled ? renderBadge(personalityEntry) : null}
          {personalityEnabled ? renderTraits(personalityEntry) : null}
        </article>
      );
      })}
    </div>
  );
}
