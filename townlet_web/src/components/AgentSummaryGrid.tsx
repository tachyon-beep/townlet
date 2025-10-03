import { tokens } from "../theme/tokens";

type AgentSummary = {
  agent_id: string;
  wallet?: number;
  attendance_ratio?: number;
  shift_state?: string;
};

interface AgentSummaryGridProps {
  agents: AgentSummary[];
}

export function AgentSummaryGrid({ agents }: AgentSummaryGridProps) {
  if (!agents.length) {
    return (
      <div style={{ color: tokens.color.textMuted, fontFamily: tokens.typography.fontFamily }}>
        No agents in snapshot yet.
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
      {agents.map((agent) => (
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
        </article>
      ))}
    </div>
  );
}
